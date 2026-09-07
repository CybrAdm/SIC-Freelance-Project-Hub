import datetime
import re


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


def validate_project_id(project_id):

    project_id = project_id.strip().upper()

    if len(project_id) == 0:
        raise ValueError("ID cannot be empty.")

    if len(project_id) < 4:
        raise ValueError("ID must contain at least 4 characters.")

    pattern = r"^P\d{3,}$"

    if not re.match(pattern, project_id):
        raise ValueError(
            "Invalid Project ID. It must start with P "
            "followed by at least 3 digits (e.g. P101, P2026)."
        )

    return project_id


def validate_milestone_id(milestone_id):

    milestone_id = milestone_id.strip().upper()

    if len(milestone_id) == 0:
        raise ValueError("ID cannot be empty.")

    if len(milestone_id) < 4:
        raise ValueError("ID must contain at least 4 characters.")

    pattern = r"^M\d{3,}$"

    if not re.match(pattern, milestone_id):
        raise ValueError(
            "Invalid Milestone ID. It must start with M "
            "followed by at least 3 digits (e.g. M101, M2026)."
        )

    return milestone_id


def validate_priority(priority):

    priority = priority.strip().capitalize()

    if priority == "":
        return "Medium"

    if priority not in ["Low", "Medium", "High"]:
        raise ValueError("Priority must be Low, Medium, or High.")

    return priority


def validate_status(status):

    status = status.strip().title()

    if status == "":
        return "Open"

    if status not in ["Open", "Pending", "In Progress", "Completed"]:
        raise ValueError("Status must be Open, Pending, In Progress, or Completed.")

    return status


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

    return password


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
    seen = set()

    for skill in skills_input.split(","):

        skill = skill.strip()

        if skill == "":
            raise ValueError("Skill cannot be empty.")

        if skill.lower() in seen:
            continue

        seen.add(skill.lower())
        skills.append(skill)

    if not skills:
        raise ValueError("Skills cannot be empty.")

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

    return round(hourly_rate, 2)


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

    return round(amount, 2)


def validate_date(date):

    date = date.strip()

    if date == "":
        raise ValueError("Date cannot be empty.")

    pattern = r"^\d{4}-\d{2}-\d{2}$"

    if not re.match(pattern, date):
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    try:
        parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date. This date does not exist.")

    if parsed_date < datetime.datetime.now().date():
        raise ValueError("Date cannot be in the past.")

    return date
