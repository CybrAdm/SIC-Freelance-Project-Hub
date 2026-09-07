from classes import Milestone, MissingFreelancerError, Project, ProjectIterator
from manager import MAX_ACTIVE_PROJECTS, count_active_projects
from validators import (
    is_cancel,
    validate_user_id,
    validate_project_id,
    validate_milestone_id,
    validate_priority,
    validate_status,
    validate_name,
    validate_email,
    validate_phone,
    validate_city,
    validate_password,
    validate_company_name,
    validate_skills,
    validate_hourly_rate,
    validate_amount,
    validate_date,
)


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


def user_home(auth):
    role = auth.current_user.role

    if role == "Client":
        client_menu(auth)
    elif role == "Freelancer":
        freelancer_menu(auth)
    elif role == "Admin":
        admin_menu(auth)


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


def admin_menu(auth):
    while True:
        print("\n" + "=" * 50)
        print("                 ADMIN MENU")
        print("=" * 50)
        print("[1] View profile")
        print("[2] View all users")
        print("[3] View all projects")
        print("[4] View Audit Logs")
        print("[5] Toggle User Status")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-5): ").strip()

        if choice == "1":
            print(auth.current_user.profile_summary())
        elif choice == "2":
            print_users(auth.manager.users)
        elif choice == "3":
            print_projects(auth.manager.projects)
        elif choice == "4":
            admin_view_audit_logs(auth)
        elif choice == "5":
            toggle_user_status(auth)
        elif choice == "0":
            auth.logout()
            return
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-5).\n")


def admin_view_audit_logs(auth):
    logs = auth.manager.audit_logs

    if not logs:
        print("\nNo audit logs yet.")
        return

    print("\n" + "-" * 60)
    print("                     AUDIT LOGS")
    print("-" * 60)

    filter_choice = (
        input("Filter by User ID (or press Enter to show all): ").strip().upper()
    )

    filtered_logs = []

    if filter_choice:
        for log in logs:
            if log["user_id"] == filter_choice:
                filtered_logs.append(log)
    else:
        filtered_logs = logs

    if not filtered_logs:
        print("\nNo audit logs found for this User ID.")
        return

    for counter, log in enumerate(filtered_logs, 1):
        print(f"[{counter}] {log['timestamp']} | {log['user_id']} | {log['action']}")
        print(f"    {log['description']}")
        print("-" * 60)


def toggle_user_status(auth):
    print("\n" + "-" * 50)
    print("           ACTIVATE / DEACTIVATE USER")
    print("-" * 50)

    user_id_input = input("Enter User ID (or CANCEL to go back): ")

    if is_cancel(user_id_input):
        print("\nCancelled.")
        return

    try:
        validate_user_id(user_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    user_id = user_id_input.strip().upper()
    user = auth.manager.find_user(user_id)

    if user is None:
        print("[ERROR] User not found.")
        return

    if user.user_id == auth.current_user.user_id:
        print("[ERROR] You cannot deactivate your own account.")
        return

    current_status = "Active" if user.active else "Inactive"
    new_status = not user.active

    confirm = (
        input(
            f"User '{user.name}' is currently {current_status}. "
            f"Change to {'Active' if new_status else 'Inactive'}? (y/n): "
        )
        .strip()
        .lower()
    )

    if confirm != "y":
        print("\nCancelled.")
        return

    user.active = new_status

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "USER_STATUS_CHANGED",
        f"Admin {auth.current_user.user_id} set {user.user_id} status to "
        f"{'Active' if new_status else 'Inactive'}.",
    )

    auth.manager.save_data()
    print(f"User '{user.name}' is now {'Active' if new_status else 'Inactive'}.")


def client_menu(auth):
    client = auth.manager.find_user(auth.current_user.user_id)

    if client is None or client.role != "Client":
        print("[ERROR] User is not a valid Client.")
        return

    while True:
        print("\n" + "=" * 50)
        print("                 CLIENT MENU")
        print("=" * 50)
        print("[1] Profile")
        print("[2] Projects")
        print("[3] Milestones")
        print("[4] Invoices")
        print("[5] Payments")
        print("[6] View My Activity")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-6): ").strip()

        if choice == "1":
            profile_menu(auth)

        elif choice == "2":
            projects_menu(auth, client)

        elif choice == "3":
            milestones_menu(auth, client)

        elif choice == "4":
            ...

        elif choice == "5":
            ...

        elif choice == "6":
            view_my_activity_log(client, auth.manager)

        elif choice == "0":
            auth.logout()
            return
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-6).\n")


def freelancer_menu(auth):
    freelancer = auth.manager.find_user(auth.current_user.user_id)

    if freelancer is None or freelancer.role != "Freelancer":
        print("[ERROR] User is not a valid Freelancer.")
        return

    while True:
        print("\n" + "=" * 50)
        print("               FREELANCER MENU")
        print("=" * 50)
        print("[1] Profile")
        print("[2] Projects")
        print("[3] Milestones")
        print("[4] Invoices")
        print("[5] Payments")
        print("[6] View Earnings")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-6): ").strip()

        if choice == "1":
            profile_menu(auth)
        elif choice == "2":
            projects_menu(auth, freelancer)
        elif choice == "3":
            milestones_menu(auth, freelancer)
        elif choice == "4":
            ...
        elif choice == "5":
            ...
        elif choice == "6":
            view_earnings(freelancer)
        elif choice == "0":
            auth.logout()
            return
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-6).\n")


