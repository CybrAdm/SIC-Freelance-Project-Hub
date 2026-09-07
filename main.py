import json
import os
import re
from datetime import datetime
from functools import reduce



class InvalidInvoiceCodeError(Exception):
    """Raised when an invoice code does not match the required format."""
    pass


class InvoiceNotFoundError(Exception):
    """Raised when an operation references an invoice code that does not exist."""
    pass


class ProjectNotReadyForInvoiceError(Exception):
    """Raised when a project cannot be invoiced (no freelancer assigned, etc.)."""
    pass


class InvalidPaymentAmountError(Exception):
    """Raised when a payment amount is zero, negative, or not a number."""
    pass


class PaymentExceedsBalanceError(Exception):
    """Raised when a payment would pay more than the invoice's remaining balance."""
    pass


class PaymentNotFoundError(Exception):
    """Raised when a payment ID does not exist."""
    pass


class MilestoneNotFoundError(Exception):
    """Raised when a milestone ID does not exist."""
    pass


class UnauthorizedAccessError(Exception):
    """Raised when a user tries to view or modify data that does not belong to them."""
    pass


INVOICE_CODE_PATTERN = re.compile(r"^INV-\d{4}-\d{4,6}$")


def is_valid_invoice_code(invoice_code):
    """Regex validation for invoice codes. Returns True/False."""
    return bool(INVOICE_CODE_PATTERN.match(invoice_code))



def make_commission_calculator(initial_rate=0.10):
    rate = initial_rate

    def calculate(amount):
        return round(amount * rate, 2)

    def update_rate(new_rate):
        nonlocal rate

        if new_rate < 0 or new_rate > 1:
            raise ValueError("Commission rate must be between 0 and 1.")

        rate = new_rate

    def current_rate():
        return rate

    calculate.update_rate = update_rate
    calculate.current_rate = current_rate

    return calculate


