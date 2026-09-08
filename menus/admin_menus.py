from classes import Freelancer, Milestone, MissingFreelancerError, Project
from manager import (
    MAX_ACTIVE_PROJECTS,
    count_active_projects,
    freelancer_matches_project,
)
from validators import (
    confirm_yes,
    is_cancel,
    print_menu,
    print_screen,
    return_to,
    validate_user_id,
    validate_project_id,
    validate_milestone_id,
    validate_priority,
    validate_status,
    validate_name,
    validate_email,
    validate_phone,
    validate_skills,
    validate_hourly_rate,
    validate_amount,
    validate_date,
)

from menus.menu_helpers import (
    FINANCE_ERRORS,
    print_users,
    print_projects,
    print_milestones_list,
    prompt_freelancer,
    prompt_client,
    prompt_project,
)


def admin_view_audit_logs(auth):
    logs = auth.manager.audit_logs

    if not logs:
        print("\nNo audit logs yet.")
        return

    print_screen("AUDIT LOGS")

    filter_choice = input("Filter by User ID (Enter to show all): ").strip()

    if is_cancel(filter_choice):
        return_to("Admin Menu")
        return

    filter_choice = filter_choice.upper()

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
        print(
            f"[{counter}] {log.get('timestamp', 'Unknown time')} | {log.get('user_id', '')} | {log.get('action', '')}"
        )
        print(f"    {log.get('description', '')}")
        print("-" * 50)


def admin_save_data(auth):
    print_screen("SAVE DATA", hint=None)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "DATA_SAVED",
        f"Admin {auth.current_user.user_id} saved data to JSON files.",
    )
    auth.manager.save_data(msg=True)


def admin_load_data(auth):
    print_screen("LOAD DATA")

    if not confirm_yes(
        "Load data from JSON files? This replaces current data in memory. (y/n): ",
        "Admin Menu",
    ):
        return

    loaded = auth.manager.load_data()

    if not loaded:
        return

    refreshed = auth.manager.find_user(auth.current_user.user_id)
    if refreshed is not None:
        auth.current_user = refreshed

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "DATA_LOADED",
        f"Admin {auth.current_user.user_id} loaded data from JSON files.",
    )
    auth.manager.save_data(msg=False)


def toggle_user_status(auth):
    print_screen("ACTIVATE / DEACTIVATE USER")

    user_id_input = input("Enter User ID: ")

    if is_cancel(user_id_input):
        return_to("Users Menu")
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

    if not confirm_yes(
        f"User '{user.name}' is currently {current_status}. "
        f"Change to {'Active' if new_status else 'Inactive'}? (y/n): ",
        "Users Menu",
    ):
        return

    user.active = new_status

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "USER_STATUS_CHANGED",
        f"Admin {auth.current_user.user_id} set {user.user_id} status to "
        f"{'Active' if new_status else 'Inactive'}.",
    )

    auth.manager.save_data(msg=False)
    print(f"User '{user.name}' is now {'Active' if new_status else 'Inactive'}.")


def view_all_freelancers(auth):
    print_screen("ALL FREELANCERS", hint=None)

    freelancers = list(
        filter(lambda user: isinstance(user, Freelancer), auth.manager.users)
    )

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "FREELANCERS_VIEWED",
        f"Admin {auth.current_user.user_id} viewed all freelancers.",
    )
    auth.manager.save_data(msg=False)

    if not freelancers:
        print("\nNo freelancers yet.")
        return

    for counter, freelancer in enumerate(freelancers, 1):
        skills = ", ".join(freelancer.skills) if freelancer.skills else "None"
        print(f"[{counter}] ID: {freelancer.user_id}")
        print(f"    Name: {freelancer.name}")
        print(f"    Email: {freelancer.email}")
        print(f"    Skills: {skills}")
        print(f"    Hourly Rate: {freelancer.hourly_rate}")
        print(f"    Status: {'Active' if freelancer.active else 'Inactive'}")
        print("-" * 50)


def delete_freelancer(auth):
    print_screen("DELETE FREELANCER")

    freelancer = prompt_freelancer(auth, "Freelancers Menu")

    if freelancer is None:
        return

    if not confirm_yes(
        f"Are you sure you want to delete freelancer '{freelancer.name}'? (y/n): ",
        "Freelancers Menu",
    ):
        return

    assigned_projects = list(
        filter(
            lambda project: project.freelancer_id == freelancer.user_id,
            auth.manager.projects,
        )
    )

    for project in assigned_projects:
        if project.status in ("Pending", "In Progress"):
            auth.manager.unassign_freelancer_from_project(project)
            project.status = "Open"

    freelancer_id = freelancer.user_id
    freelancer_name = freelancer.name

    auth.manager.remove_user(freelancer_id)
    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "FREELANCER_DELETED",
        f"Admin {auth.current_user.user_id} deleted freelancer {freelancer_id} "
        f"({freelancer_name}).",
    )
    auth.manager.save_data(msg=False)
    print(f"Freelancer '{freelancer_name}' ({freelancer_id}) has been deleted.")


