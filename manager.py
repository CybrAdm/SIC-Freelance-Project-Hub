import datetime
import json
import os

from classes import (
    User,
    Client,
    Freelancer,
    Project,
    Milestone,
    Invoice,
    Payment,
)
from validators import (
    is_cancel,
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

MAX_ACTIVE_PROJECTS = 3


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

            if not project.required_skills:
                available_projects.append(project)
                continue

            user_skills = [skill.lower() for skill in user.skills]

            for skill in project.required_skills:
                if skill.lower() in user_skills:
                    available_projects.append(project)
                    break

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

                invoice = Invoice(
                    invoice_data["invoice_id"],
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
                    payment_data["invoice_id"],
                    payment_data["client_id"],
                    payment_data["amount"],
                    payment_data["payment_method"],
                    payment_data["status"],
                )

                self.payments.append(payment)

            # LOAD AUDIT LOGS
            with open("data/audit_logs.json", "r") as file:
                self.audit_logs = json.load(file)

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

        print("\n" + "-" * 50)
        print("                 REGISTER")
        print("-" * 50)
        print("(Type cancel at any time to cancel the operation)")
        print("-" * 50)

        # ACCOUNT TYPE
        while True:

            account_type = input(
                "\n[1] Client\n" "[2] Freelancer\n" "Choose account type: "
            ).strip()

            if is_cancel(account_type):
                print("\nRegistration cancelled.")
                return None

            elif account_type == "1":
                account_type = "Client"
                break

            elif account_type == "2":
                account_type = "Freelancer"
                break

            else:
                print("\n[ERROR] Please choose 1 or 2.\n")

        # USER ID
        while True:

            user_id = input("Enter your User ID: ").strip().upper()

            if is_cancel(user_id):
                print("\nRegistration cancelled.")
                return None

            try:
                validate_user_id(user_id, expected_role=account_type, allow_admin=False)

                if self.manager.find_user(user_id) is not None:
                    print("\n[ERROR] This User ID is already registered.\n")
                else:
                    break

            except ValueError as e:
                print(f"\n[ERROR] {e}\n")

        # NAME
        while True:

            name_input = input("Enter your name: ").strip()

            if is_cancel(name_input):
                print("\nRegistration cancelled.")
                return None

            try:
                name = validate_name(name_input)
                break

            except ValueError as e:
                print(f"\n[ERROR] {e}\n")

        # AGE
        while True:

            age_input = input("Enter your age: ").strip()

            if is_cancel(age_input):
                print("\nRegistration cancelled.")
                return None

            try:
                age = validate_age(age_input)
                break

            except ValueError as e:
                print(f"\n[ERROR] {e}\n")

        # GENDER
        while True:

            gender_input = input("Enter your gender (Male/Female): ").strip()

            if is_cancel(gender_input):
                print("\nRegistration cancelled.")
                return None

            try:
                gender = validate_gender(gender_input)
                break

            except ValueError as e:
                print(f"\n[ERROR] {e}\n")

        # CITY
        while True:

            city_input = input("Enter your city: ").strip()

            if is_cancel(city_input):
                print("\nRegistration cancelled.")
                return None

            try:
                city = validate_city(city_input)
                break

            except ValueError as e:
                print(f"\n[ERROR] {e}\n")

        # EMAIL
        while True:

            email_input = input("Enter your email: ").strip()

            if is_cancel(email_input):
                print("\nRegistration cancelled.")
                return None

            try:
                email = validate_email(email_input)

                if self.manager.find_email(email) is not None:
                    print("\n[ERROR] This email is already registered.\n")
                else:
                    break

            except ValueError as e:
                print(f"\n[ERROR] {e}\n")

        # PHONE
        while True:

            phone_input = input("Enter your phone number: ").strip()

            if is_cancel(phone_input):
                print("\nRegistration cancelled.")
                return None

            try:
                phone = validate_phone(phone_input)

                if self.manager.find_phone(phone) is not None:
                    print("\n[ERROR] This phone number is already registered.\n")
                else:
                    break

            except ValueError as e:
                print(f"\n[ERROR] {e}\n")

        # PASSWORD
        while True:

            password = input("Enter your password: ").strip()

            if is_cancel(password):
                print("\nRegistration cancelled.")
                return None

            try:
                password = validate_password(password)
                break

            except ValueError as e:
                print(f"\n[ERROR] {e}\n")

        # CONFIRM PASSWORD
        while True:

            confirm_password = input("Confirm your password: ").strip()

            if is_cancel(confirm_password):
                print("\nRegistration cancelled.")
                return None

            if confirm_password != password:
                print("\n[ERROR] Passwords do not match.\n")
            else:
                break

        # CLIENT
        if account_type == "Client":

            while True:

                company_input = input("Enter your company name: ").strip()

                if is_cancel(company_input):
                    print("\nRegistration cancelled.")
                    return None

                try:
                    company_name = validate_company_name(company_input)
                    break

                except ValueError as e:
                    print(f"\n[ERROR] {e}\n")

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
                    print("\nRegistration cancelled.")
                    return None

                try:
                    skills = validate_skills(skills_input)
                    break

                except ValueError as e:
                    print(f"\n[ERROR] {e}\n")

            # HOURLY RATE
            while True:

                hourly_rate_input = input("Enter your hourly rate: ")

                if is_cancel(hourly_rate_input):
                    print("\nRegistration cancelled.")
                    return None

                try:
                    hourly_rate = validate_hourly_rate(hourly_rate_input)
                    break

                except ValueError as e:
                    print(f"\n[ERROR] {e}\n")

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

        print("\n" + "=" * 45)
        print("       REGISTRATION SUCCESSFUL")
        print("=" * 45)
        print("Account Type:", user.role)
        print("Welcome,", user.name)

        self.current_user = user
        return user

    def login(self):

        max_attempts = 3

        print("\n" + "-" * 50)
        print("                   LOGIN")
        print("-" * 50)
        print("(Type cancel at any time to cancel the operation)")
        print("-" * 50)
        attempt = 1

        while attempt <= max_attempts:

            print(f"\nLogin attempt {attempt} of {max_attempts}")

            # User ID
            while True:

                user_id = input("Enter your User ID: ").strip().upper()

                if is_cancel(user_id):
                    print("\nLogin cancelled.")
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
                    print("\nLogin cancelled.")
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

            print("\n" + "=" * 45)
            print(f"     Welcome back, {found_user.name}!")
            print("=" * 45 + "\n")

            return found_user

        print("\nLOGIN FAILED")
        print("Maximum attempts reached.")

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