class FreelanceManager:

    def __init__(self):
        self.users = []
        self.projects = []
        self.milestones = []
        self.invoices = []
        self.payments = []
        self.audit_logs = []

        self.commission_calculator = make_commission_calculator(0.10)

        self.create_data_files()
        self.load_data()

    # CREATE DATA FILES
    def create_data_files(self):

        if not os.path.exists("data"):
            os.makedirs("data")

        files = [
            "users.json",
            "projects.json",
            "milestones.json",
            "invoices.json",
            "payments.json",
            "audit_logs.json",
        ]

        for file_name in files:

            file_path = "data/" + file_name

            if not os.path.exists(file_path):

                with open(file_path, "w") as file:
                    json.dump([], file, indent=4)

        print("Data files created successfully.")

    # SETTERS
    def add_user(self, user):
        self.users.append(user)

    def add_project(self, project):
        self.projects.append(project)

    def add_milestone(self, milestone):
        self.milestones.append(milestone)

    def add_invoice(self, invoice):
        self.invoices.append(invoice)

    def add_payment(self, payment):
        self.payments.append(payment)

    def add_audit_log(self, user_id, action, description):

        log = {"user_id": user_id, "action": action, "description": description}

        self.audit_logs.append(log)

    # GETTERS
    def find_user(self, user_id):

        for user in self.users:

            if user.user_id == user_id:
                return user

        return None

    def find_project(self, project_id):

        for project in self.projects:

            if project.project_id == project_id:
                return project

        return None

    def find_milestone(self, milestone_id):

        for milestone in self.milestones:

            if milestone.milestone_id == milestone_id:
                return milestone

        return None

    def find_invoice(self, invoice_code):

        for invoice in self.invoices:

            if invoice.invoice_code == invoice_code:
                return invoice

        return None

    def find_payment(self, payment_id):

        for payment in self.payments:

            if payment.payment_id == payment_id:
                return payment

        return None


    def _is_admin(self, user_id):
        user = self.find_user(user_id)
        return user is not None and getattr(user, "role", None) == "Admin"

    def _check_invoice_ownership(self, invoice, requesting_user_id):
        """An invoice belongs to exactly one client and one freelancer."""

        if requesting_user_id is None or self._is_admin(requesting_user_id):
            return

        if requesting_user_id not in (invoice.client_id, invoice.freelancer_id):
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to access "
                f"invoice '{invoice.invoice_code}'."
            )

    def _check_payment_ownership(self, payment, requesting_user_id):
        """A payment belongs to the client who paid it and, through the
        invoice it settles, to the freelancer who is owed it."""

        if requesting_user_id is None or self._is_admin(requesting_user_id):
            return

        allowed_ids = {payment.client_id}

        invoice = self.find_invoice(payment.invoice_code)
        if invoice is not None:
            allowed_ids.add(invoice.freelancer_id)

        if requesting_user_id not in allowed_ids:
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to access "
                f"payment '{payment.payment_id}'."
            )

    def _check_milestone_ownership(self, milestone, requesting_user_id):
        """A milestone belongs to the client and freelancer of its project."""

        if requesting_user_id is None or self._is_admin(requesting_user_id):
            return

        project = self.find_project(milestone.project_id)

        allowed_ids = set()
        if project is not None:
            allowed_ids = {project.client_id, project.freelancer_id}

        if requesting_user_id not in allowed_ids:
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to access "
                f"milestone '{milestone.milestone_id}'."
            )

    def _check_project_ownership(self, project, requesting_user_id):
        """A project belongs to its client and its assigned freelancer."""

        if requesting_user_id is None or self._is_admin(requesting_user_id):
            return

        if requesting_user_id not in (project.client_id, project.freelancer_id):
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to access "
                f"project '{project.project_id}'."
            )

    def generate_invoice_code(self):
        """Auto-generate a new invoice code in the INV-YYYY-NNNN format
        and confirm it passes the regex validation rule."""

        year = datetime.now().year
        sequence = len(self.invoices) + 1
        invoice_code = f"INV-{year}-{sequence:04d}"

        if not is_valid_invoice_code(invoice_code):
            raise InvalidInvoiceCodeError(
                f"Generated invoice code '{invoice_code}' failed validation."
            )

        return invoice_code

    def generate_invoice(self, project_id, due_date, requesting_user_id=None):
        """Generate Invoice: builds an invoice from a project's budget,
        using the commission closure to work out the platform's cut.

        Only the client who owns the project or the freelancer assigned
        to it may generate an invoice for it."""

        project = self.find_project(project_id)

        if project is None:
            raise InvoiceNotFoundError(f"Project '{project_id}' does not exist.")

        self._check_project_ownership(project, requesting_user_id)

        if not project.freelancer_id:
            raise ProjectNotReadyForInvoiceError(
                "Cannot invoice a project with no freelancer assigned."
            )

        invoice_code = self.generate_invoice_code()
        commission = self.commission_calculator(project.budget)

        invoice = Invoice(
            invoice_code,
            project_id,
            project.client_id,
            project.freelancer_id,
            project.budget,
            commission,
            due_date,
        )

        self.add_invoice(invoice)
        self.add_audit_log(
            project.freelancer_id, "GENERATE_INVOICE", f"Invoice {invoice_code} created."
        )

        return invoice

    def view_invoice(self, invoice_code, requesting_user_id=None):
        """View Invoice: fetch a single invoice, raising a clear error
        if the code is unknown so the caller can react cleanly.

        If requesting_user_id is given, only the client or freelancer
        attached to the invoice (or an Admin) may view it."""

        invoice = self.find_invoice(invoice_code)

        if invoice is None:
            raise InvoiceNotFoundError(f"Invoice '{invoice_code}' was not found.")

        self._check_invoice_ownership(invoice, requesting_user_id)

        return invoice

    def update_invoice(self, invoice_code, amount=None, due_date=None, requesting_user_id=None):
        """Update Invoice: change amount and/or due date. Recomputes the
        commission and net amount whenever the amount changes.

        Only the freelancer who issued the invoice (or an Admin) may
        update it - clients are not allowed to edit invoice figures."""

        invoice = self.view_invoice(invoice_code, requesting_user_id=None)

        if requesting_user_id is not None and not self._is_admin(requesting_user_id):
            if requesting_user_id != invoice.freelancer_id:
                raise UnauthorizedAccessError(
                    f"User '{requesting_user_id}' is not authorized to update "
                    f"invoice '{invoice_code}'."
                )

        if amount is not None:
            invoice.amount = amount
            invoice.commission = self.commission_calculator(amount)
            invoice.net_amount = amount - invoice.commission

        if due_date is not None:
            invoice.due_date = due_date

        return invoice

    def get_invoice_status(self, invoice_code, requesting_user_id=None):
        """Invoice Status: reports Paid / Unpaid / Partially Paid based on
        payments actually recorded, not just the stored status flag."""

        invoice = self.view_invoice(invoice_code, requesting_user_id)
        balance = invoice.balance_due(self.payments)

        if balance <= 0:
            return "Paid"
        elif balance < invoice.amount:
            return "Partially Paid"
        else:
            return "Unpaid"


    def record_payment(self, invoice_code, amount, payment_method, requesting_user_id=None):
        """Record Payment: validates the invoice exists, the amount is
        sane, and the payment does not exceed the remaining balance.

        Only the client who owns the invoice (or an Admin) may pay it -
        a freelancer should never be able to "pay" their own invoice."""

        invoice = self.find_invoice(invoice_code)

        if invoice is None:
            raise InvoiceNotFoundError(f"Invoice '{invoice_code}' does not exist.")

        if requesting_user_id is not None and not self._is_admin(requesting_user_id):
            if requesting_user_id != invoice.client_id:
                raise UnauthorizedAccessError(
                    f"User '{requesting_user_id}' is not authorized to pay "
                    f"invoice '{invoice_code}'."
                )

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise InvalidPaymentAmountError("Payment amount must be a number.")

        if amount <= 0:
            raise InvalidPaymentAmountError("Payment amount must be greater than zero.")

        balance = invoice.balance_due(self.payments)

        if amount > balance:
            raise PaymentExceedsBalanceError(
                f"Payment of {amount} exceeds remaining balance of {balance}."
            )

        payment_id = f"PMT-{len(self.payments) + 1:04d}"
        payment = Payment(payment_id, invoice_code, invoice.client_id, amount, payment_method)
        self.add_payment(payment)

        # If the invoice is now fully paid, close it out and credit the
        # freelancer's running earnings total.
        new_balance = invoice.balance_due(self.payments)

        if new_balance <= 0:
            invoice.status = "Paid"

            freelancer = self.find_user(invoice.freelancer_id)

            if freelancer is not None and isinstance(freelancer, Freelancer):
                freelancer.earnings += invoice.net_amount
        else:
            invoice.status = "Partially Paid"

        self.add_audit_log(
            invoice.client_id, "RECORD_PAYMENT", f"Payment {payment_id} for {invoice_code}."
        )

        return payment

    def view_payment(self, payment_id, requesting_user_id=None):
        """View Payment: fetch a single payment record.

        Only the client who made the payment or the freelancer who is
        owed it (via the related invoice), or an Admin, may view it."""

        payment = self.find_payment(payment_id)

        if payment is None:
            raise PaymentNotFoundError(f"Payment '{payment_id}' was not found.")

        self._check_payment_ownership(payment, requesting_user_id)

        return payment

    def get_payment_history(self, invoice_code=None, client_id=None, requesting_user_id=None):
        """Payment History: filter payments by invoice or client. Uses
        `filter` with a lambda so the predicate stays a one-liner.

        When requesting_user_id is given (and is not an Admin), results
        are always narrowed down to payments that user is allowed to
        see, regardless of the invoice_code/client_id filters passed in."""

        history = self.payments

        if invoice_code is not None:
            history = list(filter(lambda payment: payment.invoice_code == invoice_code, history))

        if client_id is not None:
            history = list(filter(lambda payment: payment.client_id == client_id, history))

        if requesting_user_id is not None and not self._is_admin(requesting_user_id):

            def is_visible(payment):
                if payment.client_id == requesting_user_id:
                    return True
                invoice = self.find_invoice(payment.invoice_code)
                return invoice is not None and invoice.freelancer_id == requesting_user_id

            history = list(filter(is_visible, history))

        return history

    def get_payment_status(self, payment_id, requesting_user_id=None):
        """Payment Status: simple lookup wrapper around view_payment."""

        return self.view_payment(payment_id, requesting_user_id).status

    def update_commission_rate(self, new_rate, requesting_user_id=None):
        """Change the platform commission rate. Because the calculator is
        a closure built with `nonlocal`, every future invoice will use
        the new rate without needing to rebuild the closure.

        This is a platform-wide setting, so only an Admin may change it."""

        if requesting_user_id is not None and not self._is_admin(requesting_user_id):
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to change the "
                "commission rate."
            )

        self.commission_calculator.update_rate(new_rate)

    def get_commission_rate(self):
        return self.commission_calculator.current_rate()


    def calculate_freelancer_earnings(self, freelancer_id, requesting_user_id=None):
        """Total earnings for a freelancer, computed with reduce() over
        their paid invoices rather than trusting a stored running total.

        Only the freelancer themself (or an Admin) may request this."""

        if (
            requesting_user_id is not None
            and not self._is_admin(requesting_user_id)
            and requesting_user_id != freelancer_id
        ):
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to view "
                f"earnings for freelancer '{freelancer_id}'."
            )

        paid_invoices = [
            invoice
            for invoice in self.invoices
            if invoice.freelancer_id == freelancer_id and invoice.status == "Paid"
        ]

        total_earnings = reduce(
            lambda total, invoice: total + invoice.net_amount, paid_invoices, 0
        )

        return round(total_earnings, 2)

 
    def payment_report(self, requesting_user_id=None):
        """Payment Report: totals payments by status. Aggregate reports
        touch everyone's data, so this is Admin-only."""

        if requesting_user_id is not None and not self._is_admin(requesting_user_id):
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to view the "
                "payment report."
            )

        paid = list(filter(lambda payment: payment.status == "Completed", self.payments))
        pending = list(filter(lambda payment: payment.status == "Pending", self.payments))
        failed = list(filter(lambda payment: payment.status == "Failed", self.payments))

        total_amount = reduce(lambda total, payment: total + payment.amount, self.payments, 0)

        return {
            "total_payments": len(self.payments),
            "paid": len(paid),
            "pending": len(pending),
            "failed": len(failed),
            "total_amount": round(total_amount, 2),
        }

    def freelancer_earnings_report(self, requesting_user_id=None):
        """Freelancer Earnings report: one row per freelancer, built with
        map() over the manager's list of freelancers. Admin-only, since
        it exposes every freelancer's earnings side by side."""

        if requesting_user_id is not None and not self._is_admin(requesting_user_id):
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to view the "
                "freelancer earnings report."
            )

        freelancers = filter(lambda user: isinstance(user, Freelancer), self.users)

        def build_row(freelancer):
            completed_projects = list(
                filter(
                    lambda project: project.freelancer_id == freelancer.user_id
                    and project.status == "Completed",
                    self.projects,
                )
            )

            return {
                "freelancer": freelancer.name,
                "completed_projects": len(completed_projects),
                "total_earnings": self.calculate_freelancer_earnings(freelancer.user_id),
            }

        return list(map(build_row, freelancers))

    def project_report(self, requesting_user_id=None):
        """Project Report: counts active, late, and completed projects.
        Admin-only, since it summarizes every project on the platform."""

        if requesting_user_id is not None and not self._is_admin(requesting_user_id):
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to view the "
                "project report."
            )

        today = datetime.now().strftime("%Y-%m-%d")

        active = list(filter(lambda project: project.status == "In Progress", self.projects))
        completed = list(filter(lambda project: project.status == "Completed", self.projects))
        late = list(
            filter(
                lambda project: project.status != "Completed" and project.deadline < today,
                self.projects,
            )
        )

        return {
            "active_projects": len(active),
            "late_projects": len(late),
            "completed_projects": len(completed),
        }

    def dashboard_report(self, requesting_user_id=None):
        """Dashboard: a single summary view aggregating all the reports.
        Admin-only, for the same reason as the other reports."""

        if requesting_user_id is not None and not self._is_admin(requesting_user_id):
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to view the "
                "dashboard."
            )

        clients = list(filter(lambda user: isinstance(user, Client), self.users))
        freelancers = list(filter(lambda user: isinstance(user, Freelancer), self.users))
        pay_report = self.payment_report()
        proj_report = self.project_report()

        total_commission = reduce(
            lambda total, invoice: total + invoice.commission, self.invoices, 0
        )

        return {
            "total_clients": len(clients),
            "total_freelancers": len(freelancers),
            "total_projects": len(self.projects),
            "active_projects": proj_report["active_projects"],
            "late_projects": proj_report["late_projects"],
            "total_invoices": len(self.invoices),
            "total_payments": pay_report["total_payments"],
            "total_commission": round(total_commission, 2),
        }

    # LINK PROJECT MILESTONES
    def get_project_milestones(self, project_id, requesting_user_id=None):
        """Only the client or freelancer of the project (or an Admin)
        may list its milestones."""

        project = self.find_project(project_id)

        if project is not None:
            self._check_project_ownership(project, requesting_user_id)

        project_milestones = []

        for milestone in self.milestones:
            if milestone.project_id == project_id:
                project_milestones.append(milestone)

        return project_milestones

    def view_milestone(self, milestone_id, requesting_user_id=None):
        """View Milestone: fetch a single milestone, restricted to the
        client/freelancer of its project (or an Admin)."""

        milestone = self.find_milestone(milestone_id)

        if milestone is None:
            raise MilestoneNotFoundError(f"Milestone '{milestone_id}' was not found.")

        self._check_milestone_ownership(milestone, requesting_user_id)

        return milestone

    def sync_project_milestones(self, project_id):
        project = self.find_project(project_id)

        if project is None:
            return None

        project.milestones = []

        for milestone in self.milestones:
            if milestone.project_id == project_id:
                project.milestones.append(milestone.milestone_id)

        return project.milestones

    # SAVE DATA
    def save_data(self):

        users_data = []

        for user in self.users:
            users_data.append(user.to_dict())

        with open("data/users.json", "w") as file:
            json.dump(users_data, file, indent=4)

        projects_data = []

        for project in self.projects:
            self.sync_project_milestones(project.project_id)
            projects_data.append(project.to_dict())

        with open("data/projects.json", "w") as file:
            json.dump(projects_data, file, indent=4)

        invoices_data = []

        for invoice in self.invoices:
            invoices_data.append(invoice.to_dict())

        with open("data/invoices.json", "w") as file:
            json.dump(invoices_data, file, indent=4)

        payments_data = []

        for payment in self.payments:
            payments_data.append(payment.to_dict())

        with open("data/payments.json", "w") as file:
            json.dump(payments_data, file, indent=4)

        milestones_data = []

        for milestone in self.milestones:
            milestones_data.append(milestone.to_dict())

        with open("data/milestones.json", "w") as file:
            json.dump(milestones_data, file, indent=4)

        with open("data/audit_logs.json", "w") as file:
            json.dump(self.audit_logs, file, indent=4)

        print("Data saved successfully.")

    # LOAD DATA
    def load_data(self):

        try:

            # LOAD USERS
            with open("data/users.json", "r") as file:
                users_data = json.load(file)

            self.users = []

            for user_data in users_data:

                if user_data["role"] == "Client":

                    user = Client(
                        user_data["user_id"],
                        user_data["name"],
                        user_data["email"],
                        user_data["phone"],
                        user_data["password"],
                        user_data["company_name"],
                    )

                    user.active = user_data["active"]
                    user.project_ids = user_data["project_ids"]

                elif user_data["role"] == "Freelancer":

                    user = Freelancer(
                        user_data["user_id"],
                        user_data["name"],
                        user_data["email"],
                        user_data["phone"],
                        user_data["password"],
                        user_data["skills"],
                        user_data["hourly_rate"],
                    )

                    user.active = user_data["active"]
                    user.project_ids = user_data["project_ids"]
                    user.earnings = user_data["earnings"]

                else:

                    user = User(
                        user_data["user_id"],
                        user_data["name"],
                        user_data["email"],
                        user_data["phone"],
                        user_data["password"],
                        user_data["role"],
                    )

                    user.active = user_data["active"]

                self.users.append(user)

            # LOAD PROJECTS
            with open("data/projects.json", "r") as file:
                projects_data = json.load(file)

            self.projects = []

            for project_data in projects_data:

                project = Project(
                    project_data["project_id"],
                    project_data["title"],
                    project_data["description"],
                    project_data["client_id"],
                    project_data["freelancer_id"],
                    project_data["budget"],
                    project_data["deadline"],
                    project_data["status"],
                )

                project.milestones = project_data.get("milestones", [])

                self.projects.append(project)

            # LOAD INVOICES
            with open("data/invoices.json", "r") as file:
                invoices_data = json.load(file)

            self.invoices = []

            for invoice_data in invoices_data:

                invoice = Invoice(
                    invoice_data["invoice_code"],
                    invoice_data["project_id"],
                    invoice_data["client_id"],
                    invoice_data["freelancer_id"],
                    invoice_data["amount"],
                    invoice_data["commission"],
                    invoice_data["due_date"],
                    invoice_data["status"],
                )

                self.invoices.append(invoice)

            # LOAD PAYMENTS
            with open("data/payments.json", "r") as file:
                payments_data = json.load(file)

            self.payments = []

            for payment_data in payments_data:

                payment = Payment(
                    payment_data["payment_id"],
                    payment_data["invoice_code"],
                    payment_data["client_id"],
                    payment_data["amount"],
                    payment_data["payment_method"],
                    payment_data["status"],
                )

                self.payments.append(payment)

            # LOAD MILESTONES
            with open("data/milestones.json", "r") as file:
                milestones_data = json.load(file)

            self.milestones = []

            for milestone_data in milestones_data:

                milestone = Milestone(
                    milestone_data["milestone_id"],
                    milestone_data["project_id"],
                    milestone_data["title"],
                    milestone_data["description"],
                    milestone_data["amount"],
                    milestone_data["deadline"],
                    milestone_data["status"],
                )

                milestone.history = milestone_data.get("history", [])

                self.milestones.append(milestone)

            # LOAD AUDIT LOGS
            with open("data/audit_logs.json", "r") as file:
                self.audit_logs = json.load(file)

            print("Data loaded successfully.")

        except json.JSONDecodeError:

            print("Invalid JSON data.")

        except FileNotFoundError:

            print("Data files are not found.")


