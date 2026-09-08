import os
import re
from functools import reduce
from main import FreelanceManager, Invoice, Payment, Freelancer, Client, Project, manager

# ==========================================
# 1. REGEX VALIDATION FUNCTIONS (Chapter 3)
# ==========================================
def validate_invoice_code(code: str) -> bool:
    """Validates Invoice Code format (e.g., INV-1001 or INV-2024-01)."""
    pattern = r"^INV-\d{4,}(-\d+)?$"
    return bool(re.match(pattern, code))

def validate_email(email: str) -> bool:
    """Validates Email format."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validates Phone number format (10-15 digits, optional +)."""
    pattern = r"^\+?\d{10,15}$"
    return bool(re.match(pattern, phone))


# ==========================================
# 2. CLOSURE & nonlocal (Chapter 3)
# ==========================================
def create_commission_closure(initial_rate: float = 0.10):
    """
    Closure to hold and modify platform commission rate dynamically
    using the 'nonlocal' keyword.
    """
    commission_rate = initial_rate

    def calculate_commission(amount: float) -> float:
        return amount * commission_rate

    def set_commission_rate(new_rate: float):
        nonlocal commission_rate
        if 0 <= new_rate <= 1:
            commission_rate = new_rate
            print(f"Commission rate updated successfully to {commission_rate * 100:.1f}%")
        else:
            print("Invalid rate. Must be between 0 and 1 (e.g., 0.10 for 10%).")

    def get_commission_rate() -> float:
        return commission_rate

    return calculate_commission, set_commission_rate, get_commission_rate

# Initialize closure instance
calc_commission, set_commission_rate, get_commission_rate = create_commission_closure(0.10)


# ==========================================
# 3. reduce() FOR EARNINGS (Chapter 3)
# ==========================================
def calculate_freelancer_earnings(freelancer_id: str) -> float:
    """Calculates total net earnings for a freelancer using reduce()."""
    paid_invoices = [
        inv for inv in manager.invoices
        if inv.freelancer_id == freelancer_id and inv.status == "Paid"
    ]
    if not paid_invoices:
        return 0.0

    return reduce(lambda acc, inv: acc + inv.net_amount, paid_invoices, 0.0)


# ==========================================
# 4. INVOICE MANAGEMENT
# ==========================================
def generate_invoice():
    print("\n--- Generate Invoice ---")
    invoice_code = input("Enter Invoice Code (e.g., INV-1001): ").strip()
    if not validate_invoice_code(invoice_code):
        print("Invalid Invoice Code format! Must follow pattern 'INV-XXXX'.")
        return

    if manager.find_invoice(invoice_code):
        print("An invoice with this code already exists.")
        return

    project_id = input("Enter Project ID: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Project not found.")
        return

    client_id = project.client_id
    freelancer_id = project.freelancer_id

    try:
        amount = float(input("Enter Invoice Amount: "))
        if amount <= 0:
            print("Amount must be greater than zero.")
            return
    except ValueError:
        print("Invalid amount input.")
        return

    due_date = input("Enter Due Date (YYYY-MM-DD): ").strip()
    commission = calc_commission(amount)

    invoice = Invoice(
        invoice_id=invoice_code,
        project_id=project_id,
        client_id=client_id,
        freelancer_id=freelancer_id,
        amount=amount,
        commission=commission,
        due_date=due_date,
        status="Unpaid"
    )

    manager.add_invoice(invoice)
    manager.save_data()
    print(f"Invoice {invoice_code} generated successfully! Net Amount: ${invoice.net_amount:.2f}")


def view_invoices():
    print("\n--- All Invoices ---")
    if not manager.invoices:
        print("No invoices found.")
        return

    for inv in manager.invoices:
        print(f"Code: {inv.invoice_id} | Project: {inv.project_id} | Client: {inv.client_id} "
              f"| Amount: ${inv.amount:.2f} | Net: ${inv.net_amount:.2f} | Status: {inv.status}")


