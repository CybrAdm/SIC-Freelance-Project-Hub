import json
import os


class FreelanceManager:

    def __init__(self):
        self.users = []
        self.projects = []
        self.milestones = []
        self.invoices = []
        self.payments = []
        self.audit_logs = []

        self.create_data_files()

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

    def find_invoice(self, invoice_id):

        for invoice in self.invoices:

            if invoice.invoice_id == invoice_id:
                return invoice

        return None

    def find_payment(self, payment_id):

        for payment in self.payments:

            if payment.payment_id == payment_id:
                return payment

        return None

    # LINK PROJECT MILESTONES
    def get_project_milestones(self, project_id):
        project_milestones = []

        for milestone in self.milestones:
            if milestone.project_id == project_id:
                project_milestones.append(milestone)

        return project_milestones

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
                    project_data.get("priority", "Medium"),
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
        self.project_ids = []

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
        priority="Medium",
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
            "priority": self.priority,
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
        invoice_id,
        project_id,
        client_id,
        freelancer_id,
        amount,
        commission,
        due_date,
        status="Unpaid",
    ):
        self.invoice_id = invoice_id
        self.project_id = project_id
        self.client_id = client_id
        self.freelancer_id = freelancer_id
        self.amount = amount
        self.commission = commission
        self.net_amount = amount - commission
        self.due_date = due_date
        self.status = status

    def to_dict(self):
        return {
            "invoice_id": self.invoice_id,
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
        invoice_id,
        client_id,
        amount,
        payment_method,
        status="Completed",
    ):

        self.payment_id = payment_id
        self.invoice_id = invoice_id
        self.client_id = client_id
        self.amount = amount
        self.payment_method = payment_method
        self.status = status

    def to_dict(self):
        return {
            "payment_id": self.payment_id,
            "invoice_id": self.invoice_id,
            "client_id": self.client_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "status": self.status,
        }


manager = FreelanceManager()
