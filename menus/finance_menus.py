import json
import os

from validators import (
    is_cancel,
    print_menu,
    print_screen,
    return_to,
    validate_project_id,
    validate_amount,
    validate_date,
    validate_commission_rate,
)

from menus.menu_helpers import (
    FINANCE_ERRORS,
    current_user_id,
    print_invoice,
    print_payment,
    print_report,
)


def invoices_menu(auth):
    user = auth.current_user
    can_update = user.role in ("Freelancer", "Admin")

    while True:
        print_menu("INVOICES MENU")
        print("[1] Generate Invoice")
        print("[2] View Invoice")

        if can_update:
            print("[3] Update Invoice")
            print("[4] Check Invoice Status")
            max_choice = 4
        else:
            print("[3] Check Invoice Status")
            max_choice = 3

        print("[0] Back")
        print("-" * 50)

        choice = input(f"\nEnter your choice (0-{max_choice}): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to(f"{user.role} Menu")
            return

        if choice == "1":
            generate_invoice_action(auth, "Invoices Menu")
        elif choice == "2":
            view_invoice_action(auth, "Invoices Menu")
        elif choice == "3" and can_update:
            update_invoice_action(auth, "Invoices Menu")
        elif (choice == "3" and not can_update) or (choice == "4" and can_update):
            invoice_status_action(auth, "Invoices Menu")
        else:
            print(
                f"\n[ERROR] Invalid choice. Please enter a value between (0-{max_choice}).\n"
            )


def payments_menu(auth):
    user = auth.current_user
    can_pay = user.role in ("Client", "Admin")

    while True:
        print_menu("PAYMENTS MENU")

        if can_pay:
            print("[1] Record Payment")
            print("[2] View Payment")
            print("[3] Payment History")
            print("[4] Payment Status")
            max_choice = 4
        else:
            print("[1] View Payment")
            print("[2] Payment History")
            print("[3] Payment Status")
            max_choice = 3

        print("[0] Back")
        print("-" * 50)

        choice = input(f"\nEnter your choice (0-{max_choice}): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to(f"{user.role} Menu")
            return

        if choice == "1" and can_pay:
            record_payment_action(auth, "Payments Menu")
        elif (choice == "2" and can_pay) or (choice == "1" and not can_pay):
            view_payment_action(auth, "Payments Menu")
        elif (choice == "3" and can_pay) or (choice == "2" and not can_pay):
            payment_history_action(auth, "Payments Menu")
        elif (choice == "4" and can_pay) or (choice == "3" and not can_pay):
            payment_status_action(auth, "Payments Menu")
        else:
            print(
                f"\n[ERROR] Invalid choice. Please enter a value between (0-{max_choice}).\n"
            )


def admin_finance_menu(auth):
    while True:
        print_menu("FINANCE & REPORTS")
        print("[1] Generate Invoice")
        print("[2] View Invoice")
        print("[3] Update Invoice")
        print("[4] Check Invoice Status")
        print("[5] Record Payment")
        print("[6] View Payment")
        print("[7] Payment History")
        print("[8] Payment Status")
        print("[9] Update Commission Rate")
        print("[10] Payment Report")
        print("[11] Freelancer Earnings Report")
        print("[12] Project Report")
        print("[13] Dashboard")
        print("[14] Export Report")
        print("[0] Back")
        print("-" * 50)

        choice = input("\nEnter your choice (0-14): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to("Admin Menu")
            return

        if choice == "1":
            generate_invoice_action(auth, "Finance & Reports")
        elif choice == "2":
            view_invoice_action(auth, "Finance & Reports")
        elif choice == "3":
            update_invoice_action(auth, "Finance & Reports")
        elif choice == "4":
            invoice_status_action(auth, "Finance & Reports")
        elif choice == "5":
            record_payment_action(auth, "Finance & Reports")
        elif choice == "6":
            view_payment_action(auth, "Finance & Reports")
        elif choice == "7":
            payment_history_action(auth, "Finance & Reports")
        elif choice == "8":
            payment_status_action(auth, "Finance & Reports")
        elif choice == "9":
            update_commission_action(auth, "Finance & Reports")
        elif choice == "10":
            show_payment_report(auth)
        elif choice == "11":
            show_freelancer_earnings_report(auth)
        elif choice == "12":
            show_project_report(auth)
        elif choice == "13":
            show_dashboard_report(auth)
        elif choice == "14":
            export_report_menu(auth)
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-14).\n")


def generate_invoice_action(auth, back_menu):
    print_screen("GENERATE INVOICE")

    project_id_input = input("Enter Project ID: ").strip()

    if is_cancel(project_id_input):
        return_to(back_menu)
        return

    due_date_input = input("Enter Due date (YYYY-MM-DD): ").strip()

    if is_cancel(due_date_input):
        return_to(back_menu)
        return

    try:
        project_id = validate_project_id(project_id_input)
        due_date = validate_date(due_date_input)
        invoice = auth.manager.generate_invoice(
            project_id, due_date, requesting_user_id=current_user_id(auth)
        )
        auth.manager.save_data(msg=False)
        print("Invoice created.")
        print_invoice(invoice, auth.manager)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def view_invoice_action(auth, back_menu):
    print_screen("VIEW INVOICE")

    code = input("Enter Invoice code: ").strip()

    if is_cancel(code):
        return_to(back_menu)
        return

    try:
        invoice = auth.manager.view_invoice(
            code.upper(), requesting_user_id=current_user_id(auth)
        )
        print_invoice(invoice, auth.manager)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def update_invoice_action(auth, back_menu):
    print_screen(
        "UPDATE INVOICE",
        hint="(Leave blank to skip a field. Type cancel, back, or n to return.)",
    )

    code = input("Enter Invoice code: ").strip()

    if is_cancel(code):
        return_to(back_menu)
        return

    new_amount = input("New amount (blank to skip): ").strip()

    if is_cancel(new_amount):
        return_to(back_menu)
        return

    new_due_date = input("New due date YYYY-MM-DD (blank to skip): ").strip()

    if is_cancel(new_due_date):
        return_to(back_menu)
        return

    try:
        amount = validate_amount(new_amount) if new_amount else None
        due_date = validate_date(new_due_date) if new_due_date else None
        invoice = auth.manager.update_invoice(
            code.upper(),
            amount=amount,
            due_date=due_date,
            requesting_user_id=current_user_id(auth),
        )
        auth.manager.save_data(msg=False)
        print("Invoice updated.")
        print_invoice(invoice, auth.manager)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def invoice_status_action(auth, back_menu):
    print_screen("INVOICE STATUS")

    code = input("Enter Invoice code: ").strip()

    if is_cancel(code):
        return_to(back_menu)
        return

    try:
        status = auth.manager.get_invoice_status(
            code.upper(), requesting_user_id=current_user_id(auth)
        )
        print(f"    Status: {status}")
        print("-" * 50)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def record_payment_action(auth, back_menu):
    print_screen("RECORD PAYMENT")

    code = input("Enter Invoice code: ").strip()

    if is_cancel(code):
        return_to(back_menu)
        return

    amount_input = input("Enter Payment amount: ").strip()

    if is_cancel(amount_input):
        return_to(back_menu)
        return

    method = input("Enter Payment method: ").strip()

    if is_cancel(method):
        return_to(back_menu)
        return

    if not method:
        print("[ERROR] Payment method cannot be empty.")
        return

    try:
        amount = validate_amount(amount_input)
        payment = auth.manager.record_payment(
            code.upper(),
            amount,
            method,
            requesting_user_id=current_user_id(auth),
        )
        auth.manager.save_data(msg=False)
        print(f"Payment recorded: {payment.payment_id}")
        print_payment(payment)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def view_payment_action(auth, back_menu):
    print_screen("VIEW PAYMENT")

    payment_id = input("Enter Payment ID: ").strip()

    if is_cancel(payment_id):
        return_to(back_menu)
        return

    try:
        payment = auth.manager.view_payment(
            payment_id.upper(), requesting_user_id=current_user_id(auth)
        )
        print_payment(payment)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def payment_history_action(auth, back_menu):
    print_screen(
        "PAYMENT HISTORY",
        hint="(Leave blank to show all. Type cancel, back, or n to return.)",
    )

    code = input("Filter by invoice code: ").strip()

    if is_cancel(code):
        return_to(back_menu)
        return

    try:
        history = auth.manager.get_payment_history(
            invoice_code=code.upper() if code else None,
            requesting_user_id=current_user_id(auth),
        )

        if not history:
            print("\nNo payments found.")
            return

        for payment in history:
            print_payment(payment)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def payment_status_action(auth, back_menu):
    print_screen("PAYMENT STATUS")

    payment_id = input("Enter Payment ID: ").strip()

    if is_cancel(payment_id):
        return_to(back_menu)
        return

    try:
        status = auth.manager.get_payment_status(
            payment_id.upper(), requesting_user_id=current_user_id(auth)
        )
        print(f"    Status: {status}")
        print("-" * 50)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def update_commission_action(auth, back_menu):
    print_screen("UPDATE COMMISSION RATE")

    rate_input = input("Enter new commission rate (0-1): ").strip()

    if is_cancel(rate_input):
        return_to(back_menu)
        return

    try:
        new_rate = validate_commission_rate(rate_input)
        auth.manager.update_commission_rate(
            new_rate, requesting_user_id=current_user_id(auth)
        )
        auth.manager.save_data(msg=False)
        print(f"Commission rate updated to {auth.manager.get_commission_rate()}")
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def show_payment_report(auth):
    try:
        print_report(
            "PAYMENT REPORT",
            auth.manager.payment_report(requesting_user_id=current_user_id(auth)),
        )
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def show_freelancer_earnings_report(auth):
    try:
        rows = auth.manager.freelancer_earnings_report(
            requesting_user_id=current_user_id(auth)
        )

        if not rows:
            print("\nNo freelancer earnings to show.")
            return

        print_screen("FREELANCER EARNINGS REPORT", hint=None)

        for row in rows:
            print(f"    Freelancer: {row['freelancer']}")
            print(f"    Completed Projects: {row['completed_projects']}")
            print(f"    Total Earnings: ${row['total_earnings']}")
            print("-" * 50)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def show_project_report(auth):
    try:
        print_report(
            "PROJECT REPORT",
            auth.manager.project_report(requesting_user_id=current_user_id(auth)),
        )
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def show_dashboard_report(auth):
    try:
        print_report(
            "DASHBOARD",
            auth.manager.dashboard_report(requesting_user_id=current_user_id(auth)),
        )
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def export_report_menu(auth):
    user = auth.current_user
    manager = auth.manager
    role = user.role
    back_menu = "Finance & Reports" if role == "Admin" else f"{role} Menu"

    while True:
        print_menu("EXPORT REPORT")
        print("[1] All Reports")

        if role == "Admin":
            print("[2] Payment Report")
            print("[3] Freelancer Earnings Report")
            print("[4] Project Report")
            print("[5] Dashboard")
        elif role == "Client":
            print("[2] My Projects")
            print("[3] My Invoices")
            print("[4] My Payments")
            print("[5] My Activity")
        else:
            print("[2] My Projects")
            print("[3] My Earnings")
            print("[4] My Invoices")
            print("[5] My Payments")

        print("[0] Back")
        print("-" * 50)

        choice = input("\nEnter your choice (0-5): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to(back_menu)
            return

        if choice not in ("1", "2", "3", "4", "5"):
            print("\n[ERROR] Invalid choice. Please enter a value between (0-5).\n")
            continue

        try:
            if role == "Admin":
                reports = {
                    "Payment Report": manager.payment_report(
                        requesting_user_id=user.user_id
                    ),
                    "Freelancer Earnings Report": manager.freelancer_earnings_report(
                        requesting_user_id=user.user_id
                    ),
                    "Project Report": manager.project_report(
                        requesting_user_id=user.user_id
                    ),
                    "Dashboard": manager.dashboard_report(
                        requesting_user_id=user.user_id
                    ),
                }
                names = {
                    "1": "all",
                    "2": "payments",
                    "3": "earnings",
                    "4": "projects",
                    "5": "dashboard",
                }
                topics = list(reports.keys())
                data = (
                    reports
                    if choice == "1"
                    else {topics[int(choice) - 2]: reports[topics[int(choice) - 2]]}
                )
            elif role == "Client":
                reports = {
                    "My Projects": [
                        p.to_dict() for p in manager.get_user_projects(user)
                    ],
                    "My Invoices": [
                        invoice.to_dict()
                        for invoice in manager.invoices
                        if invoice.client_id == user.user_id
                    ],
                    "My Payments": [
                        payment.to_dict()
                        for payment in manager.get_payment_history(
                            requesting_user_id=user.user_id
                        )
                    ],
                    "My Activity": [
                        log
                        for log in manager.audit_logs
                        if log.get("user_id") == user.user_id
                    ],
                }
                names = {
                    "1": "all",
                    "2": "projects",
                    "3": "invoices",
                    "4": "payments",
                    "5": "activity",
                }
                topics = list(reports.keys())
                data = (
                    reports
                    if choice == "1"
                    else {topics[int(choice) - 2]: reports[topics[int(choice) - 2]]}
                )
            else:
                reports = {
                    "My Projects": [
                        p.to_dict() for p in manager.get_user_projects(user)
                    ],
                    "My Earnings": manager.calculate_freelancer_earnings(
                        user.user_id, requesting_user_id=user.user_id
                    ),
                    "My Invoices": [
                        invoice.to_dict()
                        for invoice in manager.invoices
                        if invoice.freelancer_id == user.user_id
                    ],
                    "My Payments": [
                        payment.to_dict()
                        for payment in manager.get_payment_history(
                            requesting_user_id=user.user_id
                        )
                    ],
                }
                names = {
                    "1": "all",
                    "2": "projects",
                    "3": "earnings",
                    "4": "invoices",
                    "5": "payments",
                }
                topics = list(reports.keys())
                data = (
                    reports
                    if choice == "1"
                    else {topics[int(choice) - 2]: reports[topics[int(choice) - 2]]}
                )
        except FINANCE_ERRORS as error:
            print(f"[ERROR] {error}")
            continue

        if not os.path.exists("reports"):
            os.makedirs("reports")

        filepath = os.path.join("reports", f"{user.user_id}_{names[choice]}.txt")

        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)

        manager.add_audit_log(
            user.user_id,
            "REPORT_EXPORTED",
            f"User {user.user_id} exported report to {filepath}.",
        )
        manager.save_data(msg=False)
        print(f"Report saved to {filepath}")