def view_freelancer_assignments(auth):
    print_screen("FREELANCER ASSIGNMENTS")

    freelancer = prompt_freelancer(auth, "Freelancers Menu")

    if freelancer is None:
        return

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "FREELANCER_ASSIGNMENTS_VIEWED",
        f"Admin {auth.current_user.user_id} viewed assignments for "
        f"freelancer {freelancer.user_id}.",
    )
    auth.manager.save_data(msg=False)

    print_screen(f"ASSIGNMENTS FOR {freelancer.name.upper()}", hint=None)

    if not freelancer.project_ids:
        print("No assignments found.")
        return

    for counter, project_id in enumerate(freelancer.project_ids, 1):
        project = auth.manager.find_project(project_id)

        print(f"[{counter}] ID: {project_id}")
        if project is not None:
            print(f"    Title: {project.title}")
            print(f"    Status: {project.status}")
            print(f"    Priority: {project.priority}")
            print(f"    Deadline: {project.deadline}")
        else:
            print("    Title: Project not found")
        print("-" * 50)


def view_freelancer_statistics(auth):
    print_screen("FREELANCER STATISTICS")

    freelancer = prompt_freelancer(auth, "Freelancers Menu")

    if freelancer is None:
        return

    try:
        total_earnings = auth.manager.calculate_freelancer_earnings(
            freelancer.user_id, requesting_user_id=auth.current_user.user_id
        )
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")
        return

    active_count = count_active_projects(freelancer.user_id, auth.manager)

    print_screen(f"STATISTICS FOR {freelancer.name.upper()}", hint=None)
    print(f"    ID: {freelancer.user_id}")
    print(f"    Total Projects: {len(freelancer.project_ids)}")
    print(f"    Active Projects: {active_count}/{MAX_ACTIVE_PROJECTS}")
    print(f"    Total Earnings: ${total_earnings:.2f}")
    print(f"    Hourly Rate: ${freelancer.hourly_rate:.2f}")
    print(f"    Status: {'Active' if freelancer.active else 'Inactive'}")
    print("-" * 50)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "FREELANCER_STATS_VIEWED",
        f"Admin {auth.current_user.user_id} viewed statistics for "
        f"freelancer {freelancer.user_id}.",
    )
    auth.manager.save_data(msg=False)