def profile_menu(auth):
    while True:
        print("\n" + "=" * 50)
        print("                 PROFILE")
        print("=" * 50)
        print("[1] View profile")
        print("[2] Update profile")
        print("[0] Back to previous menu")
        print("-" * 50)

        sub_choice = input("\nEnter your choice (0-2): ").strip()

        if sub_choice == "1":
            print(auth.current_user.profile_summary())
        elif sub_choice == "2":
            update_profile(auth.current_user, auth.manager)
        elif sub_choice == "0":
            break
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-2).\n")


def update_profile(current_user, manager):

    print("\n" + "=" * 50)
    print("                 UPDATE PROFILE")
    print("=" * 50)
    print("[1] Update Name")
    print("[2] Update Email")
    print("[3] Update Phone Number")
    print("[4] Update City")
    print("[5] Reset Password")

    if current_user.role == "Client":
        print("[6] Update Company Name")
        max_choice = 6
    elif current_user.role == "Freelancer":
        print("[6] Add New Skill")
        print("[7] Update Hourly Rate")
        max_choice = 7
    else:
        max_choice = 5

    print("[0] Back to Profile Menu")
    print("-" * 50)
    print("(Type cancel at any time to cancel the operation)")
    print("-" * 50)

    sub_choice = input(f"Enter your choice (0-{max_choice}): ").strip()

    if sub_choice == "0":
        return

    elif sub_choice == "1":
        new_name = input("Enter new name: ").strip()

        if is_cancel(new_name):
            print("\nUpdate cancelled.")
            return

        try:
            current_user.name = validate_name(new_name)
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated name.",
            )
            manager.save_data()
            print("Name updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "2":
        new_email = input("Enter new email: ")

        if is_cancel(new_email):
            print("\nUpdate cancelled.")
            return

        try:
            email = validate_email(new_email)
            found_user = manager.find_email(email)

            if found_user is not None and found_user.user_id != current_user.user_id:
                print("[ERROR] This email is already registered.")
                return

            current_user.email = email
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated email.",
            )
            manager.save_data()
            print("Email updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "3":
        new_phone = input("Enter new phone number: ")

        if is_cancel(new_phone):
            print("\nUpdate cancelled.")
            return

        try:
            phone = validate_phone(new_phone)
            found_user = manager.find_phone(phone)

            if found_user is not None and found_user.user_id != current_user.user_id:
                print("[ERROR] This phone number is already registered.")
                return

            current_user.phone = phone
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated phone number.",
            )
            manager.save_data()
            print("Phone number updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "4":
        new_city = input("Enter new city: ")

        if is_cancel(new_city):
            print("\nUpdate cancelled.")
            return

        try:
            city = validate_city(new_city)
            current_user.city = city
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated city.",
            )
            manager.save_data()
            print("City updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "5":
        new_password = input("Enter new password: ").strip()

        if is_cancel(new_password):
            print("\nUpdate cancelled.")
            return

        confirm_password = input("Confirm new password: ").strip()

        if is_cancel(confirm_password):
            print("\nUpdate cancelled.")
            return

        try:
            new_password = validate_password(new_password)

            if new_password != confirm_password.strip():
                raise ValueError("Passwords do not match.")

            current_user.password = new_password
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} reset password.",
            )
            manager.save_data()
            print("Password reset successfully!")

        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "6" and current_user.role == "Client":
        new_company = input("Enter new company name: ").strip()

        if is_cancel(new_company):
            print("\nUpdate cancelled.")
            return

        try:
            company_name = validate_company_name(new_company)
            current_user.company_name = company_name
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated company name.",
            )
            manager.save_data()
            print("Company name updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "6" and current_user.role == "Freelancer":
        new_skills_input = input("Enter new skill(s) (comma-separated): ")

        if is_cancel(new_skills_input):
            print("\nUpdate cancelled.")
            return

        try:
            new_skills = validate_skills(new_skills_input)
            added_skills = []

            for skill in new_skills:
                existing_skills = [s.lower() for s in current_user.skills]
                if skill.lower() not in existing_skills:
                    current_user.skills.append(skill)
                    added_skills.append(skill)

            if not added_skills:
                print("[ERROR] Skill(s) already exist in your profile.")
                return

            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} added skill(s).",
            )
            manager.save_data()
            print("Skill(s) added successfully!")
        except ValueError as e:
            print(f"[ERROR] {e}")

    elif sub_choice == "7" and current_user.role == "Freelancer":
        new_rate_input = input("Enter new hourly rate ($): ")

        if is_cancel(new_rate_input):
            print("\nUpdate cancelled.")
            return

        try:
            current_user.hourly_rate = validate_hourly_rate(new_rate_input)
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated hourly rate.",
            )
            manager.save_data()
            print("Hourly rate updated successfully!")
        except ValueError as e:
            print(f"[ERROR] {e}")

    else:
        print("[ERROR] Invalid choice.")


def view_earnings(freelancer):
    print(f"\nTotal Earnings: ${freelancer.earnings}")


def view_my_activity_log(user, manager):
    logs = []

    for log in manager.audit_logs:
        if log["user_id"] == user.user_id:
            logs.append(log)

    if not logs:
        print("\nNo activity recorded yet.")
        return

    print("\n" + "-" * 60)
    print("                 MY ACTIVITY LOG")
    print("-" * 60)

    for counter, log in enumerate(logs, 1):
        print(f"[{counter}] {log['timestamp']} | {log['action']}")
        print(f"    {log['description']}")
        print("-" * 60)


