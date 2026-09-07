import datetime
import json
import os
from functools import reduce

from classes import (
    User,
    Client,
    Freelancer,
    Project,
    Milestone,
    Invoice,
    Payment,
    InvalidInvoiceCodeError,
    InvoiceNotFoundError,
    ProjectNotReadyForInvoiceError,
    InvalidPaymentAmountError,
    PaymentExceedsBalanceError,
    PaymentNotFoundError,
    MilestoneNotFoundError,
    UnauthorizedAccessError,
)
from validators import (
    is_cancel,
    print_menu,
    print_screen,
    return_to,
    is_valid_invoice_code,
    validate_user_id,
    validate_name,
    validate_age,
    validate_gender,
    validate_city,
    validate_email,
    validate_phone,
    validate_password,
    validate_company_name,
    validate_skills,
    validate_hourly_rate,
)

from menus import freelancer_matches_project

MAX_ACTIVE_PROJECTS = 3


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


def count_active_projects(freelancer_id, manager):
    active_statuses = ("Pending", "In Progress")
    count = 0

    for project in manager.projects:
        if project.freelancer_id == freelancer_id and project.status in active_statuses:
            count += 1

    return count


class Manager:

    def __init__(self):
        self.users = []
        self.projects = []
        self.milestones = []
        self.invoices = []
        self.payments = []
        self.audit_logs = []

        self.commission_calculator = make_commission_calculator(0.10)

        self.create_data_files()

    # CREATE DATA FILES
    def create_data_files(self):

        created = False

        if not os.path.exists("data"):
            os.makedirs("data")
            created = True

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

                created = True

        settings_path = "data/settings.json"

        if not os.path.exists(settings_path):

            with open(settings_path, "w") as file:
                json.dump({"commission_rate": 0.10}, file, indent=4)

            created = True

        if created:
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
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = {
            "user_id": user_id,
            "action": action,
            "description": description,
            "timestamp": time,
        }

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

    def find_email(self, email):

        for user in self.users:

            if user.email == email:
                return user

        return None

    def find_phone(self, phone):

        for user in self.users:

            if user.phone == phone:
                return user

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
        """Auto-generate a new invoice code in the I000 format
        and confirm it passes the regex validation rule."""

        sequence = 1
        existing_codes = {invoice.invoice_code for invoice in self.invoices}

        while True:
            invoice_code = f"I{sequence:03d}"
            if invoice_code not in existing_codes:
                break
            sequence += 1

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

        for existing_invoice in self.invoices:
            if existing_invoice.project_id == project_id:
                raise ValueError(
                    f"Project '{project_id}' already has invoice "
                    f"'{existing_invoice.invoice_code}'."
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
        actor_id = requesting_user_id or project.client_id
        self.add_audit_log(
            actor_id,
            "GENERATE_INVOICE",
            f"Invoice {invoice_code} created for project {project_id}.",
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

    def update_invoice(
        self, invoice_code, amount=None, due_date=None, requesting_user_id=None
    ):
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
            try:
                amount = round(float(amount), 2)
            except (TypeError, ValueError):
                raise InvalidPaymentAmountError("Invoice amount must be a number.")

            if amount <= 0:
                raise InvalidPaymentAmountError(
                    "Invoice amount must be greater than zero."
                )

            already_paid = round(invoice.amount_paid(self.payments), 2)

            if amount < already_paid:
                raise InvalidPaymentAmountError(
                    f"New amount cannot be less than already paid ({already_paid})."
                )

            invoice.amount = amount
            invoice.commission = self.commission_calculator(amount)
            invoice.net_amount = round(amount - invoice.commission, 2)

            paid = round(invoice.amount_paid(self.payments), 2)
            if paid <= 0:
                invoice.status = "Unpaid"
            elif paid < invoice.amount:
                invoice.status = "Partially Paid"
            else:
                invoice.status = "Paid"

            freelancer = self.find_user(invoice.freelancer_id)
            if freelancer is not None and freelancer.role == "Freelancer":
                freelancer.earnings = self.calculate_freelancer_earnings(
                    freelancer.user_id
                )

        if due_date is not None:
            invoice.due_date = due_date

        actor_id = requesting_user_id or invoice.freelancer_id
        self.add_audit_log(
            actor_id,
            "UPDATE_INVOICE",
            f"Invoice {invoice_code} updated.",
        )

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

    def record_payment(
        self, invoice_code, amount, payment_method, requesting_user_id=None
    ):
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
            amount = round(float(amount), 2)
        except (TypeError, ValueError):
            raise InvalidPaymentAmountError("Payment amount must be a number.")

        if amount <= 0:
            raise InvalidPaymentAmountError("Payment amount must be greater than zero.")

        balance = invoice.balance_due(self.payments)

        if amount > balance:
            raise PaymentExceedsBalanceError(
                f"Payment of {amount} exceeds remaining balance of {balance}."
            )

        existing_ids = {payment.payment_id for payment in self.payments}
        sequence = 1

        while True:
            payment_id = f"PAY{sequence:03d}"
            if payment_id not in existing_ids:
                break
            sequence += 1

        payment = Payment(
            payment_id, invoice_code, invoice.client_id, amount, payment_method
        )
        self.add_payment(payment)

        paid = round(invoice.amount_paid(self.payments), 2)
        if paid <= 0:
            invoice.status = "Unpaid"
        elif paid < invoice.amount:
            invoice.status = "Partially Paid"
        else:
            invoice.status = "Paid"

        freelancer = self.find_user(invoice.freelancer_id)
        if freelancer is not None and freelancer.role == "Freelancer":
            freelancer.earnings = self.calculate_freelancer_earnings(freelancer.user_id)

        actor_id = requesting_user_id or invoice.client_id
        self.add_audit_log(
            actor_id,
            "RECORD_PAYMENT",
            f"Payment {payment_id} of {amount} recorded for {invoice_code}.",
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

    def get_payment_history(
        self, invoice_code=None, client_id=None, requesting_user_id=None
    ):
        """Payment History: filter payments by invoice or client. Uses
        `filter` with a lambda so the predicate stays a one-liner.

        When requesting_user_id is given (and is not an Admin), results
        are always narrowed down to payments that user is allowed to
        see, regardless of the invoice_code/client_id filters passed in."""

        history = self.payments

        if invoice_code is not None:
            history = list(
                filter(lambda payment: payment.invoice_code == invoice_code, history)
            )

        if client_id is not None:
            history = list(
                filter(lambda payment: payment.client_id == client_id, history)
            )

        if requesting_user_id is not None and not self._is_admin(requesting_user_id):

            def is_visible(payment):
                if payment.client_id == requesting_user_id:
                    return True
                invoice = self.find_invoice(payment.invoice_code)
                return (
                    invoice is not None and invoice.freelancer_id == requesting_user_id
                )

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
        actor_id = requesting_user_id or "SYSTEM"
        self.add_audit_log(
            actor_id,
            "COMMISSION_RATE_UPDATED",
            f"Commission rate changed to {new_rate}.",
        )

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

        paid = list(
            filter(lambda payment: payment.status == "Completed", self.payments)
        )
        pending = list(
            filter(lambda payment: payment.status == "Pending", self.payments)
        )
        failed = list(filter(lambda payment: payment.status == "Failed", self.payments))

        total_amount = reduce(
            lambda total, payment: total + payment.amount, self.payments, 0
        )

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

        freelancers = filter(lambda user: user.role == "Freelancer", self.users)

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
                "total_earnings": self.calculate_freelancer_earnings(
                    freelancer.user_id
                ),
            }

        return list(map(build_row, freelancers))

    def project_report(self, requesting_user_id=None):
        if requesting_user_id is not None and not self._is_admin(requesting_user_id):
            raise UnauthorizedAccessError(
                f"User '{requesting_user_id}' is not authorized to view the "
                "project report."
            )

        active = list(
            filter(
                lambda project: project.status in ("Pending", "In Progress"),
                self.projects,
            )
        )
        completed = list(
            filter(lambda project: project.status == "Completed", self.projects)
        )
        late = list(
            filter(lambda project: project.get_health() == "Late", self.projects)
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

        clients = list(filter(lambda user: user.role == "Client", self.users))
        freelancers = list(filter(lambda user: user.role == "Freelancer", self.users))
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

    # GET USER PROJECTS
    def get_user_projects(self, user):
        user_projects = []

        for project in self.projects:
            if user.role == "Client" and project.client_id == user.user_id:
                user_projects.append(project)
            elif user.role == "Freelancer" and project.freelancer_id == user.user_id:
                user_projects.append(project)
            elif user.role == "Admin":
                user_projects.append(project)

        return user_projects

    def get_available_projects(self, user):
        available_projects = []

        for project in self.projects:
            if project.freelancer_id:
                continue
            if project.status != "Open":
                continue
            if freelancer_matches_project(user, project):
                available_projects.append(project)

        return available_projects

    def get_active_projects(self, user=None):
        if user is None:
            projects = self.projects
        else:
            projects = self.get_user_projects(user)

        return list(filter(lambda p: p.status in ("Pending", "In Progress"), projects))

    def get_late_projects(self, user=None):
        if user is None:
            projects = self.projects
        else:
            projects = self.get_user_projects(user)

        return list(filter(lambda p: p.get_health() == "Late", projects))

    def sort_projects_by_deadline(self, projects=None):
        if projects is not None:
            proj_list = projects
        else:
            proj_list = self.projects

        return sorted(proj_list, key=lambda p: p.deadline)

    def sort_projects_by_budget(self, projects=None, descending=True):
        if projects is not None:
            proj_list = projects
        else:
            proj_list = self.projects

        return sorted(proj_list, key=lambda p: float(p.budget), reverse=descending)

    def sort_projects_by_priority(self, projects=None):
        if projects is not None:
            proj_list = projects
        else:
            proj_list = self.projects

        priority_order = {"High": 1, "Medium": 2, "Low": 3}

        return sorted(
            proj_list,
            key=lambda p: priority_order.get(p.priority, 4),
        )

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

    def unassign_freelancer_from_project(self, project, requesting_actor_id=None):

        if not project.freelancer_id:
            return

        freelancer = self.find_user(project.freelancer_id)

        if freelancer is not None and project.project_id in freelancer.project_ids:
            freelancer.project_ids.remove(project.project_id)

        project.freelancer_id = ""

        for milestone in self.get_project_milestones(project.project_id):
            if milestone.status not in ("Approved", "Paid"):
                milestone.update_status("Pending")

    # SAVE DATA
    def save_data(self, msg=True):

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

        with open("data/settings.json", "w") as file:
            json.dump({"commission_rate": self.get_commission_rate()}, file, indent=4)

        if msg:
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
                        user_data["age"],
                        user_data["gender"],
                        user_data["city"],
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
                        user_data["age"],
                        user_data["gender"],
                        user_data["city"],
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
                        user_data["age"],
                        user_data["gender"],
                        user_data["city"],
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
                    project_data.get("required_skills", []),
                    project_data["status"],
                    project_data.get("priority", "Medium"),
                    project_data.get("health", "On Track"),
                )

                project.milestones = project_data.get("milestones", [])

                self.projects.append(project)

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

            # LOAD INVOICES
            with open("data/invoices.json", "r") as file:
                invoices_data = json.load(file)

            self.invoices = []

            for invoice_data in invoices_data:

                invoice_code = invoice_data.get("invoice_code") or invoice_data.get(
                    "invoice_id"
                )

                invoice = Invoice(
                    invoice_code,
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

                invoice_code = payment_data.get("invoice_code") or payment_data.get(
                    "invoice_id"
                )

                payment = Payment(
                    payment_data["payment_id"],
                    invoice_code,
                    payment_data["client_id"],
                    payment_data["amount"],
                    payment_data["payment_method"],
                    payment_data["status"],
                )

                self.payments.append(payment)

            # LOAD AUDIT LOGS
            with open("data/audit_logs.json", "r") as file:
                self.audit_logs = json.load(file)

            for log in self.audit_logs:
                if not log.get("description"):
                    extra = (
                        log.get("invoice_id")
                        or log.get("invoice_code")
                        or log.get("project_id", "")
                    )
                    action = log.get("action", "UNKNOWN")
                    log["description"] = action + (f" ({extra})" if extra else "")

                if not log.get("timestamp"):
                    log["timestamp"] = "Unknown time"

            try:
                with open("data/settings.json", "r") as file:
                    settings = json.load(file)

                rate = float(settings.get("commission_rate", 0.10))
                self.commission_calculator.update_rate(rate)
            except (FileNotFoundError, TypeError, ValueError, json.JSONDecodeError):
                pass

            for invoice in self.invoices:
                paid = round(invoice.amount_paid(self.payments), 2)
                if paid <= 0:
                    invoice.status = "Unpaid"
                elif paid < invoice.amount:
                    invoice.status = "Partially Paid"
                else:
                    invoice.status = "Paid"

            for user in self.users:
                if user.role in ("Client", "Freelancer"):
                    user.project_ids = []

            for project in self.projects:
                client = self.find_user(project.client_id)
                if client is not None and client.role == "Client":
                    if project.project_id not in client.project_ids:
                        client.project_ids.append(project.project_id)

                if project.freelancer_id:
                    freelancer = self.find_user(project.freelancer_id)
                    if freelancer is not None and freelancer.role == "Freelancer":
                        if project.project_id not in freelancer.project_ids:
                            freelancer.project_ids.append(project.project_id)

            for user in self.users:
                if user.role == "Freelancer":
                    user.earnings = self.calculate_freelancer_earnings(user.user_id)

            print("Data loaded successfully.")

        except json.JSONDecodeError:

            print("\n[ERROR] Invalid JSON data.\n")

        except FileNotFoundError:

            print("\n[ERROR] Data files are not found.\n")

        except KeyError:

            print("\n[ERROR] Data files are missing required fields.\n")


class Authentication:

    def __init__(self, manager):
        self.manager = manager
        self.current_user = None

    def register(self):

        while True:
            print_screen("REGISTER")
            print("[1] Client")
            print("[2] Freelancer")
            print("[0] Back")
            print("-" * 50)

            account_type = input("\nEnter your choice (0-2): ").strip()

            if is_cancel(account_type) or account_type == "0":
                return_to("Main Menu")
                return None

            if account_type == "1":
                account_type = "Client"
                break

            if account_type == "2":
                account_type = "Freelancer"
                break

            print("[ERROR] Please choose 1 or 2.")

        # USER ID
        while True:

            user_id = input("Enter your User ID: ").strip().upper()

            if is_cancel(user_id):
                return_to("Main Menu")
                return None

            try:
                validate_user_id(user_id, expected_role=account_type, allow_admin=False)

                if self.manager.find_user(user_id) is not None:
                    print("[ERROR] This User ID is already registered.")
                else:
                    break

            except ValueError as e:
                print(f"[ERROR] {e}")

        # NAME
        while True:

            name_input = input("Enter your name: ").strip()

            if is_cancel(name_input):
                return_to("Main Menu")
                return None

            try:
                name = validate_name(name_input)
                break

            except ValueError as e:
                print(f"[ERROR] {e}")

        # AGE
        while True:

            age_input = input("Enter your age: ").strip()

            if is_cancel(age_input):
                return_to("Main Menu")
                return None

            try:
                age = validate_age(age_input)
                break

            except ValueError as e:
                print(f"[ERROR] {e}")

        # GENDER
        while True:

            gender_input = input("Enter your gender (Male/Female): ").strip()

            if is_cancel(gender_input):
                return_to("Main Menu")
                return None

            try:
                gender = validate_gender(gender_input)
                break

            except ValueError as e:
                print(f"[ERROR] {e}")

        # CITY
        while True:

            city_input = input("Enter your city: ").strip()

            if is_cancel(city_input):
                return_to("Main Menu")
                return None

            try:
                city = validate_city(city_input)
                break

            except ValueError as e:
                print(f"[ERROR] {e}")

        # EMAIL
        while True:

            email_input = input("Enter your email: ").strip()

            if is_cancel(email_input):
                return_to("Main Menu")
                return None

            try:
                email = validate_email(email_input)

                if self.manager.find_email(email) is not None:
                    print("[ERROR] This email is already registered.")
                else:
                    break

            except ValueError as e:
                print(f"[ERROR] {e}")

        # PHONE
        while True:

            phone_input = input("Enter your phone number: ").strip()

            if is_cancel(phone_input):
                return_to("Main Menu")
                return None

            try:
                phone = validate_phone(phone_input)

                if self.manager.find_phone(phone) is not None:
                    print("[ERROR] This phone number is already registered.")
                else:
                    break

            except ValueError as e:
                print(f"[ERROR] {e}")

        # PASSWORD
        while True:

            password = input("Enter your password: ").strip()

            if is_cancel(password):
                return_to("Main Menu")
                return None

            try:
                password = validate_password(password)
                break

            except ValueError as e:
                print(f"[ERROR] {e}")

        # CONFIRM PASSWORD
        while True:

            confirm_password = input("Confirm your password: ").strip()

            if is_cancel(confirm_password):
                return_to("Main Menu")
                return None

            if confirm_password != password:
                print("[ERROR] Passwords do not match.")
            else:
                break

        # CLIENT
        if account_type == "Client":

            while True:

                company_input = input("Enter your company name: ").strip()

                if is_cancel(company_input):
                    return_to("Main Menu")
                    return None

                try:
                    company_name = validate_company_name(company_input)
                    break

                except ValueError as e:
                    print(f"[ERROR] {e}")

            user = Client(
                user_id,
                name,
                email,
                phone,
                password,
                age,
                gender,
                city,
                company_name,
            )

        # FREELANCER
        else:

            # SKILLS
            while True:

                skills_input = input("Enter your skills separated by commas: ")

                if is_cancel(skills_input):
                    return_to("Main Menu")
                    return None

                try:
                    skills = validate_skills(skills_input)
                    break

                except ValueError as e:
                    print(f"[ERROR] {e}")

            # HOURLY RATE
            while True:

                hourly_rate_input = input("Enter your hourly rate: ")

                if is_cancel(hourly_rate_input):
                    return_to("Main Menu")
                    return None

                try:
                    hourly_rate = validate_hourly_rate(hourly_rate_input)
                    break

                except ValueError as e:
                    print(f"[ERROR] {e}")

            user = Freelancer(
                user_id,
                name,
                email,
                phone,
                password,
                age,
                gender,
                city,
                skills,
                hourly_rate,
            )

        # ADD USER
        self.manager.add_user(user)

        # AUDIT LOG
        self.manager.add_audit_log(user_id, "USER_REGISTERED", "New user registered.")

        # SAVE DATA
        self.manager.save_data()

        print_menu("REGISTRATION SUCCESSFUL")
        print(f"    Account Type: {user.role}")
        print(f"    Welcome: {user.name}")
        print("=" * 50)

        self.current_user = user
        return user

    def login(self):

        max_attempts = 3

        print_screen("LOGIN")
        attempt = 1

        while attempt <= max_attempts:

            print(f"\nLogin attempt {attempt} of {max_attempts}")

            # User ID
            while True:

                user_id = input("Enter your User ID: ").strip().upper()

                if is_cancel(user_id):
                    return_to("Main Menu")
                    return None

                try:
                    validate_user_id(user_id)
                    break

                except ValueError as e:
                    print(f"[ERROR] {e}")
                    continue

            # Password
            while True:

                password = input("Enter your password: ").strip()

                if is_cancel(password):
                    return_to("Main Menu")
                    return None

                if password == "":
                    print("[ERROR] Password cannot be empty.")
                    continue

                break

            # Find user
            found_user = self.manager.find_user(user_id)

            if found_user is None:
                print("[ERROR] Invalid User ID or password.")
                attempt += 1
                continue

            # Check password
            if found_user.password != password:
                print("[ERROR] Invalid User ID or password.")
                attempt += 1
                continue

            if not found_user.active:
                print("[ERROR] This account is inactive.")
                return None

            # Login successful
            self.current_user = found_user

            self.manager.add_audit_log(
                found_user.user_id, "USER_LOGIN", "User logged in successfully."
            )
            self.manager.save_data(msg=False)

            print_menu(f"Welcome back, {found_user.name}!")

            return found_user

        print_screen("LOGIN FAILED", hint=None)
        print("    Maximum attempts reached.")
        print("-" * 50)

        return None

    def logout(self):

        if self.current_user is None:
            print("No user is currently logged in.")
            return

        user_id = self.current_user.user_id

        self.manager.add_audit_log(user_id, "USER_LOGOUT", "User logged out.")
        self.current_user = None
        self.manager.save_data(msg=False)
        print("Logout successful.")