def update_freelancer_data(auth):
    print_screen("UPDATE FREELANCER")

    freelancer = prompt_freelancer(auth, "Freelancers Menu")

    if freelancer is None:
        return

    print_menu("UPDATE FREELANCER DATA")
    print(f"Freelancer: {freelancer.name} ({freelancer.user_id})")
    print("-" * 50)
    print("[1] Update Name")
    print("[2] Update Email")
    print("[3] Update Phone")
    print("[4] Update Hourly Rate")
    print("[5] Update Active Status")
    print("[0] Back")
    print("-" * 50)

    choice = input("\nEnter your choice (0-5): ").strip()

    if is_cancel(choice) or choice == "0":
        return_to("Freelancers Menu")
        return

    manager = auth.manager
    admin_id = auth.current_user.user_id

    if choice == "1":
        new_name = input("Enter new name: ").strip()

        if is_cancel(new_name):
            return_to("Freelancers Menu")
            return

        try:
            freelancer.name = validate_name(new_name)
            manager.add_audit_log(
                admin_id,
                "FREELANCER_UPDATED",
                f"Admin {admin_id} updated name for freelancer {freelancer.user_id}.",
            )
            manager.save_data(msg=False)
            print("Name updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif choice == "2":
        new_email = input("Enter new email: ")

        if is_cancel(new_email):
            return_to("Freelancers Menu")
            return

        try:
            email = validate_email(new_email)
            found_user = manager.find_email(email)

            if found_user is not None and found_user.user_id != freelancer.user_id:
                print("[ERROR] This email is already registered.")
                return

            freelancer.email = email
            manager.add_audit_log(
                admin_id,
                "FREELANCER_UPDATED",
                f"Admin {admin_id} updated email for freelancer {freelancer.user_id}.",
            )
            manager.save_data(msg=False)
            print("Email updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif choice == "3":
        new_phone = input("Enter new phone number: ")

        if is_cancel(new_phone):
            return_to("Freelancers Menu")
            return

        try:
            phone = validate_phone(new_phone)
            found_user = manager.find_phone(phone)

            if found_user is not None and found_user.user_id != freelancer.user_id:
                print("[ERROR] This phone number is already registered.")
                return

            freelancer.phone = phone
            manager.add_audit_log(
                admin_id,
                "FREELANCER_UPDATED",
                f"Admin {admin_id} updated phone number for freelancer {freelancer.user_id}.",
            )
            manager.save_data(msg=False)
            print("Phone number updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif choice == "4":
        new_rate_input = input("Enter new hourly rate ($): ")

        if is_cancel(new_rate_input):
            return_to("Freelancers Menu")
            return

        try:
            freelancer.hourly_rate = validate_hourly_rate(new_rate_input)
            manager.add_audit_log(
                admin_id,
                "FREELANCER_UPDATED",
                f"Admin {admin_id} updated hourly rate for freelancer {freelancer.user_id}.",
            )
            manager.save_data(msg=False)
            print("Hourly rate updated successfully!")
        except ValueError as e:
            print(f"[ERROR] {e}")

    elif choice == "5":
        current_status = "Active" if freelancer.active else "Inactive"
        new_status_input = input("Enter new status (active/inactive): ").strip().lower()

        if is_cancel(new_status_input):
            return_to("Freelancers Menu")
            return

        if new_status_input not in ("active", "inactive"):
            print("[ERROR] Invalid status. Please enter 'active' or 'inactive'.")
            return

        new_status = new_status_input == "active"

        if new_status == freelancer.active:
            print(f"Freelancer is already {current_status}.")
            return

        if not confirm_yes(
            f"User '{freelancer.name}' is currently {current_status}. "
            f"Change to {'Active' if new_status else 'Inactive'}? (y/n): ",
            "Freelancers Menu",
        ):
            return

        freelancer.active = new_status
        manager.add_audit_log(
            admin_id,
            "FREELANCER_UPDATED",
            f"Admin {admin_id} set freelancer {freelancer.user_id} status to "
            f"{'Active' if new_status else 'Inactive'}.",
        )
        manager.save_data(msg=False)
        print(
            f"Freelancer '{freelancer.name}' is now "
            f"{'Active' if new_status else 'Inactive'}."
        )

    else:
        print("\n[ERROR] Invalid choice. Please enter a value between (0-5).\n")


def admin_users_menu(auth):
    while True:
        print_menu("USERS MENU")
        print("[1] View All Users")
        print("[2] Toggle User Status")
        print("[3] Freelancers")
        print("[0] Back")
        print("-" * 50)

        choice = input("\nEnter your choice (0-3): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to("Admin Menu")
            return

        if choice == "1":
            print_users(auth.manager.users)
        elif choice == "2":
            toggle_user_status(auth)
        elif choice == "3":
            admin_freelancer_menu(auth)
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-3).\n")


def admin_freelancer_menu(auth):
    while True:
        print_menu("FREELANCERS MENU")
        print("[1] View All Freelancers")
        print("[2] Delete a Freelancer")
        print("[3] View Freelancer Assignments")
        print("[4] Freelancer Statistics")
        print("[5] Update Freelancer Data")
        print("[0] Back")
        print("-" * 50)

        choice = input("\nEnter your choice (0-5): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to("Users Menu")
            return

        if choice == "1":
            view_all_freelancers(auth)
        elif choice == "2":
            delete_freelancer(auth)
        elif choice == "3":
            view_freelancer_assignments(auth)
        elif choice == "4":
            view_freelancer_statistics(auth)
        elif choice == "5":
            update_freelancer_data(auth)
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-5).\n")


def admin_create_project(auth):
    print_screen("CREATE PROJECT")

    client = prompt_client(auth, "Projects Menu")

    if client is None:
        return

    if not client.active:
        print("[ERROR] This client account is inactive.")
        return

    manager = auth.manager

    while True:
        project_id_input = input("Enter Project ID (e.g. P001): ").strip()

        if is_cancel(project_id_input):
            return_to("Projects Menu")
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
            return_to("Projects Menu")
            return

        if title:
            break

        print("[ERROR] Title cannot be empty.")

    while True:
        description = input("Enter Project Description: ").strip()

        if is_cancel(description):
            return_to("Projects Menu")
            return

        if description:
            break

        print("[ERROR] Description cannot be empty.")

    while True:
        budget_input = input("Enter Budget ($): ").strip()

        if is_cancel(budget_input):
            return_to("Projects Menu")
            return

        try:
            budget = validate_amount(budget_input)
            break
        except ValueError as e:
            print(f"[ERROR] {e}")

    while True:
        deadline_input = input("Enter Deadline (YYYY-MM-DD): ").strip()

        if is_cancel(deadline_input):
            return_to("Projects Menu")
            return

        try:
            deadline = validate_date(deadline_input)
            break
        except ValueError as e:
            print(f"[ERROR] {e}")

    while True:
        priority_input = input("Enter Priority (Low/Medium/High): ").strip()

        if is_cancel(priority_input):
            return_to("Projects Menu")
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
            return_to("Projects Menu")
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

    assign_choice = input("Assign a freelancer now? (y/n): ").strip().lower()

    if is_cancel(assign_choice):
        return_to("Projects Menu")
        return

    assigned_freelancer = None

    if assign_choice == "y":
        freelancer_id_input = input("Enter Freelancer ID: ").strip()

        if is_cancel(freelancer_id_input):
            return_to("Projects Menu")
            return

        try:
            validate_user_id(freelancer_id_input, expected_role="Freelancer")
            assigned_id = freelancer_id_input.strip().upper()
            freelancer = manager.find_user(assigned_id)

            if freelancer is None or freelancer.role != "Freelancer":
                raise MissingFreelancerError(
                    f"Freelancer with ID '{assigned_id}' does not exist."
                )

            if not freelancer.active:
                print(
                    "[ERROR] This freelancer account is inactive. "
                    "Project will remain unassigned."
                )
            elif (
                count_active_projects(freelancer.user_id, manager)
                >= MAX_ACTIVE_PROJECTS
            ):
                print(
                    "[ERROR] This freelancer already has the maximum number of "
                    "active projects. Project will remain unassigned."
                )
            elif not freelancer_matches_project(freelancer, new_project):
                print(
                    "[ERROR] This freelancer does not have the required skills. "
                    "Project will remain unassigned."
                )
            else:
                assigned_freelancer = freelancer
                new_project.freelancer_id = freelancer.user_id
                new_project.status = "Pending"
        except MissingFreelancerError as e:
            print(f"[ERROR] {e} Project will remain unassigned.")
        except ValueError as e:
            print(f"[ERROR] {e} Project will remain unassigned.")

    manager.add_project(new_project)

    if project_id not in client.project_ids:
        client.project_ids.append(project_id)

    if (
        assigned_freelancer is not None
        and project_id not in assigned_freelancer.project_ids
    ):
        assigned_freelancer.project_ids.append(project_id)

    manager.add_audit_log(
        auth.current_user.user_id,
        "PROJECT_CREATED",
        f"Admin {auth.current_user.user_id} created project {project_id} "
        f"for client {client.user_id}.",
    )
    manager.save_data(msg=False)
    print(f"Project '{title}' (ID: {project_id}) created successfully.")


def admin_view_all_projects(auth):
    print_screen("ALL PROJECTS", hint=None)

    if not auth.manager.projects:
        print("\nNo projects yet.")
        return

    print(f"Total Projects: {len(auth.manager.projects)}")
    print_projects(auth.manager.projects)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "PROJECTS_VIEWED",
        f"Admin {auth.current_user.user_id} viewed all projects.",
    )
    auth.manager.save_data(msg=False)


def admin_view_project_details(auth):
    print_screen("PROJECT DETAILS")

    project = prompt_project(auth, "Projects Menu")

    if project is None:
        return

    client = auth.manager.find_user(project.client_id)
    client_name = (
        f"{client.name} ({project.client_id})"
        if client is not None
        else project.client_id
    )

    if project.freelancer_id:
        freelancer = auth.manager.find_user(project.freelancer_id)
        freelancer_name = (
            f"{freelancer.name} ({project.freelancer_id})"
            if freelancer is not None
            else project.freelancer_id
        )
    else:
        freelancer_name = "Unassigned"

    print_screen(project.title.upper(), hint=None)
    print(f"    ID: {project.project_id}")
    print(f"    Description: {project.description}")
    print(f"    Client: {client_name}")
    print(f"    Freelancer: {freelancer_name}")
    print(
        f"    Required Skills: {', '.join(project.required_skills) if project.required_skills else 'None'}"
    )
    print(f"    Budget: ${float(project.budget):.2f}")
    print(f"    Deadline: {project.deadline}")
    print(f"    Status: {project.status}")
    print(f"    Priority: {project.priority}")
    print(f"    Health: {project.get_health()}")
    print("-" * 50)

    milestones = auth.manager.get_project_milestones(project.project_id)
    print(f"Milestones ({len(milestones)}):")
    if not milestones:
        print("    No milestones created yet.")
    else:
        for milestone in milestones:
            print(
                f"    - [{milestone.milestone_id}] {milestone.title} | "
                f"${milestone.amount} | Due: {milestone.deadline} | "
                f"Status: {milestone.status}"
            )
    print("-" * 50)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "PROJECT_DETAILS_VIEWED",
        f"Admin {auth.current_user.user_id} viewed details for project {project.project_id}.",
    )
    auth.manager.save_data(msg=False)


def admin_update_project(auth):
    print_screen(
        "UPDATE PROJECT",
        hint="(Leave empty to keep the current value. Type cancel, back, or n to return.)",
    )

    project = prompt_project(auth, "Projects Menu")

    if project is None:
        return

    manager = auth.manager
    print(f"Updating: '{project.title}' (ID: {project.project_id})")

    new_title = input(f"New Title [{project.title}]: ").strip()

    if is_cancel(new_title):
        return_to("Projects Menu")
        return

    new_desc = input(f"New Description [{project.description}]: ").strip()

    if is_cancel(new_desc):
        return_to("Projects Menu")
        return

    new_budget = input(f"New Budget [${project.budget}]: ").strip()

    if is_cancel(new_budget):
        return_to("Projects Menu")
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
        return_to("Projects Menu")
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
        return_to("Projects Menu")
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
        return_to("Projects Menu")
        return

    priority = project.priority

    if new_priority:
        try:
            priority = validate_priority(new_priority)
        except ValueError as e:
            print(f"[ERROR] {e} Kept previous priority.")
            priority = project.priority

    reassign_client = input(
        f"New Client ID [{project.client_id}] (leave blank to keep): "
    ).strip()

    if is_cancel(reassign_client):
        return_to("Projects Menu")
        return

    if new_title:
        project.title = new_title

    if new_desc:
        project.description = new_desc

    project.budget = budget
    project.deadline = deadline
    project.status = status
    project.priority = priority

    if unassign_freelancer and project.freelancer_id:
        manager.unassign_freelancer_from_project(project)

    if reassign_client:
        try:
            validate_user_id(reassign_client, expected_role="Client")
            new_client_id = reassign_client.strip().upper()
            new_client = manager.find_user(new_client_id)

            if new_client is None or new_client.role != "Client":
                print(
                    f"[ERROR] No client found with ID {new_client_id}. Kept current client."
                )
            else:
                old_client = manager.find_user(project.client_id)
                if (
                    old_client is not None
                    and project.project_id in old_client.project_ids
                ):
                    old_client.project_ids.remove(project.project_id)

                project.client_id = new_client_id
                if project.project_id not in new_client.project_ids:
                    new_client.project_ids.append(project.project_id)
                print(f"Client updated to '{new_client.name}'.")
        except ValueError as e:
            print(f"[ERROR] {e} Kept current client.")

    manager.add_audit_log(
        auth.current_user.user_id,
        "PROJECT_UPDATED",
        f"Admin {auth.current_user.user_id} updated project {project.project_id}.",
    )
    manager.save_data(msg=False)
    print("Project updated successfully.")


def admin_delete_project(auth):
    print_screen("DELETE PROJECT")

    project = prompt_project(auth, "Projects Menu")

    if project is None:
        return

    if not confirm_yes(
        f"Are you sure you want to delete '{project.title}' "
        f"and all related milestones, invoices, and payments? (y/n): ",
        "Projects Menu",
    ):
        return

    manager = auth.manager
    project_id = project.project_id

    invoice_codes = [
        invoice.invoice_code
        for invoice in manager.invoices
        if invoice.project_id == project_id
    ]

    manager.projects = [p for p in manager.projects if p.project_id != project_id]
    manager.milestones = [m for m in manager.milestones if m.project_id != project_id]
    manager.invoices = [i for i in manager.invoices if i.project_id != project_id]
    manager.payments = [
        payment
        for payment in manager.payments
        if payment.invoice_code not in invoice_codes
    ]

    client = manager.find_user(project.client_id)
    if client is not None and project_id in client.project_ids:
        client.project_ids.remove(project_id)

    if project.freelancer_id:
        freelancer = manager.find_user(project.freelancer_id)
        if freelancer is not None and project_id in freelancer.project_ids:
            freelancer.project_ids.remove(project_id)

        if freelancer is not None and freelancer.role == "Freelancer":
            freelancer.earnings = manager.calculate_freelancer_earnings(
                freelancer.user_id
            )

    manager.add_audit_log(
        auth.current_user.user_id,
        "PROJECT_DELETED",
        f"Admin {auth.current_user.user_id} deleted project {project_id} "
        f"with its milestones, invoices, and payments.",
    )
    manager.save_data(msg=False)
    print(f"Project '{project_id}' deleted successfully.")


def admin_assign_freelancer(auth):
    print_screen("ASSIGN FREELANCER")

    project = prompt_project(auth, "Projects Menu")

    if project is None:
        return

    manager = auth.manager

    if project.freelancer_id:
        current_fl = manager.find_user(project.freelancer_id)
        current_str = (
            f"{current_fl.name} ({project.freelancer_id})"
            if current_fl is not None
            else project.freelancer_id
        )
        print(f"Currently assigned to: {current_str}")
        print("Type 'none' to unassign this project.")
    else:
        print("Currently: Unassigned")

    fl_id_input = input("Enter Freelancer ID: ").strip()

    if is_cancel(fl_id_input):
        return_to("Projects Menu")
        return

    if fl_id_input.lower() == "none":
        if not project.freelancer_id:
            print("Project is already unassigned.")
            return

        manager.unassign_freelancer_from_project(project)
        project.status = "Open"
        manager.add_audit_log(
            auth.current_user.user_id,
            "FREELANCER_UNASSIGNED",
            f"Admin {auth.current_user.user_id} unassigned freelancer from "
            f"project {project.project_id}.",
        )
        manager.save_data(msg=False)
        print(f"Project '{project.project_id}' is now unassigned and Open.")
        return

    try:
        validate_user_id(fl_id_input, expected_role="Freelancer")
        fl_id = fl_id_input.strip().upper()
        freelancer = manager.find_user(fl_id)

        if freelancer is None or freelancer.role != "Freelancer":
            raise MissingFreelancerError(
                f"Freelancer with ID '{fl_id}' does not exist."
            )

        if not freelancer.active:
            print("[ERROR] This freelancer account is inactive.")
            return

        if project.freelancer_id == freelancer.user_id:
            print("This freelancer is already assigned to the project.")
            return

        active_count = count_active_projects(freelancer.user_id, manager)

        if active_count >= MAX_ACTIVE_PROJECTS:
            print(
                f"[ERROR] This freelancer already has {active_count} active projects."
            )
            return

        if not freelancer_matches_project(freelancer, project):
            print("[ERROR] This freelancer does not have the required skills.")
            return

        if project.freelancer_id:
            manager.unassign_freelancer_from_project(project)

        project.freelancer_id = freelancer.user_id
        project.status = "Pending"

        if project.project_id not in freelancer.project_ids:
            freelancer.project_ids.append(project.project_id)

        manager.add_audit_log(
            auth.current_user.user_id,
            "FREELANCER_ASSIGNED",
            f"Admin {auth.current_user.user_id} assigned {freelancer.user_id} "
            f"to project {project.project_id}.",
        )
        manager.save_data(msg=False)
        print(f"Freelancer '{freelancer.name}' assigned to project '{project.title}'.")
    except MissingFreelancerError as e:
        print(f"[ERROR] {e}")
    except ValueError as e:
        print(f"[ERROR] {e}")


def admin_filter_projects(auth):
    print_menu("FILTER PROJECTS")
    print("[1] Active Projects (Pending / In Progress)")
    print("[2] Late / Overdue Projects")
    print("[3] Completed Projects")
    print("[4] Open (Unassigned) Projects")
    print("[0] Back")
    print("-" * 50)

    choice = input("\nEnter your choice (0-4): ").strip()

    if is_cancel(choice) or choice == "0":
        return_to("Projects Menu")
        return

    manager = auth.manager

    if choice == "1":
        filtered = list(
            filter(
                lambda project: project.status in ("Pending", "In Progress"),
                manager.projects,
            )
        )
        label = "ACTIVE PROJECTS"
    elif choice == "2":
        filtered = manager.get_late_projects()
        label = "LATE PROJECTS"
    elif choice == "3":
        filtered = list(
            filter(lambda project: project.status == "Completed", manager.projects)
        )
        label = "COMPLETED PROJECTS"
    elif choice == "4":
        filtered = list(
            filter(lambda project: project.status == "Open", manager.projects)
        )
        label = "OPEN PROJECTS"
    else:
        print("\n[ERROR] Invalid choice. Please enter a value between (0-4).\n")
        return

    print_screen(label, hint=None)
    print(f"Total: {len(filtered)}")
    print_projects(filtered)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "PROJECTS_FILTERED",
        f"Admin {auth.current_user.user_id} filtered projects ({label}).",
    )
    auth.manager.save_data(msg=False)