def projects_menu(auth, user):
    while True:
        print("\n" + "=" * 50)
        print("               PROJECTS MENU")
        print("=" * 50)

        if user.role == "Client":
            print("[1] Create Project")
            print("[2] My Projects")
            print("[3] View Project Details")
            print("[4] Update Project")
            print("[5] Assign Freelancer")
            print("[6] Browse Freelancers")
            print("[7] View Assigned Freelancer")
            print("[8] Active Projects")
            print("[9] Late Projects")
            print("[10] Sort Projects")
            print("[11] Remove Project")
            max_choice = 11
        else:
            print("[1] Browse Projects")
            print("[2] My Projects")
            print("[3] View Project Details")
            print("[4] Choose Project")
            print("[5] Active Projects")
            print("[6] Late Projects")
            print("[7] Sort Projects")
            print("[8] Withdraw Project")
            max_choice = 8

        print("[0] Back to previous menu")
        print("-" * 50)

        choice = input(f"\nEnter your choice (0-{max_choice}): ").strip()

        if choice == "1":
            if user.role == "Client":
                create_project(user, auth.manager)
            else:
                print_projects(auth.manager.get_available_projects(user))
        elif choice == "2":
            user_projects = auth.manager.get_user_projects(user)
            print_projects(user_projects)
        elif choice == "3":
            view_project_details(user, auth.manager)
        elif choice == "4":
            if user.role == "Client":
                update_project(user, auth.manager)
            else:
                choose_project(user, auth.manager)
        elif choice == "5":
            if user.role == "Client":
                assign_freelancer(user, auth.manager)
            else:
                print_projects(auth.manager.get_active_projects(user))
        elif choice == "6":
            if user.role == "Client":
                browse_freelancers(user, auth.manager)
            else:
                print_projects(auth.manager.get_late_projects(user))
        elif choice == "7":
            if user.role == "Client":
                view_assigned_freelancer(user, auth.manager)
            else:
                sort_projects_menu(user, auth.manager)
        elif choice == "8":
            if user.role == "Client":
                print_projects(auth.manager.get_active_projects(user))
            else:
                withdraw_from_project(user, auth.manager)
        elif choice == "9":
            if user.role == "Client":
                print_projects(auth.manager.get_late_projects(user))
        elif choice == "10" and user.role == "Client":
            sort_projects_menu(user, auth.manager)
        elif choice == "11" and user.role == "Client":
            delete_project(user, auth.manager)
        elif choice == "0":
            print(f"\nReturning to {user.role} Menu...")
            return
        else:
            print(
                f"\n[ERROR] Invalid choice. Please enter a value between (0-{max_choice}).\n"
            )


def create_project(client, manager):
    print("\n" + "-" * 50)
    print("               CREATE PROJECT")
    print("-" * 50)
    print("(Type cancel at any time to cancel the operation)")
    print("-" * 50)

    while True:
        project_id_input = input("Enter Project ID (e.g. P001): ").strip()

        if is_cancel(project_id_input):
            print("\nCancelled.")
            return

        try:
            project_id = validate_project_id(project_id_input)
        except ValueError as e:
            print(f"[ERROR] {e}")
            continue

        if manager.find_project(project_id) is not None:
            print("\n[ERROR] This Project ID already exists.\n")
        else:
            break

    while True:
        title = input("Enter Project Title: ").strip()

        if is_cancel(title):
            print("\nCancelled.")
            return

        if title:
            break

        print("[ERROR] Title cannot be empty.")

    while True:
        description = input("Enter Project Description: ").strip()

        if is_cancel(description):
            print("\nCancelled.")
            return

        if description:
            break

        print("[ERROR] Description cannot be empty.")

    while True:
        budget_input = input("Enter Budget ($): ").strip()

        if is_cancel(budget_input):
            print("\nCancelled.")
            return

        try:
            budget = validate_amount(budget_input)
            break
        except ValueError as e:
            print(f"[ERROR] {e}")

    while True:
        deadline_input = input("Enter Deadline (YYYY-MM-DD): ").strip()

        if is_cancel(deadline_input):
            print("\nCancelled.")
            return

        try:
            deadline = validate_date(deadline_input)
            break
        except ValueError as e:
            print(f"[ERROR] {e}")

    while True:
        priority_input = input("Enter Priority (Low/Medium/High): ").strip()

        if is_cancel(priority_input):
            print("\nCancelled.")
            return

        try:
            priority = validate_priority(priority_input)
            break
        except ValueError as e:
            print(f"[ERROR] {e}")

    while True:
        skills_input = input(
            "Enter required skills (comma-separated, or leave empty): "
        )

        if is_cancel(skills_input):
            print("\nCancelled.")
            return

        if not skills_input.strip():
            required_skills = []
            break

        try:
            required_skills = validate_skills(skills_input)
            break
        except ValueError as e:
            print(f"[ERROR] {e}")

    new_project = Project(
        project_id,
        title,
        description,
        client.user_id,
        "",
        budget,
        deadline,
        required_skills,
        "Open",
        priority,
    )

    manager.add_project(new_project)
    client.project_ids.append(project_id)

    manager.add_audit_log(
        client.user_id,
        "PROJECT_CREATED",
        f"Client {client.user_id} created project {project_id}.",
    )

    manager.save_data()
    print(f"Project '{title}' (ID: {project_id}) created successfully.")


