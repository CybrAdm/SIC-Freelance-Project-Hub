import datetime
from functools import reduce


class MissingFreelancerError(Exception):
    pass


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


class ProjectIterator:

    def __init__(self, projects):
        self._projects = projects
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._projects):
            project = self._projects[self._index]
            self._index += 1
            return project
        raise StopIteration


class User:

    def __init__(self, user_id, name, email, phone, age, gender, city, password, role):

        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.age = age
        self.gender = gender
        self.city = city
        self.password = password
        self.role = role
        self.active = True

    def profile_summary(self):
        status = "Active" if self.active else "Inactive"
        return (
            "\n"
            + "-" * 50
            + "\n"
            + "USER PROFILE".center(50)
            + "\n"
            + "-" * 50
            + "\n"
            + f"    User ID: {self.user_id}\n"
            + f"    Name: {self.name}\n"
            + f"    Email: {self.email}\n"
            + f"    Phone: {self.phone}\n"
            + f"    Role: {self.role}\n"
            + f"    Status: {status}\n"
            + "-" * 50
            + "\n"
        )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "age": self.age,
            "gender": self.gender,
            "city": self.city,
            "password": self.password,
            "role": self.role,
            "active": self.active,
        }


class Client(User):

    def __init__(
        self, user_id, name, email, phone, password, age, gender, city, company_name
    ):
        super().__init__(
            user_id, name, email, phone, age, gender, city, password, "Client"
        )

        self.company_name = company_name
        self.project_ids = []

    def profile_summary(self):
        status = "Active" if self.active else "Inactive"
        return (
            "\n"
            + "-" * 50
            + "\n"
            + "CLIENT PROFILE".center(50)
            + "\n"
            + "-" * 50
            + "\n"
            + f"    ID: {self.user_id}\n"
            + f"    Name: {self.name}\n"
            + f"    Email: {self.email}\n"
            + f"    Phone: {self.phone}\n"
            + f"    Age: {self.age}\n"
            + f"    Gender: {self.gender}\n"
            + f"    City: {self.city}\n"
            + f"    Company: {self.company_name}\n"
            + f"    Projects: {len(self.project_ids)}\n"
            + f"    Status: {status}\n"
            + "-" * 50
            + "\n"
        )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "age": self.age,
            "gender": self.gender,
            "city": self.city,
            "password": self.password,
            "role": self.role,
            "active": self.active,
            "company_name": self.company_name,
            "project_ids": self.project_ids,
        }


class Freelancer(User):

    def __init__(
        self,
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
    ):
        super().__init__(
            user_id, name, email, phone, age, gender, city, password, "Freelancer"
        )

        self.skills = skills
        self.hourly_rate = hourly_rate
        self.project_ids = []
        self.earnings = 0

    def profile_summary(self):
        status = "Active" if self.active else "Inactive"
        skills = ", ".join(self.skills)
        return (
            "\n"
            + "-" * 50
            + "\n"
            + "FREELANCER PROFILE".center(50)
            + "\n"
            + "-" * 50
            + "\n"
            + f"    ID: {self.user_id}\n"
            + f"    Name: {self.name}\n"
            + f"    Email: {self.email}\n"
            + f"    Phone: {self.phone}\n"
            + f"    Age: {self.age}\n"
            + f"    Gender: {self.gender}\n"
            + f"    City: {self.city}\n"
            + f"    Skills: {skills}\n"
            + f"    Hourly Rate: {self.hourly_rate}\n"
            + f"    Projects: {len(self.project_ids)}\n"
            + f"    Earnings: {self.earnings}\n"
            + f"    Status: {status}\n"
            + "-" * 50
            + "\n"
        )

    def to_dict(self):

        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "password": self.password,
            "role": self.role,
            "active": self.active,
            "age": self.age,
            "gender": self.gender,
            "city": self.city,
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
        required_skills=None,
        status="Open",
        priority="Medium",
        health="On Track",
    ):
        self.project_id = project_id
        self.title = title
        self.description = description
        self.client_id = client_id
        self.freelancer_id = freelancer_id
        self.budget = budget
        self.deadline = deadline
        self.status = status
        self.priority = priority
        self.health = health
        self.required_skills = required_skills if required_skills else []
        self.milestones = []

    def get_health(self):
        if self.status == "Completed":
            health = "Completed"
        else:
            try:
                deadline_date = datetime.datetime.strptime(
                    self.deadline, "%Y-%m-%d"
                ).date()
                today = datetime.datetime.now().date()

                if today > deadline_date:
                    health = "Late"
                elif (deadline_date - today).days <= 3:
                    health = "At Risk"
                else:
                    health = "On Track"
            except (ValueError, TypeError):
                health = "On Track"

        self.health = health
        return health

    def to_dict(self):

        return {
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "client_id": self.client_id,
            "freelancer_id": self.freelancer_id,
            "budget": self.budget,
            "deadline": self.deadline,
            "required_skills": self.required_skills,
            "status": self.status,
            "priority": self.priority,
            "health": self.get_health(),
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
        self.history.append(
            {
                "old_status": old_status,
                "new_status": new_status,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

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
        self.invoice_id = invoice_code
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
        self.invoice_id = invoice_code
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