def admin_sort_projects(auth):
    print_menu("SORT PROJECTS")
    print("[1] Sort by Deadline (earliest first)")
    print("[2] Sort by Budget (highest first)")
    print("[3] Sort by Priority (High -> Low)")
    print("[0] Back")
    print("-" * 50)

    choice = input("\nEnter your choice (0-3): ").strip()

    if is_cancel(choice) or choice == "0":
        return_to("Projects Menu")
        return

    manager = auth.manager

    if choice == "1":
        sorted_list = manager.sort_projects_by_deadline()
        label = "SORTED BY DEADLINE"
    elif choice == "2":
        sorted_list = manager.sort_projects_by_budget()
        label = "SORTED BY BUDGET"
    elif choice == "3":
        sorted_list = manager.sort_projects_by_priority()
        label = "SORTED BY PRIORITY"
    else:
        print("\n[ERROR] Invalid choice. Please enter a value between (0-3).\n")
        return

    print_screen(label, hint=None)
    print_projects(sorted_list)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "PROJECTS_SORTED",
        f"Admin {auth.current_user.user_id} sorted projects ({label}).",
    )
    auth.manager.save_data(msg=False)


def admin_project_report(auth):
    print_screen("PROJECT HEALTH REPORT", hint=None)

    projects = auth.manager.projects
    total_count = len(projects)

    if total_count == 0:
        print("\nNo projects yet.")
        return

    completed_projects = list(
        filter(lambda project: project.status == "Completed", projects)
    )
    active_projects = list(
        filter(
            lambda project: project.status in ("Pending", "In Progress"),
            projects,
        )
    )
    open_projects = list(filter(lambda project: project.status == "Open", projects))
    late_projects = auth.manager.get_late_projects()
    at_risk_projects = list(
        filter(lambda project: project.get_health() == "At Risk", projects)
    )
    total_budget = sum(float(project.budget) for project in projects)

    print(f"    Total Projects: {total_count}")
    print(f"    Total Budget: ${total_budget:,.2f}")
    print("-" * 50)
    print(f"    Completed: {len(completed_projects)}")
    print(f"    Active (Pending / In Progress): {len(active_projects)}")
    print(f"    Open (Unassigned): {len(open_projects)}")
    print(f"    At Risk (due in 3 days or less): {len(at_risk_projects)}")
    print(f"    Late / Overdue: {len(late_projects)}")
    print("-" * 50)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "PROJECT_REPORT_VIEWED",
        f"Admin {auth.current_user.user_id} viewed the project health report.",
    )
    auth.manager.save_data(msg=False)