def update_invoice_status():
    code = input("Enter Invoice Code to update: ").strip()
    invoice = manager.find_invoice(code)
    if not invoice:
        print("Invoice not found.")
        return

    print("Status options: 1. Paid | 2. Unpaid | 3. Cancelled")
    choice = input("Select new status: ").strip()
    status_map = {"1": "Paid", "2": "Unpaid", "3": "Cancelled"}
    
    if choice in status_map:
        invoice.status = status_map[choice]
        manager.save_data()
        print(f"Invoice status updated to '{invoice.status}'.")
    else:
        print("Invalid selection.")


def invoice_management_menu():
    while True:
        print("\n--- Invoice Management ---")
        print("1. Generate Invoice")
        print("2. View All Invoices")
        print("3. Update Invoice Status")
        print("4. Back to Finance Menu")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            generate_invoice()
        elif choice == '2':
            view_invoices()
        elif choice == '3':
            update_invoice_status()
        elif choice == '4':
            break
        else:
            print("Invalid option.")


# ==========================================
# 5. PAYMENT MANAGEMENT
# ==========================================
def record_payment():
    print("\n--- Record Payment ---")
    payment_id = input("Enter Payment ID (e.g., PAY-1001): ").strip()
    invoice_code = input("Enter Invoice Code: ").strip()

    # Validation: Invoice Exists
    invoice = manager.find_invoice(invoice_code)
    if not invoice:
        print("Validation Failed: Invoice does not exist.")
        return

    try:
        amount = float(input("Enter Payment Amount: "))
        # Validation: Valid Amount (> 0)
        if amount <= 0:
            print("Validation Failed: Payment amount must be greater than zero.")
            return
    except ValueError:
        print("Invalid amount input.")
        return

    # Validation: Doesn't exceed remaining balance
    existing_payments = sum(
        p.amount for p in manager.payments 
        if p.invoice_id == invoice_code and p.status == "Completed"
    )
    remaining_balance = invoice.amount - existing_payments

    if amount > remaining_balance:
        print(f"Validation Failed: Amount exceeds remaining balance (${remaining_balance:.2f}).")
        return

    payment_method = input("Enter Payment Method (Credit Card / Bank Transfer / Paypal): ").strip()

    payment = Payment(
        payment_id=payment_id,
        invoice_id=invoice_code,
        client_id=invoice.client_id,
        amount=amount,
        payment_method=payment_method,
        status="Completed"
    )

    manager.add_payment(payment)

    # Auto-update invoice status if fully paid
    if existing_payments + amount >= invoice.amount:
        invoice.status = "Paid"

    manager.save_data()
    print(f"Payment of ${amount:.2f} recorded successfully for Invoice {invoice_code}.")


def view_payments():
    print("\n--- Payment History ---")
    if not manager.payments:
        print("No payments recorded yet.")
        return

    for p in manager.payments:
        print(f"ID: {p.payment_id} | Invoice: {p.invoice_id} | Amount: ${p.amount:.2f} "
              f"| Method: {p.payment_method} | Status: {p.status}")


def payment_management_menu():
    while True:
        print("\n--- Payment Management ---")
        print("1. Record Payment")
        print("2. View Payment History")
        print("3. Back to Finance Menu")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            record_payment()
        elif choice == '2':
            view_payments()
        elif choice == '3':
            break
        else:
            print("Invalid option.")


# ==========================================
# 6. REPORTS & DASHBOARD
# ==========================================
def payment_report():
    print("\n--- Payment Report ---")
    total_payments = len(manager.payments)
    paid = len([p for p in manager.payments if p.status == "Completed"])
    pending = len([p for p in manager.payments if p.status == "Pending"])
    failed = len([p for p in manager.payments if p.status == "Failed"])
    total_amount = sum(p.amount for p in manager.payments if p.status == "Completed")

    print(f"Total Payments: {total_payments}")
    print(f"Paid: {paid}")
    print(f"Pending: {pending}")
    print(f"Failed: {failed}")
    print(f"Total Amount Collected: ${total_amount:.2f}")