class User:

    def __init__(self, user_id, name, email, phone, password, role):

        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password
        self.role = role
        self.active = True

    def profile_summary(self):

        return f"""
                User ID: {self.user_id}
                Name: {self.name}
                Email: {self.email}
                Phone: {self.phone}
                Role: {self.role}
                Status: {"Active" if self.active else "Inactive"}
                """

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "password": self.password,
            "role": self.role,
            "active": self.active,
        }


class Client(User):

    def __init__(self, user_id, name, email, phone, password, company_name):
        super().__init__(user_id, name, email, phone, password, "Client")

        self.company_name = company_name
        self.project_ids = []

    def profile_summary(self):

        return f"""
                Client Profile
                --------------
                ID: {self.user_id}
                Name: {self.name}
                Email: {self.email}
                Phone: {self.phone}
                Company: {self.company_name}
                Projects: {len(self.project_ids)}
                Status: {"Active" if self.active else "Inactive"}
                """

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "password": self.password,
            "role": self.role,
            "active": self.active,
            "company_name": self.company_name,
            "project_ids": self.project_ids,
        }


class Freelancer(User):

    def __init__(self, user_id, name, email, phone, password, skills, hourly_rate):
        super().__init__(user_id, name, email, phone, password, "Freelancer")

        self.skills = skills
        self.hourly_rate = hourly_rate
        self.project_ids = []
        self.earnings = 0

    def profile_summary(self):

        skills = ", ".join(self.skills)

        return f"""
                Freelancer Profile
                ------------------
                ID: {self.user_id}
                Name: {self.name}
                Email: {self.email}
                Phone: {self.phone}
                Skills: {skills}
                Hourly Rate: {self.hourly_rate}
                Projects: {len(self.project_ids)}
                Earnings: {self.earnings}
                Status: {"Active" if self.active else "Inactive"}
                """

    def to_dict(self):

        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "password": self.password,
            "role": self.role,
            "active": self.active,
            "skills": self.skills,
            "hourly_rate": self.hourly_rate,
            "project_ids": self.project_ids,
            "earnings": self.earnings,
        }