def admin_project_management_menu(auth):
    while True:
        print_menu("PROJECTS MENU")
        print("[1] Create Project")
        print("[2] All Projects")
        print("[3] View Project Details")
        print("[4] Update Project")
        print("[5] Assign Freelancer")
        print("[6] Filter Projects")
        print("[7] Sort Projects")
        print("[8] Remove Project")
        print("[9] Project Report")
        print("[0] Back")
        print("-" * 50)

        choice = input("\nEnter your choice (0-9): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to("Admin Menu")
            return

        if choice == "1":
            admin_create_project(auth)
        elif choice == "2":
            admin_view_all_projects(auth)
        elif choice == "3":
            admin_view_project_details(auth)
        elif choice == "4":
            admin_update_project(auth)
        elif choice == "5":
            admin_assign_freelancer(auth)
        elif choice == "6":
            admin_filter_projects(auth)
        elif choice == "7":
            admin_sort_projects(auth)
        elif choice == "8":
            admin_delete_project(auth)
        elif choice == "9":
            admin_project_report(auth)
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-9).\n")


def admin_view_all_milestones(auth):
    print_screen("ALL MILESTONES", hint=None)

    if not auth.manager.milestones:
        print("\nNo milestones yet.")
        return

    print(f"Total Milestones: {len(auth.manager.milestones)}")
    print_milestones_list(auth.manager.milestones)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "MILESTONES_VIEWED",
        f"Admin {auth.current_user.user_id} viewed all milestones.",
    )
    auth.manager.save_data(msg=False)


