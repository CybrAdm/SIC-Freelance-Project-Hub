from classes import (
    Freelancer,
    ProjectIterator,
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
    print_screen,
    return_to,
    validate_user_id,
    validate_project_id,
)

FINANCE_ERRORS = (
    InvalidInvoiceCodeError,
    InvoiceNotFoundError,
    ProjectNotReadyForInvoiceError,
    InvalidPaymentAmountError,
    PaymentExceedsBalanceError,
    PaymentNotFoundError,
    MilestoneNotFoundError,
    UnauthorizedAccessError,
    ValueError,
)

def print_users(users):
    if not users:
        print("\nNo users yet.")
        return

    print_screen("USERS", hint=None)

    for counter, user in enumerate(users, 1):
        print(f"[{counter}] ID: {user.user_id}")
        print(f"    Name: {user.name}")
        print(f"    Role: {user.role}")
        print(f"    Email: {user.email}")
        print(f"    Status: {'Active' if user.active else 'Inactive'}")
        print("-" * 50)

def print_projects(projects):
    if not projects:
        print("\nNo projects yet.")
        return

    print_screen("PROJECTS", hint=None)

    for counter, project in enumerate(ProjectIterator(projects), 1):
        freelancer_info = (
            project.freelancer_id if project.freelancer_id else "Unassigned"
        )
        print(f"[{counter}] ID: {project.project_id}")
        print(f"    Title: {project.title}")
        print(f"    Description: {project.description}")
        print(f"    Client ID: {project.client_id}")
        print(f"    Freelancer ID: {freelancer_info}")
        print(
            f"    Required Skills: {', '.join(project.required_skills) if project.required_skills else 'None'}"
        )
        print(f"    Status: {project.status}")
        print(f"    Priority: {project.priority}")
        print(f"    Health: {project.get_health()}")
        print(f"    Budget: {project.budget}")
        print(f"    Deadline: {project.deadline}")
        print("-" * 50)

def print_milestones_list(milestones):
    if not milestones:
        print("\nNo milestones yet.")
        return

    print_screen("MILESTONES", hint=None)

    for counter, milestone in enumerate(milestones, 1):
        print(f"[{counter}] ID: {milestone.milestone_id}")
        print(f"    Project ID: {milestone.project_id}")
        print(f"    Title: {milestone.title}")
        print(f"    Description: {milestone.description}")
        print(f"    Amount: ${milestone.amount}")
        print(f"    Deadline: {milestone.deadline}")
        print(f"    Status: {milestone.status}")
        print("-" * 50)

def print_invoice(invoice, manager):
    print_screen("INVOICE", hint=None)
    print(f"    Code: {invoice.invoice_code}")
    print(f"    Project ID: {invoice.project_id}")
    print(f"    Client ID: {invoice.client_id}")
    print(f"    Freelancer ID: {invoice.freelancer_id}")
    print(f"    Amount: ${invoice.amount}")
    print(f"    Commission: ${invoice.commission}")
    print(f"    Net Amount: ${invoice.net_amount}")
    print(f"    Due Date: {invoice.due_date}")
    print(f"    Status: {invoice.status}")
    print(f"    Amount Paid: ${invoice.amount_paid(manager.payments)}")
    print(f"    Balance Due: ${invoice.balance_due(manager.payments)}")
    print("-" * 50)

def print_payment(payment):
    print_screen("PAYMENT", hint=None)
    print(f"    Payment ID: {payment.payment_id}")
    print(f"    Invoice Code: {payment.invoice_code}")
    print(f"    Client ID: {payment.client_id}")
    print(f"    Amount: ${payment.amount}")
    print(f"    Method: {payment.payment_method}")
    print(f"    Status: {payment.status}")
    print("-" * 50)

def print_report(title, data):
    print_screen(title, hint=None)

    for key, value in data.items():
        label = key.replace("_", " ").title()
        print(f"    {label}: {value}")

    print("-" * 50)

def prompt_freelancer(auth, back_menu):
    freelancer_id_input = input("Enter Freelancer ID: ").strip()

    if is_cancel(freelancer_id_input):
        return_to(back_menu)
        return None

    try:
        validate_user_id(freelancer_id_input, expected_role="Freelancer")
    except ValueError as e:
        print(f"[ERROR] {e}")
        return None

    freelancer_id = freelancer_id_input.strip().upper()
    freelancer = auth.manager.find_user(freelancer_id)

    if freelancer is None or not isinstance(freelancer, Freelancer):
        print(f"[ERROR] No freelancer found with ID {freelancer_id}.")
        return None

    return freelancer

def prompt_client(auth, back_menu):
    client_id_input = input("Enter Client ID: ").strip()

    if is_cancel(client_id_input):
        return_to(back_menu)
        return None

    try:
        validate_user_id(client_id_input, expected_role="Client")
    except ValueError as e:
        print(f"[ERROR] {e}")
        return None

    client_id = client_id_input.strip().upper()
    client = auth.manager.find_user(client_id)

    if client is None or client.role != "Client":
        print(f"[ERROR] No client found with ID {client_id}.")
        return None

    return client

def prompt_project(auth, back_menu):
    project_id_input = input("Enter Project ID: ").strip()

    if is_cancel(project_id_input):
        return_to(back_menu)
        return None

    try:
        project_id = validate_project_id(project_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return None

    project = auth.manager.find_project(project_id)

    if project is None:
        print("[ERROR] Project not found.")
        return None

    return project

def current_user_id(auth):
    return auth.current_user.user_id if auth.current_user is not None else None