def view_project_details(user, manager):
    while True:
        proj_id = input("Enter Project ID for details (or CANCEL to go back): ")

        if is_cancel(proj_id):
            print(f"\nReturning to {user.role} Menu...")
            return

        try:
            proj_id = validate_project_id(proj_id)
        except ValueError as e:
            print(f"[ERROR] {e}")
            continue

        project = manager.find_project(proj_id)

        if project is None:
            print("[ERROR] Project not found.")
        else:
            if user.role == "Client":
                owns = project.client_id == user.user_id
                error_msg = "[ERROR] This project does not belong to you."
            else:
                owns = project.freelancer_id == user.user_id
                error_msg = "[ERROR] This project is not assigned to you."

            if not owns:
                print(error_msg)
            else:
                print(f"\n--- Project Details ---")
                print(f"    ID: {project.project_id}")
                print(f"    Title: {project.title}")
                print(f"    Description: {project.description}")
                print(f"    Client ID: {project.client_id}")
                freelancer_info = (
                    project.freelancer_id if project.freelancer_id else "Unassigned"
                )
                print(f"    Freelancer ID: {freelancer_info}")
                print(
                    f"    Required Skills: {', '.join(project.required_skills) if project.required_skills else 'None'}"
                )
                print(f"    Status: {project.status}")
                print(f"    Priority: {project.priority}")
                print(f"    Health: {project.get_health()}")
                print(f"    Budget: {project.budget}")
                print(f"    Deadline: {project.deadline}")
                print(f"    Milestones: {project.milestones}")

        while True:
            again = input("\nView another project? (y/n): ").strip().lower()

            if again == "y":
                break
            elif again == "n":
                return
            else:
                print("[ERROR] Please enter 'y' or 'n'.")