def admin_view_project_milestones(auth):
    print_screen("PROJECT MILESTONES")

    project = prompt_project(auth, "Milestones Menu")

    if project is None:
        return

    milestones = auth.manager.get_project_milestones(project.project_id)
    print(f"Project: {project.title} ({project.project_id})")
    print_milestones_list(milestones)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "PROJECT_MILESTONES_VIEWED",
        f"Admin {auth.current_user.user_id} viewed milestones for "
        f"project {project.project_id}.",
    )
    auth.manager.save_data(msg=False)


def admin_add_milestone(auth):
    print_screen("ADD MILESTONE")

    project = prompt_project(auth, "Milestones Menu")

    if project is None:
        return

    manager = auth.manager
    project_id = project.project_id

    while True:
        ms_id_input = input("Enter Milestone ID (e.g. M001): ").strip()

        if is_cancel(ms_id_input):
            return_to("Milestones Menu")
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
            return_to("Milestones Menu")
            return

        if title:
            break

        print("[ERROR] Title cannot be empty.")

    while True:
        description = input("Enter Milestone Description: ").strip()

        if is_cancel(description):
            return_to("Milestones Menu")
            return

        if description:
            break

        print("[ERROR] Description cannot be empty.")

    while True:
        amount_input = input("Enter Milestone Amount ($): ").strip()

        if is_cancel(amount_input):
            return_to("Milestones Menu")
            return

        try:
            amount = validate_amount(amount_input)
        except ValueError as e:
            print(f"[ERROR] {e}")
            continue

        existing_total = round(
            sum(
                milestone.amount
                for milestone in manager.get_project_milestones(project_id)
            ),
            2,
        )
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
            return_to("Milestones Menu")
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
        auth.current_user.user_id,
        "MILESTONE_ADDED",
        f"Admin {auth.current_user.user_id} added milestone {ms_id} "
        f"to project {project_id}.",
    )
    manager.save_data(msg=False)
    print(f"Milestone '{title}' (ID: {ms_id}) added to project '{project.title}'.")