class Project:

    def __init__(
        self,
        project_id,
        title,
        description,
        client_id,
        freelancer_id,
        budget,
        deadline,
        status="Pending",
    ):
        self.project_id = project_id
        self.title = title
        self.description = description
        self.client_id = client_id
        self.freelancer_id = freelancer_id
        self.budget = budget
        self.deadline = deadline
        self.status = status
        self.milestones = []

    def to_dict(self):

        return {
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "client_id": self.client_id,
            "freelancer_id": self.freelancer_id,
            "budget": self.budget,
            "deadline": self.deadline,
            "status": self.status,
            "milestones": self.milestones,
        }


class Milestone:

    def __init__(
        self,
        milestone_id,
        project_id,
        title,
        description,
        amount,
        deadline,
        status="Pending",
    ):
        self.milestone_id = milestone_id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.amount = amount
        self.deadline = deadline
        self.status = status
        self.history = []

    def update_status(self, new_status):
        old_status = self.status
        self.status = new_status
        self.history.append({"old_status": old_status, "new_status": new_status})

    def to_dict(self):
        return {
            "milestone_id": self.milestone_id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "amount": self.amount,
            "deadline": self.deadline,
            "status": self.status,
            "history": self.history,
        }


class Invoice:

    def __init__(
        self,
        invoice_code,
        project_id,
        client_id,
        freelancer_id,
        amount,
        commission,
        due_date,
        status="Unpaid",
    ):
        self.invoice_code = invoice_code
        self.project_id = project_id
        self.client_id = client_id
        self.freelancer_id = freelancer_id
        self.amount = amount
        self.commission = commission
        self.net_amount = amount - commission
        self.due_date = due_date
        self.status = status

    def amount_paid(self, payments):
        """Sum of completed payments recorded against this invoice."""
        return reduce(
            lambda total, payment: total + payment.amount
            if payment.invoice_code == self.invoice_code and payment.status != "Failed"
            else total,
            payments,
            0,
        )

    def balance_due(self, payments):
        return round(self.amount - self.amount_paid(payments), 2)

    def to_dict(self):
        return {
            "invoice_code": self.invoice_code,
            "project_id": self.project_id,
            "client_id": self.client_id,
            "freelancer_id": self.freelancer_id,
            "amount": self.amount,
            "commission": self.commission,
            "net_amount": self.net_amount,
            "due_date": self.due_date,
            "status": self.status,
        }


