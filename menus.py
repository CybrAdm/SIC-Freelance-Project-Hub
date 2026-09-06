from manager import count_active_projects, MAX_ACTIVE_PROJECTS
from validators import (
    is_cancel,
    validate_email,
    validate_password,
    validate_phone,
    validate_city,
    validate_company_name,
    validate_skills,
    validate_project_id,
)


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
        print(f"    Description: {project.description}")
        print(f"    Client ID: {project.client_id}")
        print(
            f"    Required Skills: {', '.join(project.required_skills) if project.required_skills else 'None'}"
        )
        print(f"    Status: {project.status}")
        print(f"    Budget: {project.budget}")
        print(f"    Deadline: {project.deadline}")
        print("-" * 50)


def client_menu(auth):
    client = auth.manager.find_user(auth.current_user.user_id)

    while True:
        print("\n" + "=" * 50)
        print("                 CLIENT MENU")
        print("=" * 50)
        print("[1] Profile")
        print("[2] Projects")
        print("[3] Milestones")
        print("[4] Invoices")
        print("[5] Payments")
        print("[0] Logout")
        print("-" * 50)

        choice = input("\nEnter your choice (0-5): ").strip()

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

        elif choice == "0":
            auth.logout()
            return
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-5).\n")


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
            print("\n[ERROR] Invalid choice. Please enter a value between (0-2).\n")


def profile_menu(auth):
    while True:
        print("\n" + "=" * 50)
        print("                 PROFILE")
        print("=" * 50)
        print("[1] View profile")
        print("[2] Update profile")
        print("[0] Back to Freelancer Menu")
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

        if new_name:
            current_user.name = new_name
            manager.save_data()
            print("Name updated successfully!")
        else:
            print("[ERROR] Name cannot be empty.")

    elif sub_choice == "2":
        new_email = input("Enter new email: ")

        if is_cancel(new_email):
            print("\nUpdate cancelled.")
            return

        try:
            email = validate_email(new_email)
            current_user.email = email
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
            current_user.phone = phone
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
            current_user.skills.extend(new_skills)
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
            new_rate = float(new_rate_input)
            if new_rate > 0:
                current_user.hourly_rate = new_rate
                manager.save_data()
                print("Hourly rate updated successfully!")
            else:
                print("[ERROR] Rate must be a positive number.")
        except ValueError:
            print("[ERROR] Invalid input. Please enter a number.")

    else:
        print("[ERROR] Invalid choice.")


def projects_menu(auth, user):
    while True:
        print("\n" + "=" * 50)
        print("               PROJECTS MENU")
        print("=" * 50)

        if user.role == "Client":
            print("[1] Create Project")
            print("[2] My Projects")
            print("[3] Remove Project")
            print("[4] View Assigned Freelancer")
            max_choice = 4
        else:
            print("[1] Browse Projects")
            print("[2] My Projects")
            print("[3] View Project Details")
            print("[4] Choose Project")
            print("[5] Withdraw Project")
            max_choice = 5

        print("[0] Back to previous menu")
        print("-" * 50)

        choice = input(f"\nEnter your choice (0-{max_choice}): ").strip()

        if choice == "1":
            if user.role == "Client":
                ...
            else:
                print_projects(auth.manager.get_available_projects(user))
        elif choice == "2":
            user_projects = auth.manager.get_user_projects(user)
            print_projects(user_projects)
        elif choice == "3":
            if user.role == "Client":
                ...
            else:
                view_project_details(user, auth.manager)
        elif choice == "4":
            if user.role == "Client":
                view_assigned_freelancer(user, auth.manager)
            else:
                choose_project(user, auth.manager)
        elif choice == "5" and user.role == "Freelancer":
            withdraw_from_project(user, auth.manager)
        elif choice == "0":
            print(f"\nReturning to {user.role} Menu...")
            return
        else:
            print(
                f"\n[ERROR] Invalid choice. Please enter a value between (0-{max_choice}).\n"
            )


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
                print(
                    f"    Required Skills: {', '.join(project.required_skills) if project.required_skills else 'None'}"
                )
                print(f"    Status: {project.status}")
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
    elif project.status != "Open":
        print("[ERROR] This project is not available for selection.")
    elif active_count >= MAX_ACTIVE_PROJECTS:
        print(
            f"[ERROR] You already have {active_count} active projects. "
            f"Complete one before choosing a new project."
        )
    elif project.required_skills and not any(
        skill in freelancer.skills for skill in project.required_skills
    ):
        print("[ERROR] You don't have the required skills for this project.")
    else:
        project.freelancer_id = freelancer.user_id
        project.status = "Pending"
        freelancer.project_ids.append(project.project_id)

        manager.add_audit_log(
            freelancer.user_id,
            "PROJECT_CHOSEN",
            f"Freelancer chose project {project.project_id}.",
        )

        manager.save_data()

        print("Project chosen successfully!")


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
            print("[3] Review Milestone (Approve/Reject)")
        else:
            print("[3] Update Milestone")

        print("[0] Back")
        print("-" * 50)

        choice = input("\nEnter your choice (0-3): ").strip()

        if choice == "1":
            my_milestones(user, auth.manager)
        elif choice == "2":
            milestone_details(user, auth.manager)
        elif choice == "3":
            if user.role == "Client":
                review_milestone(user, auth.manager)
            else:
                update_milestone(user, auth.manager)
        elif choice == "0":
            print(f"\nReturning to {user.role} Menu...")
            return
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-3).\n")


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

        while True:

            again = input("\nView another milestone? (y/n): ").strip().lower()

            if again == "y":
                break
            elif again == "n":
                return
            else:
                print("[ERROR] Please enter 'y' or 'n'.")


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

    status_choice = input("Enter choice (1 or 2): ")

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

    if status_choice == "2":
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
        milestone.update_status("Approved")

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


def view_earnings(freelancer):
    print(f"\nTotal Earnings: ${freelancer.earnings}")


def user_home(auth):
    role = auth.current_user.role

    if role == "Client":
        client_menu(auth)
    elif role == "Freelancer":
        freelancer_menu(auth)
    elif role == "Admin":
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
