from validators import is_cancel, print_menu, return_to

from menus.profile_menus import profile_menu, view_earnings, view_my_activity_log
from menus.project_menus import projects_menu
from menus.milestone_menus import milestones_menu
from menus.finance_menus import (
    invoices_menu,
    payments_menu,
    admin_finance_menu,
    export_report_menu,
)
from menus.admin_menus import (
    admin_users_menu,
    admin_project_management_menu,
    admin_milestone_management_menu,
    admin_view_audit_logs,
    admin_save_data,
    admin_load_data,
)


def landing_page(auth):
    while True:
        print("\n")
        print("=" * 50)
        print("SIC FREELANCE PROJECT HUB".center(50))
        print("=" * 50)
        print("Connecting Clients & Freelancers".center(50))
        print("-" * 50)
        print("[1] Login")
        print("[2] Register")
        print("[0] Exit")
        print("-" * 50)
        choiceInput = input("\nEnter your choice (0-2): ").strip()

        if is_cancel(choiceInput) or choiceInput == "0":
            print("\nExiting...")
            return

        if choiceInput == "":
            print("\n[ERROR] Choice cannot be empty.\n")
            continue

        if not choiceInput.isdigit():
            print("\n[ERROR] Invalid choice. Please enter numbers only.\n")
            continue

        choice = int(choiceInput)

        if choice not in [1, 2]:
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


def user_home(auth):
    role = auth.current_user.role

    if role == "Client":
        client_menu(auth)
    elif role == "Freelancer":
        freelancer_menu(auth)
    elif role == "Admin":
        admin_menu(auth)


def admin_menu(auth):
    while True:
        print_menu("ADMIN MENU")
        print("[1] Profile")
        print("[2] Users")
        print("[3] Projects")
        print("[4] Milestones")
        print("[5] Finance & Reports")
        print("[6] Audit Logs")
        print("[7] View My Activity")
        print("[8] Save Data")
        print("[9] Load Data")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-9): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to("Main Menu")
            auth.logout()
            return

        if choice == "1":
            profile_menu(auth)
        elif choice == "2":
            admin_users_menu(auth)
        elif choice == "3":
            admin_project_management_menu(auth)
        elif choice == "4":
            admin_milestone_management_menu(auth)
        elif choice == "5":
            admin_finance_menu(auth)
        elif choice == "6":
            admin_view_audit_logs(auth)
        elif choice == "7":
            view_my_activity_log(auth.current_user, auth.manager)
        elif choice == "8":
            admin_save_data(auth)
        elif choice == "9":
            admin_load_data(auth)
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-9).\n")


def client_menu(auth):
    client = auth.manager.find_user(auth.current_user.user_id)

    if client is None or client.role != "Client":
        print("[ERROR] User is not a valid Client.")
        return

    while True:
        print_menu("CLIENT MENU")
        print("[1] Profile")
        print("[2] Projects")
        print("[3] Milestones")
        print("[4] Invoices")
        print("[5] Payments")
        print("[6] Reports")
        print("[7] View My Activity")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-7): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to("Main Menu")
            auth.logout()
            return

        if choice == "1":
            profile_menu(auth)

        elif choice == "2":
            projects_menu(auth, client)

        elif choice == "3":
            milestones_menu(auth, client)

        elif choice == "4":
            invoices_menu(auth)

        elif choice == "5":
            payments_menu(auth)

        elif choice == "6":
            export_report_menu(auth)

        elif choice == "7":
            view_my_activity_log(client, auth.manager)
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-7).\n")


def freelancer_menu(auth):
    freelancer = auth.manager.find_user(auth.current_user.user_id)

    if freelancer is None or freelancer.role != "Freelancer":
        print("[ERROR] User is not a valid Freelancer.")
        return

    while True:
        print_menu("FREELANCER MENU")
        print("[1] Profile")
        print("[2] Projects")
        print("[3] Milestones")
        print("[4] Invoices")
        print("[5] Payments")
        print("[6] Reports")
        print("[7] View Earnings")
        print("[8] View My Activity")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-8): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to("Main Menu")
            auth.logout()
            return

        if choice == "1":
            profile_menu(auth)
        elif choice == "2":
            projects_menu(auth, freelancer)
        elif choice == "3":
            milestones_menu(auth, freelancer)
        elif choice == "4":
            invoices_menu(auth)
        elif choice == "5":
            payments_menu(auth)
        elif choice == "6":
            export_report_menu(auth)
        elif choice == "7":
            view_earnings(freelancer, auth)
        elif choice == "8":
            view_my_activity_log(freelancer, auth.manager)

        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-8).\n")