class Payment:

    def __init__(
        self,
        payment_id,
        invoice_code,
        client_id,
        amount,
        payment_method,
        status="Completed",
    ):

        self.payment_id = payment_id
        self.invoice_code = invoice_code
        self.client_id = client_id
        self.amount = amount
        self.payment_method = payment_method
        self.status = status

    def to_dict(self):
        return {
            "payment_id": self.payment_id,
            "invoice_code": self.invoice_code,
            "client_id": self.client_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "status": self.status,
        }



def finance_menu(manager, current_user_id=None):

    while True:

        print("\n----- Finance Menu (Invoices / Payments / Reports) -----")
        print("1. Generate Invoice")
        print("2. View Invoice")
        print("3. Update Invoice")
        print("4. Check Invoice Status")
        print("5. Record Payment")
        print("6. View Payment")
        print("7. Payment History")
        print("8. Payment Status")
        print("9. Update Commission Rate")
        print("10. Payment Report")
        print("11. Freelancer Earnings Report")
        print("12. Project Report")
        print("13. Dashboard")
        print("14. View Milestone")
        print("0. Back / Quit")

        choice = input("Choose an option: ").strip()

        try:

            if choice == "1":
                project_id = input("Project ID: ").strip()
                due_date = input("Due date (YYYY-MM-DD): ").strip()
                invoice = manager.generate_invoice(project_id, due_date, requesting_user_id=current_user_id)
                print(f"Invoice created: {invoice.invoice_code} | Net amount: {invoice.net_amount}")

            elif choice == "2":
                code = input("Invoice code: ").strip()
                invoice = manager.view_invoice(code, requesting_user_id=current_user_id)
                print(invoice.to_dict())

            elif choice == "3":
                code = input("Invoice code: ").strip()
                new_amount = input("New amount (blank to skip): ").strip()
                new_due_date = input("New due date (blank to skip): ").strip()
                invoice = manager.update_invoice(
                    code,
                    amount=float(new_amount) if new_amount else None,
                    due_date=new_due_date if new_due_date else None,
                    requesting_user_id=current_user_id,
                )
                print(f"Invoice updated: {invoice.to_dict()}")

            elif choice == "4":
                code = input("Invoice code: ").strip()
                print(f"Status: {manager.get_invoice_status(code, requesting_user_id=current_user_id)}")

            elif choice == "5":
                code = input("Invoice code: ").strip()
                amount = input("Payment amount: ").strip()
                method = input("Payment method: ").strip()
                payment = manager.record_payment(code, amount, method, requesting_user_id=current_user_id)
                print(f"Payment recorded: {payment.payment_id}")

            elif choice == "6":
                payment_id = input("Payment ID: ").strip()
                print(manager.view_payment(payment_id, requesting_user_id=current_user_id).to_dict())

            elif choice == "7":
                code = input("Filter by invoice code (blank for all): ").strip()
                history = manager.get_payment_history(
                    invoice_code=code if code else None,
                    requesting_user_id=current_user_id,
                )
                for payment in history:
                    print(payment.to_dict())

            elif choice == "8":
                payment_id = input("Payment ID: ").strip()
                print(f"Status: {manager.get_payment_status(payment_id, requesting_user_id=current_user_id)}")

            elif choice == "9":
                new_rate = float(input("New commission rate (0-1): ").strip())
                manager.update_commission_rate(new_rate, requesting_user_id=current_user_id)
                print(f"Commission rate updated to {manager.get_commission_rate()}")

            elif choice == "10":
                print(manager.payment_report(requesting_user_id=current_user_id))

            elif choice == "11":
                for row in manager.freelancer_earnings_report(requesting_user_id=current_user_id):
                    print(row)

            elif choice == "12":
                print(manager.project_report(requesting_user_id=current_user_id))

            elif choice == "13":
                print(manager.dashboard_report(requesting_user_id=current_user_id))

            elif choice == "14":
                milestone_id = input("Milestone ID: ").strip()
                print(manager.view_milestone(milestone_id, requesting_user_id=current_user_id).to_dict())

            elif choice == "0":
                break

            else:
                print("Invalid choice, please try again.")

        except (
            InvalidInvoiceCodeError,
            InvoiceNotFoundError,
            ProjectNotReadyForInvoiceError,
            InvalidPaymentAmountError,
            PaymentExceedsBalanceError,
            PaymentNotFoundError,
            MilestoneNotFoundError,
            UnauthorizedAccessError,
            ValueError,
        ) as error:
            print(f"Error: {error}")


manager = FreelanceManager()


if __name__ == "__main__":
    logged_in_user_id = None
    
    while True:
        user_input = input("Enter your User ID to login: ").strip()
        
        if not user_input:
            print("Error: User ID cannot be empty. Please try again.")
            continue
            
        user = manager.find_user(user_input)
        if user is None:
            print(f"Error: User ID '{user_input}' not found. Please enter a valid User ID.")
        else:
            logged_in_user_id = user.user_id
            print(f"Welcome, {user.name} ({user.role})!")
            break

    finance_menu(manager, current_user_id=logged_in_user_id)