def admin_update_milestone_status(auth):
    print_screen("UPDATE MILESTONE STATUS")

    ms_id_input = input("Enter Milestone ID: ").strip()

    if is_cancel(ms_id_input):
        return_to("Milestones Menu")
        return

    try:
        ms_id = validate_milestone_id(ms_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    milestone = auth.manager.find_milestone(ms_id)

    if milestone is None:
        print("[ERROR] Milestone not found.")
        return

    print(f"    Title: {milestone.title}")
    print(f"    Current Status: {milestone.status}")
    print("-" * 50)
    print("[1] Pending")
    print("[2] In Progress")
    print("[3] Submitted")
    print("[4] Approved")
    print("[5] Rejected")
    print("[0] Back")
    print("-" * 50)

    choice = input("\nEnter your choice (0-5): ").strip()

    if is_cancel(choice) or choice == "0":
        return_to("Milestones Menu")
        return

    status_map = {
        "1": "Pending",
        "2": "In Progress",
        "3": "Submitted",
        "4": "Approved",
        "5": "Rejected",
    }

    new_status = status_map.get(choice)

    if new_status is None:
        print("\n[ERROR] Invalid choice. Please enter a value between (0-5).\n")
        return

    if milestone.status == new_status:
        print(f"Milestone is already '{new_status}'.")
        return

    old_status = milestone.status
    milestone.update_status(new_status)
    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "MILESTONE_UPDATED",
        f"Admin {auth.current_user.user_id} updated milestone {ms_id} "
        f"from {old_status} to {new_status}.",
    )
    auth.manager.save_data(msg=False)
    print(f"Milestone status updated to '{new_status}'.")