def freelancer_earnings_report():
    print("\n--- Freelancer Earnings Report ---")
    freelancers = [u for u in manager.users if isinstance(u, Freelancer)]
    if not freelancers:
        print("No freelancers found.")
        return

    for f in freelancers:
        completed_projects = len([
            p for p in manager.projects 
            if p.freelancer_id == f.user_id and p.status == "Completed"
        ])
        total_earnings = calculate_freelancer_earnings(f.user_id)
        print(f"Freelancer: {f.name} (ID: {f.user_id}) | Completed Projects: {completed_projects} | Total Earnings: ${total_earnings:.2f}")


def project_report():
    print("\n--- Project Report ---")
    active = len([p for p in manager.projects if p.status == "Active"])
    late = len([p for p in manager.projects if p.status == "Late"])
    completed = len([p for p in manager.projects if p.status == "Completed"])

    print(f"Active Projects: {active}")
    print(f"Late Projects: {late}")
    print(f"Completed Projects: {completed}")


def dashboard():
    print("\n==========================================")
    print("           FINANCIAL DASHBOARD            ")
    print("==========================================")
    total_clients = len([u for u in manager.users if isinstance(u, Client)])
    total_freelancers = len([u for u in manager.users if isinstance(u, Freelancer)])
    total_projects = len(manager.projects)
    active_projects = len([p for p in manager.projects if p.status == "Active"])
    late_projects = len([p for p in manager.projects if p.status == "Late"])
    total_invoices = len(manager.invoices)
    total_payments = len(manager.payments)
    
    total_commission = sum(
        inv.commission for inv in manager.invoices if inv.status == "Paid"
    )

    print(f"Total Clients      : {total_clients}")
    print(f"Total Freelancers  : {total_freelancers}")
    print(f"Total Projects     : {total_projects}")
    print(f"Active Projects    : {active_projects}")
    print(f"Late Projects      : {late_projects}")
    print(f"Total Invoices     : {total_invoices}")
    print(f"Total Payments     : {total_payments}")
    print(f"Total Commission   : ${total_commission:.2f}")
    print("==========================================\n")


def export_report():
    print("\n--- Exporting Financial Report ---")
    os.makedirs("reports", exist_ok=True)
    filepath = "reports/financial_summary.txt"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("FINANCIAL SUMMARY REPORT\n")
        f.write("------------------------\n")
        f.write(f"Total Invoices: {len(manager.invoices)}\n")
        f.write(f"Total Payments: {len(manager.payments)}\n")
        f.write(f"Current Commission Rate: {get_commission_rate() * 100:.1f}%\n")
    
    print(f"Report exported successfully to '{filepath}'.")


def commission_settings_menu():
    print("\n--- Commission Settings ---")
    print(f"Current Commission Rate: {get_commission_rate() * 100:.1f}%")
    try:
        new_rate = float(input("Enter new commission rate (e.g., 0.15 for 15%): "))
        set_commission_rate(new_rate)
    except ValueError:
        print("Invalid number input.")


# ==========================================
# 7. MAIN ADMIN FINANCE MENU
# ==========================================
def finance_admin_menu():
    while True:
        print("\n----------------------------------------")
        print("             Finance Menu               ")
        print("----------------------------------------")
        print("1. Invoice Management")
        print("2. Payment Management")
        print("3. Financial Reports")
        print("4. Commission Settings")
        print("5. Export Report")
        print("6. Dashboard")
        print("7. Return to Main Menu")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            invoice_management_menu()
        elif choice == '2':
            payment_management_menu()
        elif choice == '3':
            payment_report()
            freelancer_earnings_report()
            project_report()
        elif choice == '4':
            commission_settings_menu()
        elif choice == '5':
            export_report()
        elif choice == '6':
            dashboard()
        elif choice == '7':
            break
        else:
            print("Invalid choice. Please try again.")