def update_project(client, manager):
    print("\n" + "-" * 50)
    print("               UPDATE PROJECT")
    print("-" * 50)
    print("(Leave empty to keep the current value. Type cancel to stop.)")
    print("-" * 50)

    project_id_input = input("Enter Project ID to update: ").strip()

    if is_cancel(project_id_input):
        print("\nCancelled.")
        return

    try:
        project_id = validate_project_id(project_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    project = manager.find_project(project_id)

    if project is None or project.client_id != client.user_id:
        print("[ERROR] Project not found or not assigned to you.")
        return

    new_title = input(f"New Title [{project.title}]: ").strip()

    if is_cancel(new_title):
        print("\nCancelled.")
        return

    new_desc = input(f"New Description [{project.description}]: ").strip()

    if is_cancel(new_desc):
        print("\nCancelled.")
        return

    new_budget = input(f"New Budget [${project.budget}]: ").strip()

    if is_cancel(new_budget):
        print("\nCancelled.")
        return

    budget = project.budget

    if new_budget:
        try:
            budget = validate_amount(new_budget)

            existing_total = round(
                sum(
                    milestone.amount
                    for milestone in manager.get_project_milestones(project.project_id)
                ),
                2,
            )

            if budget < existing_total:
                print(
                    f"[ERROR] Budget cannot be less than existing milestone total "
                    f"(${existing_total}). Kept previous budget."
                )
                budget = project.budget
        except ValueError as e:
            print(f"[ERROR] {e} Kept previous value.")
            budget = project.budget

    new_deadline = input(f"New Deadline (YYYY-MM-DD) [{project.deadline}]: ").strip()

    if is_cancel(new_deadline):
        print("\nCancelled.")
        return

    deadline = project.deadline

    if new_deadline:
        try:
            deadline = validate_date(new_deadline)
        except ValueError as e:
            print(f"[ERROR] {e} Kept previous deadline.")

    new_status = input(
        f"New Status (Open/Pending/In Progress/Completed) [{project.status}]: "
    ).strip()

    if is_cancel(new_status):
        print("\nCancelled.")
        return

    status = project.status
    unassign_freelancer = False

    if new_status:
        try:
            status = validate_status(new_status)
            if status == "Open" and project.freelancer_id:
                unassign_freelancer = True
        except ValueError as e:
            print(f"[ERROR] {e} Kept previous status.")
            status = project.status

    new_priority = input(
        f"New Priority (Low/Medium/High) [{project.priority}]: "
    ).strip()

    if is_cancel(new_priority):
        print("\nCancelled.")
        return

    priority = project.priority

    if new_priority:
        try:
            priority = validate_priority(new_priority)
        except ValueError as e:
            print(f"[ERROR] {e} Kept previous priority.")
            priority = project.priority

    if new_title:
        project.title = new_title

    if new_desc:
        project.description = new_desc

    project.budget = budget
    project.deadline = deadline
    project.status = status
    project.priority = priority

    if unassign_freelancer and project.freelancer_id:
        freelancer = manager.find_user(project.freelancer_id)
        if freelancer is not None and project.project_id in freelancer.project_ids:
            freelancer.project_ids.remove(project.project_id)
        project.freelancer_id = ""

    manager.add_audit_log(
        client.user_id,
        "PROJECT_UPDATED",
        f"Client {client.user_id} updated project {project.project_id}.",
    )

    manager.save_data()
    print("Project updated successfully.")


def assign_freelancer(client, manager):
    print("\n" + "-" * 50)
    print("               ASSIGN FREELANCER")
    print("-" * 50)

    project_id_input = input("Enter Project ID (or CANCEL to go back): ")

    if is_cancel(project_id_input):
        print("\nCancelled.")
        return

    try:
        project_id = validate_project_id(project_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    project = manager.find_project(project_id)

    if project is None or project.client_id != client.user_id:
        print("[ERROR] Project not found or not assigned to you.")
        return

    if project.status != "Open":
        print("[ERROR] This project is not available for assignment.")
        return

    if project.freelancer_id:
        print("[ERROR] This project already has an assigned freelancer.")
        return

    freelancer_id_input = input("Enter Freelancer ID (or CANCEL to go back): ")

    if is_cancel(freelancer_id_input):
        print("\nCancelled.")
        return

    try:
        validate_user_id(freelancer_id_input, expected_role="Freelancer")
        freelancer_id = freelancer_id_input.strip().upper()

        freelancer = manager.find_user(freelancer_id)

        if freelancer is None or freelancer.role != "Freelancer":
            raise MissingFreelancerError(
                f"Freelancer with ID '{freelancer_id}' does not exist."
            )

        if not freelancer.active:
            print("[ERROR] This freelancer account is inactive.")
            return

        active_count = count_active_projects(freelancer.user_id, manager)

        if active_count >= MAX_ACTIVE_PROJECTS:
            print(
                f"[ERROR] This freelancer already has {active_count} active projects."
            )
            return

        if project.required_skills and not any(
            skill.lower() in [s.lower() for s in freelancer.skills]
            for skill in project.required_skills
        ):
            print("[ERROR] This freelancer does not have the required skills.")
            return

        project.freelancer_id = freelancer.user_id
        project.status = "Pending"

        if project.project_id not in freelancer.project_ids:
            freelancer.project_ids.append(project.project_id)

        manager.add_audit_log(
            client.user_id,
            "FREELANCER_ASSIGNED",
            f"Client {client.user_id} assigned {freelancer.user_id} "
            f"to project {project.project_id}.",
        )

        manager.save_data()
        print(f"Freelancer '{freelancer.name}' assigned to project '{project.title}'.")

    except MissingFreelancerError as e:
        print(f"[ERROR] {e}")
    except ValueError as e:
        print(f"[ERROR] {e}")


def browse_freelancers(client, manager):
    print("\n" + "-" * 50)
    print("               BROWSE FREELANCERS")
    print("-" * 50)

    project_id_input = input(
        "Enter Project ID to match freelancers (or CANCEL to go back): "
    )

    if is_cancel(project_id_input):
        print("\nCancelled.")
        return

    try:
        project_id = validate_project_id(project_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    project = manager.find_project(project_id)

    if project is None or project.client_id != client.user_id:
        print("[ERROR] Project not found or not assigned to you.")
        return

    if project.freelancer_id:
        print("[ERROR] This project already has an assigned freelancer.")
        return

    matches = []

    for user in manager.users:

        if user.role != "Freelancer":
            continue

        if not user.active:
            continue

        active_count = count_active_projects(user.user_id, manager)

        if active_count >= MAX_ACTIVE_PROJECTS:
            continue

        if project.required_skills:
            user_skills = []
            for skill in user.skills:
                user_skills.append(skill.lower())

            has_skill = False
            for required_skill in project.required_skills:
                if required_skill.lower() in user_skills:
                    has_skill = True
                    break

            if not has_skill:
                continue

        matches.append(user)

    if not matches:
        print("\nNo available freelancers match this project's requirements.")
        return

    print(f"\n--- Matching Freelancers for '{project.title}' ---")

    for counter, freelancer in enumerate(matches, 1):
        skills = ", ".join(freelancer.skills)
        active_count = count_active_projects(freelancer.user_id, manager)
        print(f"[{counter}] ID: {freelancer.user_id}")
        print(f"    Name: {freelancer.name}")
        print(f"    Skills: {skills}")
        print(f"    Hourly Rate: {freelancer.hourly_rate}")
        print(f"    Active Projects: {active_count}/{MAX_ACTIVE_PROJECTS}")
        print("-" * 50)


def view_assigned_freelancer(client, manager):

    project_id_input = input("Enter Project ID (or CANCEL to go back): ")

    if is_cancel(project_id_input):
        print("\nCancelled.")
        return

    try:
        project_id = validate_project_id(project_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    project = manager.find_project(project_id)

    if project is None or project.client_id != client.user_id:
        print("[ERROR] Project not found or not assigned to you.")
        return

    if not project.freelancer_id:
        print("[ERROR] No freelancer assigned to this project yet.")
        return

    freelancer = manager.find_user(project.freelancer_id)

    if freelancer is None:
        print("[ERROR] Assigned freelancer could not be found.")
        return

    skills = ", ".join(freelancer.skills)

    print(f"""
            Assigned Freelancer
            --------------------
            ID: {freelancer.user_id}
            Name: {freelancer.name}
            Email: {freelancer.email}
            Phone: {freelancer.phone}
            Skills: {skills}
            Hourly Rate: {freelancer.hourly_rate}
            Status: {"Active" if freelancer.active else "Inactive"}
            """)


def choose_project(freelancer, manager):
    proj_id = input("Enter Project ID (or CANCEL to go back): ")

    if is_cancel(proj_id):
        print("\nCancelled.")
        return

    try:
        proj_id = validate_project_id(proj_id)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    project = manager.find_project(proj_id)

    active_count = count_active_projects(freelancer.user_id, manager)

    if project is None:
        print("[ERROR] Project not found.")
    elif project.freelancer_id:
        print("[ERROR] This project already has an assigned freelancer.")
    elif project.status != "Open":
        print("[ERROR] This project is not available for selection.")
    elif active_count >= MAX_ACTIVE_PROJECTS:
        print(
            f"[ERROR] You already have {active_count} active projects. "
            f"Complete one before choosing a new project."
        )
    elif project.required_skills and not any(
        skill.lower() in [s.lower() for s in freelancer.skills]
        for skill in project.required_skills
    ):
        print("[ERROR] You don't have the required skills for this project.")
    else:
        project.freelancer_id = freelancer.user_id
        project.status = "Pending"
        if project.project_id not in freelancer.project_ids:
            freelancer.project_ids.append(project.project_id)

        manager.add_audit_log(
            freelancer.user_id,
            "PROJECT_CHOSEN",
            f"Freelancer chose project {project.project_id}.",
        )

        manager.save_data()

        print("Project chosen successfully!")


def sort_projects_menu(user, manager):
    user_projects = manager.get_user_projects(user)

    if not user_projects:
        print("\nNo projects yet.")
        return

    print("\n" + "=" * 50)
    print("               SORT PROJECTS")
    print("=" * 50)
    print("[1] Sort by Deadline")
    print("[2] Sort by Budget (highest first)")
    print("[3] Sort by Priority")
    print("[0] Back")
    print("-" * 50)

    choice = input("\nEnter your choice (0-3): ").strip()

    if choice == "1":
        print_projects(manager.sort_projects_by_deadline(user_projects))
    elif choice == "2":
        print_projects(manager.sort_projects_by_budget(user_projects))
    elif choice == "3":
        print_projects(manager.sort_projects_by_priority(user_projects))
    elif choice == "0":
        return
    else:
        print("\n[ERROR] Invalid choice. Please enter a value between (0-3).\n")


def delete_project(client, manager):
    print("\n" + "-" * 50)
    print("               REMOVE PROJECT")
    print("-" * 50)

    project_id_input = input("Enter Project ID to delete (or CANCEL to go back): ")

    if is_cancel(project_id_input):
        print("\nCancelled.")
        return

    try:
        project_id = validate_project_id(project_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    project = manager.find_project(project_id)

    if project is None or project.client_id != client.user_id:
        print("[ERROR] Project not found or not assigned to you.")
        return

    confirm = (
        input(f"Are you sure you want to delete '{project.title}'? (y/n): ")
        .strip()
        .lower()
    )

    if confirm != "y":
        print("\nDeletion cancelled.")
        return

    manager.projects = [p for p in manager.projects if p.project_id != project_id]
    manager.milestones = [m for m in manager.milestones if m.project_id != project_id]

    if project_id in client.project_ids:
        client.project_ids.remove(project_id)

    if project.freelancer_id:
        freelancer = manager.find_user(project.freelancer_id)
        if freelancer is not None and project_id in freelancer.project_ids:
            freelancer.project_ids.remove(project_id)

    manager.add_audit_log(
        client.user_id,
        "PROJECT_DELETED",
        f"Client {client.user_id} deleted project {project_id}.",
    )

    manager.save_data()
    print(f"Project '{project_id}' deleted successfully.")


def withdraw_from_project(freelancer, manager):

    project_id_input = input(
        "Enter Project ID to withdraw from (or CANCEL to go back): "
    )

    if is_cancel(project_id_input):
        print("\nCancelled.")
        return

    try:
        project_id = validate_project_id(project_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    project = manager.find_project(project_id)

    if project is None or project.freelancer_id != freelancer.user_id:
        print("[ERROR] Project not found or not assigned to you.")
        return

    if project.status not in ("Pending", "In Progress"):
        print(
            f"[ERROR] You cannot withdraw from a project with status '{project.status}'."
        )
        return

    confirm = (
        input(f"Are you sure you want to withdraw from '{project.title}'? (y/n): ")
        .strip()
        .lower()
    )

    if confirm != "y":
        print("\nWithdrawal cancelled.")
        return

    old_status = project.status

    project.freelancer_id = ""
    project.status = "Open"

    if project.project_id in freelancer.project_ids:
        freelancer.project_ids.remove(project.project_id)

    for milestone in manager.get_project_milestones(project.project_id):
        if milestone.status not in ("Approved", "Paid"):
            milestone.update_status("Pending")

    manager.add_audit_log(
        freelancer.user_id,
        "PROJECT_WITHDRAWN",
        f"Freelancer {freelancer.user_id} withdrew from project {project.project_id} "
        f"(was {old_status}).",
    )

    manager.save_data()

    print(f"You have withdrawn from '{project.title}'. The project is now Open again.")


def milestones_menu(auth, user):
    while True:
        print("\n" + "=" * 50)
        print("               MILESTONES MENU")
        print("=" * 50)

        print("[1] My Milestones")
        print("[2] Milestone Details")

        if user.role == "Client":
            print("[3] Add Milestone")
            print("[4] Review Milestone (Approve/Reject)")
            print("[5] Milestone History")
            max_choice = 5
        else:
            print("[3] Update Milestone")
            print("[4] Milestone History")
            max_choice = 4

        print("[0] Back")
        print("-" * 50)

        choice = input(f"\nEnter your choice (0-{max_choice}): ").strip()

        if choice == "1":
            my_milestones(user, auth.manager)
        elif choice == "2":
            milestone_details(user, auth.manager)
        elif choice == "3":
            if user.role == "Client":
                add_milestone(user, auth.manager)
            else:
                update_milestone(user, auth.manager)
        elif choice == "4":
            if user.role == "Client":
                review_milestone(user, auth.manager)
            else:
                view_milestone_history(user, auth.manager)
        elif choice == "5" and user.role == "Client":
            view_milestone_history(user, auth.manager)
        elif choice == "0":
            print(f"\nReturning to {user.role} Menu...")
            return
        else:
            print(
                f"\n[ERROR] Invalid choice. Please enter a value between (0-{max_choice}).\n"
            )


def my_milestones(user, manager):
    user_projects = manager.get_user_projects(user)
    milestones = []

    for project in user_projects:
        project_milestones = manager.get_project_milestones(project.project_id)
        milestones.extend(project_milestones)

    if not milestones:
        print("\nNo milestones yet.")
        return

    print("\n" + "-" * 50)
    print("                 MILESTONES")
    print("-" * 50)

    for counter, milestone in enumerate(milestones, 1):
        print(f"[{counter}] ID: {milestone.milestone_id}")
        print(f"    Project ID: {milestone.project_id}")
        print(f"    Title: {milestone.title}")
        print(f"    Description: {milestone.description}")
        print(f"    Amount: {milestone.amount}")
        print(f"    Deadline: {milestone.deadline}")
        print(f"    Status: {milestone.status}")
        print(f"    History: {milestone.history}")
        print("-" * 50)


def milestone_details(user, manager):
    while True:

        ms_id = input("Enter Milestone ID for details (or CANCEL to go back): ")

        if is_cancel(ms_id):
            print(f"\nReturning to {user.role} Menu...")
            return

        ms_id = ms_id.strip().upper()

        milestone = manager.find_milestone(ms_id)

        if milestone is None:
            print("[ERROR] Milestone not found.")
        else:
            project = manager.find_project(milestone.project_id)

            if user.role == "Client":
                owns = project is not None and project.client_id == user.user_id
                error_msg = (
                    "[ERROR] This milestone does not belong to one of your projects."
                )
            else:
                owns = project is not None and project.freelancer_id == user.user_id
                error_msg = "[ERROR] This milestone is not assigned to you."

            if not owns:
                print(error_msg)
            else:
                print(f"\n--- Milestone Details: {milestone.title} ---")
                print(f"Description: {milestone.description}")
                print(f"Project ID: {milestone.project_id}")
                print(f"Amount: ${milestone.amount}")
                print(f"Deadline: {milestone.deadline}")
                print(f"Status: {milestone.status}")

                history = milestone.history
                if not history:
                    print("History: No status change history recorded yet.")
                else:
                    print("History:")
                    for idx, entry in enumerate(history, 1):
                        timestamp = entry.get("timestamp", "Unknown time")
                        print(
                            f"    {idx}. {entry.get('old_status')} -> {entry.get('new_status')} "
                            f"({timestamp})"
                        )

        while True:

            again = input("\nView another milestone? (y/n): ").strip().lower()

            if again == "y":
                break
            elif again == "n":
                return
            else:
                print("[ERROR] Please enter 'y' or 'n'.")


def add_milestone(client, manager):
    print("\n" + "-" * 50)
    print("               ADD MILESTONE")
    print("-" * 50)
    print("(Type cancel at any time to cancel the operation)")
    print("-" * 50)

    while True:
        project_id_input = input("Enter Project ID: ").strip()

        if is_cancel(project_id_input):
            print("\nCancelled.")
            return

        try:
            project_id = validate_project_id(project_id_input)
        except ValueError as e:
            print(f"[ERROR] {e}")
            continue

        project = manager.find_project(project_id)

        if project is None or project.client_id != client.user_id:
            print("[ERROR] Project not found or not assigned to you.")
            continue

        break

    while True:
        ms_id_input = input("Enter Milestone ID: ").strip()

        if is_cancel(ms_id_input):
            print("\nCancelled.")
            return

        try:
            ms_id = validate_milestone_id(ms_id_input)
        except ValueError as e:
            print(f"[ERROR] {e}")
            continue

        if manager.find_milestone(ms_id) is not None:
            print("\n[ERROR] This Milestone ID already exists.\n")
        else:
            break

    while True:
        title = input("Enter Milestone Title: ").strip()

        if is_cancel(title):
            print("\nCancelled.")
            return

        if title:
            break

        print("[ERROR] Title cannot be empty.")

    while True:
        description = input("Enter Milestone Description: ").strip()

        if is_cancel(description):
            print("\nCancelled.")
            return

        if description:
            break

        print("[ERROR] Description cannot be empty.")

    while True:
        amount_input = input("Enter Milestone Amount ($): ").strip()

        if is_cancel(amount_input):
            print("\nCancelled.")
            return

        try:
            amount = validate_amount(amount_input)
        except ValueError as e:
            print(f"[ERROR] {e}")
            continue

        existing_total = sum(
            milestone.amount for milestone in manager.get_project_milestones(project_id)
        )

        existing_total = round(existing_total, 2)
        new_total = round(existing_total + amount, 2)

        if new_total > project.budget:
            print(
                f"[ERROR] Milestone amount exceeds remaining project budget "
                f"(${round(project.budget - existing_total, 2)})."
            )
            continue

        break

    while True:
        deadline_input = input("Enter Milestone Deadline (YYYY-MM-DD): ").strip()

        if is_cancel(deadline_input):
            print("\nCancelled.")
            return

        try:
            deadline = validate_date(deadline_input)
            break
        except ValueError as e:
            print(f"[ERROR] {e}")

    new_milestone = Milestone(
        ms_id, project_id, title, description, amount, deadline, "Pending"
    )

    manager.add_milestone(new_milestone)
    manager.sync_project_milestones(project_id)

    manager.add_audit_log(
        client.user_id,
        "MILESTONE_ADDED",
        f"Client {client.user_id} added milestone {ms_id} to project {project_id}.",
    )

    manager.save_data()
    print(f"Milestone '{title}' (ID: {ms_id}) added successfully.")


def review_milestone(client, manager):

    ms_id_input = input("Enter Milestone ID to review (or CANCEL to go back): ")

    if is_cancel(ms_id_input):
        print("\nCancelled.")
        return

    ms_id = ms_id_input.strip().upper()

    milestone = manager.find_milestone(ms_id)

    if milestone is None:
        print("[ERROR] Milestone not found.")
        return

    project = manager.find_project(milestone.project_id)

    if project is None or project.client_id != client.user_id:
        print("[ERROR] This milestone does not belong to one of your projects.")
        return

    if milestone.status != "Submitted":
        print(
            f"[ERROR] This milestone has status '{milestone.status}' "
            f"and is not awaiting review."
        )
        return

    print(f"\n--- Reviewing Milestone: {milestone.title} ---")
    print(f"Description: {milestone.description}")
    print(f"Amount: ${milestone.amount}")
    print(f"Deadline: {milestone.deadline}")
    print("\n[1] Approve")
    print("[2] Reject")

    review_choice = input("Enter choice (1 or 2): ").strip()

    if review_choice == "1":
        old_status = milestone.status
        already_approved = any(
            entry.get("new_status") == "Approved" for entry in milestone.history
        )
        milestone.update_status("Approved")

        freelancer = manager.find_user(project.freelancer_id)
        if freelancer is not None and not already_approved:
            freelancer.earnings = round(freelancer.earnings + milestone.amount, 2)

        manager.add_audit_log(
            client.user_id,
            "MILESTONE_APPROVED",
            f"Client {client.user_id} approved {milestone.milestone_id} "
            f"from {old_status} to {milestone.status}.",
        )

        manager.save_data()
        print(f"Milestone {milestone.milestone_id} approved.")

    elif review_choice == "2":
        old_status = milestone.status
        milestone.update_status("In Progress")

        manager.add_audit_log(
            client.user_id,
            "MILESTONE_REJECTED",
            f"Client {client.user_id} rejected {milestone.milestone_id} "
            f"from {old_status} to {milestone.status}.",
        )

        manager.save_data()
        print(
            f"Milestone {milestone.milestone_id} rejected and sent back to the freelancer."
        )

    else:
        print("[ERROR] Invalid choice.")


def view_milestone_history(user, manager):
    ms_id_input = input("Enter Milestone ID for history (or CANCEL to go back): ")

    if is_cancel(ms_id_input):
        print("\nCancelled.")
        return

    ms_id = ms_id_input.strip().upper()
    milestone = manager.find_milestone(ms_id)

    if milestone is None:
        print("[ERROR] Milestone not found.")
        return

    project = manager.find_project(milestone.project_id)

    if user.role == "Client":
        owns = project is not None and project.client_id == user.user_id
        error_msg = "[ERROR] This milestone does not belong to one of your projects."
    else:
        owns = project is not None and project.freelancer_id == user.user_id
        error_msg = "[ERROR] This milestone is not assigned to you."

    if not owns:
        print(error_msg)
        return

    print(f"\n--- Milestone History: {milestone.title} ({milestone.milestone_id}) ---")
    print(f"Current Status: {milestone.status}")

    history = milestone.history

    if not history:
        print("No status change history recorded yet.")
        return

    for idx, entry in enumerate(history, 1):
        timestamp = entry.get("timestamp", "Unknown time")
        print(
            f"  {idx}. {entry.get('old_status')} -> {entry.get('new_status')} ({timestamp})"
        )


def update_milestone(freelancer, manager):

    project_id_input = input(
        "Enter Project ID to view milestones (or CANCEL to go back): "
    )

    if is_cancel(project_id_input):
        print("\nCancelled.")
        return

    try:
        project_id = validate_project_id(project_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    project = manager.find_project(project_id)

    if project is None or project.freelancer_id != freelancer.user_id:
        print("[ERROR] Project not found or not assigned to you.")
        return

    milestones = manager.get_project_milestones(project_id)

    if not milestones:
        print("No milestones found for this project.")
        return

    print("\n--- Milestones ---")
    for ms in milestones:
        print(
            f"ID: {ms.milestone_id} | Title: {ms.title} | Status: {ms.status} | Amount: ${ms.amount}"
        )

    ms_id = input("\nEnter Milestone ID to update (or CANCEL to go back): ")

    if is_cancel(ms_id):
        print("\nCancelled.")
        return

    ms_id = ms_id.strip().upper()
    target_milestone = manager.find_milestone(ms_id)

    if target_milestone is None or target_milestone.project_id != project_id:
        print("[ERROR] Invalid Milestone ID.")
        return

    if target_milestone.status in ("Submitted", "Approved", "Paid"):
        print(
            f"[ERROR] This milestone is already {target_milestone.status.lower()} and cannot be changed."
        )
        return

    print(f"Current Status: {target_milestone.status}")
    print("1. Set to 'In Progress'")
    print("2. Submit for Client Review")

    status_choice = input("Enter choice (1 or 2): ").strip()

    if status_choice == "1":
        old_status = target_milestone.status
        target_milestone.update_status("In Progress")

        manager.add_audit_log(
            freelancer.user_id,
            "MILESTONE_UPDATED",
            f"Freelancer {freelancer.user_id} updated {target_milestone.milestone_id} "
            f"from {old_status} to {target_milestone.status}.",
        )

        manager.save_data()
        print(f"Milestone {target_milestone.milestone_id} is now In Progress.")

    elif status_choice == "2":
        old_status = target_milestone.status
        target_milestone.update_status("Submitted")

        manager.add_audit_log(
            freelancer.user_id,
            "MILESTONE_UPDATED",
            f"Freelancer {freelancer.user_id} updated {target_milestone.milestone_id} "
            f"from {old_status} to {target_milestone.status}.",
        )

        manager.save_data()
        print(f"Milestone {target_milestone.milestone_id} submitted for client review.")

    else:
        print("[ERROR] Invalid choice.")
