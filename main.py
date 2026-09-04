import datetime
import json
import os
import re


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
            "\n" + "=" * 50 + "\n"
            "                 USER PROFILE\n" + "=" * 50 + "\n"
            f"  User ID       : {self.user_id}\n"
            f"  Name          : {self.name}\n"
            f"  Email         : {self.email}\n"
            f"  Phone         : {self.phone}\n"
            f"  Role          : {self.role}\n"
            f"  Status        : {status}\n" + "=" * 50 + "\n"
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
            "\n" + "=" * 50 + "\n"
            "                CLIENT PROFILE\n" + "=" * 50 + "\n"
            f"  ID            : {self.user_id}\n"
            f"  Name          : {self.name}\n"
            f"  Email         : {self.email}\n"
            f"  Phone         : {self.phone}\n"
            f"  Age           : {self.age}\n"
            f"  Gender        : {self.gender}\n"
            f"  City          : {self.city}\n"
            f"  Company       : {self.company_name}\n"
            f"  Projects      : {len(self.project_ids)}\n"
            f"  Status        : {status}\n" + "=" * 50 + "\n"
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
            "\n" + "=" * 50 + "\n"
            "              FREELANCER PROFILE\n" + "=" * 50 + "\n"
            f"  ID            : {self.user_id}\n"
            f"  Name          : {self.name}\n"
            f"  Email         : {self.email}\n"
            f"  Phone         : {self.phone}\n"
            f"  Age           : {self.age}\n"
            f"  Gender        : {self.gender}\n"
            f"  City          : {self.city}\n"
            f"  Skills        : {skills}\n"
            f"  Hourly Rate   : {self.hourly_rate}\n"
            f"  Projects      : {len(self.project_ids)}\n"
            f"  Earnings      : {self.earnings}\n"
            f"  Status        : {status}\n" + "=" * 50 + "\n"
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
                    project_data["status"],
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


class Authentication:

    def __init__(self, manager):
        self.manager = manager
        self.current_user = None

    def register(self):

        print("\n" + "-" * 50)
        print("                 REGISTER")
        print("-" * 50)

        print("\nType cancel at any time to stop registration.")

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
                validate_password(password)
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
        print("\nType cancel at any time to stop login.")
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


def is_cancel(value):
    return value.strip().lower() == "cancel"


def validate_user_id(user_id, expected_role=None, allow_admin=True):

    user_id = user_id.strip().upper()

    if len(user_id) == 0:
        raise ValueError("ID cannot be empty.")

    if len(user_id) < 4:
        raise ValueError("ID must contain at least 4 characters.")

    pattern = r"^[CFA]\d{3,}$"

    if not re.match(pattern, user_id):
        raise ValueError(
            "Invalid User ID. It must start with C, F or A "
            "followed by at least 3 digits (e.g. C101, F2026)."
        )

    prefix = user_id[0]

    if prefix.upper() == "A" and not allow_admin:
        raise ValueError("Admin IDs cannot be used for self-registration.")

    if expected_role is not None:
        expected_prefix = {"Client": "C", "Freelancer": "F", "Admin": "A"}[
            expected_role
        ]

        if prefix.upper() != expected_prefix:
            raise ValueError(
                f"User ID must start with '{expected_prefix}' for a {expected_role}."
            )

    return True


def validate_name(name):

    name = name.strip()

    if len(name) == 0:
        raise ValueError("Name cannot be empty.")

    if len(name) < 2:
        raise ValueError("Name must contain at least 2 characters.")

    pattern = r"^[A-Za-z ]+$"

    if not re.match(pattern, name):
        raise ValueError("Name can contain letters and spaces only.")

    if "  " in name:
        raise ValueError("Name cannot contain consecutive spaces.")

    return name


def validate_email(email):

    email = email.strip().lower()

    if email == "":
        raise ValueError("Email cannot be empty.")

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(pattern, email):
        raise ValueError("Invalid email format.")

    return email


def validate_phone(phone):

    phone = phone.strip()

    if phone == "":
        raise ValueError("Phone number cannot be empty.")

    pattern = r"^(010|011|012|015)\d{8}$"

    if not re.match(pattern, phone):
        raise ValueError(
            "Invalid phone number. Use an Egyptian mobile number "
            "(11 digits, starting with 010/011/012/015)."
        )

    return phone


def validate_gender(gender):

    gender = gender.strip().capitalize()

    if gender == "":
        raise ValueError("Gender cannot be empty.")

    if gender not in ["Male", "Female"]:
        raise ValueError("Gender must be Male or Female.")

    return gender


def validate_age(age):

    if age == "":
        raise ValueError("Age cannot be empty.")

    if not age.isdigit():
        raise ValueError("Age must be a number.")

    age = int(age)

    if age < 18 or age > 100:
        raise ValueError("Age must be between 18 and 100.")

    return age


def validate_city(city):

    city = city.strip()

    if city == "":
        raise ValueError("City cannot be empty.")

    if len(city) < 2:
        raise ValueError("City must contain at least 2 characters.")

    return city


def validate_password(password):

    if password == "":
        raise ValueError("Password cannot be empty.")

    if len(password) < 6:
        raise ValueError("Password must contain at least 6 characters.")

    if " " in password:
        raise ValueError("Password cannot contain spaces.")

    if not re.search(r"[A-Za-z]", password):
        raise ValueError("Password must contain at least one letter.")

    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one number.")

    return True