def admin_view_milestone_history(auth):
    print_screen("MILESTONE HISTORY")

    ms_id_input = input("Enter Milestone ID: ").strip()

    if is_cancel(ms_id_input):
        return_to("Milestones Menu")
        return

    try:
        ms_id = validate_milestone_id(ms_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    milestone = auth.manager.find_milestone(ms_id)

    if milestone is None:
        print("[ERROR] Milestone not found.")
        return

    print(f"    ID: {milestone.milestone_id}")
    print(f"    Title: {milestone.title}")
    print(f"    Status: {milestone.status}")

    history = milestone.history

    if not history:
        print("    History: No status change recorded yet.")
        print("-" * 50)
        return

    print("    History:")
    for idx, entry in enumerate(history, 1):
        timestamp = entry.get("timestamp", "Unknown time")
        print(
            f"      {idx}. {entry.get('old_status')} -> {entry.get('new_status')} ({timestamp})"
        )
    print("-" * 50)

    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "MILESTONE_HISTORY_VIEWED",
        f"Admin {auth.current_user.user_id} viewed history for milestone {ms_id}.",
    )
    auth.manager.save_data(msg=False)


def admin_delete_milestone(auth):
    print_screen("DELETE MILESTONE")

    ms_id_input = input("Enter Milestone ID: ").strip()

    if is_cancel(ms_id_input):
        return_to("Milestones Menu")
        return

    try:
        ms_id = validate_milestone_id(ms_id_input)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    milestone = auth.manager.find_milestone(ms_id)

    if milestone is None:
        print("[ERROR] Milestone not found.")
        return

    if not confirm_yes(
        f"Are you sure you want to delete '{milestone.title}' ({ms_id})? (y/n): ",
        "Milestones Menu",
    ):
        return

    project_id = milestone.project_id
    auth.manager.milestones = [
        item for item in auth.manager.milestones if item.milestone_id != ms_id
    ]
    auth.manager.sync_project_milestones(project_id)
    auth.manager.add_audit_log(
        auth.current_user.user_id,
        "MILESTONE_DELETED",
        f"Admin {auth.current_user.user_id} deleted milestone {ms_id} "
        f"from project {project_id}.",
    )
    auth.manager.save_data(msg=False)
    print(f"Milestone '{ms_id}' deleted successfully.")


def admin_milestone_management_menu(auth):
    while True:
        print_menu("MILESTONES MENU")
        print("[1] All Milestones")
        print("[2] Project Milestones")
        print("[3] Add Milestone")
        print("[4] Update Milestone")
        print("[5] Milestone History")
        print("[6] Remove Milestone")
        print("[0] Back")
        print("-" * 50)

        choice = input("\nEnter your choice (0-6): ").strip()

        if is_cancel(choice) or choice == "0":
            return_to("Admin Menu")
            return

        if choice == "1":
            admin_view_all_milestones(auth)
        elif choice == "2":
            admin_view_project_milestones(auth)
        elif choice == "3":
            admin_add_milestone(auth)
        elif choice == "4":
            admin_update_milestone_status(auth)
        elif choice == "5":
            admin_view_milestone_history(auth)
        elif choice == "6":
            admin_delete_milestone(auth)
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-6).\n")