def validate_company_name(company_name):
    company_name = company_name.strip()

    if company_name == "":
        raise ValueError("Company name cannot be empty.")

    if len(company_name) < 2:
        raise ValueError("Company name must contain at least 2 characters.")

    return company_name


def validate_skills(skills_input):

    skills_input = skills_input.strip()

    if skills_input == "":
        raise ValueError("Skills cannot be empty.")

    skills = []

    for skill in skills_input.split(","):

        skill = skill.strip()

        if skill == "":
            raise ValueError("Skill cannot be empty.")

        skills.append(skill)

    return skills


def validate_hourly_rate(hourly_rate):

    hourly_rate = hourly_rate.strip()

    if hourly_rate == "":
        raise ValueError("Hourly rate cannot be empty.")

    try:
        hourly_rate = float(hourly_rate)
    except ValueError:
        raise ValueError("Hourly rate must be a number.")

    if hourly_rate <= 0:
        raise ValueError("Hourly rate must be greater than 0.")

    return hourly_rate


def validate_amount(amount):

    amount = amount.strip()

    if amount == "":
        raise ValueError("Amount cannot be empty.")

    try:
        amount = float(amount)
    except ValueError:
        raise ValueError("Amount must be a number.")

    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")

    return amount


def validate_date(date):

    date = date.strip()

    if date == "":
        raise ValueError("Date cannot be empty.")

    pattern = r"^\d{4}-\d{2}-\d{2}$"

    if not re.match(pattern, date):
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date. This date does not exist.")

    return date


def admin_menu(auth):
    while True:
        print("\n" + "=" * 50)
        print("                 ADMIN MENU")
        print("=" * 50)
        print("[1] View profile")
        print("[2] View all users")
        print("[3] View all projects")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-3): ").strip()

        if choice == "1":
            print(auth.current_user.profile_summary())
        elif choice == "2":
            print_users(auth.manager.users)
        elif choice == "3":
            print_projects(auth.manager.projects)
        elif choice == "0":
            auth.logout()
            return
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-3).\n")


def print_users(users):
    if not users:
        print("\n[ERROR] No users yet.")
        return

    print("\n" + "-" * 50)
    print("                  USERS")
    print("-" * 50)

    for counter, user in enumerate(users, 1):
        print(
            f"[{counter}] {user.user_id} | " f"{user.name} | {user.role} | {user.email}"
        )


def print_projects(projects):
    if not projects:
        print("\nNo projects yet.")
        return

    print("\n" + "-" * 50)
    print("                 PROJECTS")
    print("-" * 50)

    for counter, project in enumerate(projects, 1):
        print(f"[{counter}] ID: {project.project_id}")
        print(f"    Title: {project.title}")
        print(f"    Status: {project.status}")
        print(f"    Budget: {project.budget}")
        print(f"    Deadline: {project.deadline}")
        print("-" * 50)


def client_menu(auth):
    while True:
        print("\n" + "=" * 50)
        print("                 CLIENT MENU")
        print("=" * 50)
        print("[1] View profile")
        print("[2] View my projects")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-2): ").strip()

        if choice == "1":
            print(auth.current_user.profile_summary())
        elif choice == "2":
            print_projects(auth.manager.get_user_projects(auth.current_user))
        elif choice == "0":
            auth.logout()
            return
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-2).\n")


def freelancer_menu(auth):
    while True:
        print("\n" + "=" * 50)
        print("               FREELANCER MENU")
        print("=" * 50)
        print("[1] View profile")
        print("[2] View my projects")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-2): ").strip()

        if choice == "1":
            print(auth.current_user.profile_summary())
        elif choice == "2":
            print_projects(auth.manager.get_user_projects(auth.current_user))
        elif choice == "0":
            auth.logout()
            return
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-2).\n")


def user_home(auth):
    role = auth.current_user.role

    if role == "Client":
        client_menu(auth)
    elif role == "Freelancer":
        freelancer_menu(auth)
    else:
        admin_menu(auth)


def landing_page(auth):
    while True:
        print("\n")
        print("=" * 50)
        print("             SIC FREELANCE PROJECT HUB")
        print("=" * 50)
        print("         Connecting Clients & Freelancers")
        print("-" * 50)
        print("[1] Login")
        print("[2] Register")
        print("[0] Exit")
        print("-" * 50)
        choiceInput = input("\nEnter your choice (0-2): ").strip()

        if choiceInput == "":
            print("\n[ERROR] Choice cannot be empty.\n")
            continue

        if not choiceInput.isdigit():
            print("\n[ERROR] Invalid choice. Please enter numbers only.\n")
            continue

        choice = int(choiceInput)

        if choice not in [0, 1, 2]:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-2).\n")
            continue

        if choice == 1:
            user = auth.login()
            if user is not None:
                user_home(auth)

        elif choice == 2:
            user = auth.register()
            if user is not None:
                user_home(auth)

        else:
            print("\nExiting...\n")
            return


def main():
    manager = FreelanceManager()
    manager.load_data()
    auth = Authentication(manager)

    landing_page(auth)


if __name__ == "__main__":
    main()
