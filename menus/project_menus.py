from classes import MissingFreelancerError, Project
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
    validate_priority,
    validate_status,
    validate_skills,
    validate_amount,
    validate_date,
)

from menus.menu_helpers import print_projects


def projects_menu(auth, user):
    while True:
        print_menu("PROJECTS MENU")

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

        print("[0] Back")
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
        elif is_cancel(choice) or choice == "0":
            return_to(f"{user.role} Menu")
            return
        else:
            print(
                f"\n[ERROR] Invalid choice. Please enter a value between (0-{max_choice}).\n"
            )


def create_project(client, manager):
    print_screen("CREATE PROJECT")

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

    manager.add_project(new_project)
    client.project_ids.append(project_id)

    manager.add_audit_log(
        client.user_id,
        "PROJECT_CREATED",
        f"Client {client.user_id} created project {project_id}.",
    )

    manager.save_data(msg=False)
    print(f"Project '{title}' (ID: {project_id}) created successfully.")


def view_project_details(user, manager):
    while True:
        print_screen("PROJECT DETAILS")
        proj_id = input("Enter Project ID: ").strip()

        if is_cancel(proj_id):
            return_to("Projects Menu")
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
                print("-" * 50)

        while True:
            again = input("\nView another project? (y/n): ").strip().lower()

            if again == "y":
                break
            if is_cancel(again):
                return_to("Projects Menu")
                return
            print("[ERROR] Please enter y or n.")


def update_project(client, manager):
    print_screen(
        "UPDATE PROJECT",
        hint="(Leave empty to keep the current value. Type cancel, back, or n to return.)",
    )

    project_id_input = input("Enter Project ID to update: ").strip()

    if is_cancel(project_id_input):
        return_to("Projects Menu")
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

    manager.add_audit_log(
        client.user_id,
        "PROJECT_UPDATED",
        f"Client {client.user_id} updated project {project.project_id}.",
    )

    manager.save_data(msg=False)
    print("Project updated successfully.")


def assign_freelancer(client, manager):
    print_screen("ASSIGN FREELANCER")

    project_id_input = input("Enter Project ID: ")

    if is_cancel(project_id_input):
        return_to("Projects Menu")
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

    freelancer_id_input = input("Enter Freelancer ID: ")

    if is_cancel(freelancer_id_input):
        return_to("Projects Menu")
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

        if not freelancer_matches_project(freelancer, project):
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

        manager.save_data(msg=False)
        print(f"Freelancer '{freelancer.name}' assigned to project '{project.title}'.")

    except MissingFreelancerError as e:
        print(f"[ERROR] {e}")
    except ValueError as e:
        print(f"[ERROR] {e}")


def browse_freelancers(client, manager):
    print_screen("BROWSE FREELANCERS")

    project_id_input = input("Enter Project ID to match freelancers: ")

    if is_cancel(project_id_input):
        return_to("Projects Menu")
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

        if not freelancer_matches_project(user, project):
            continue

        matches.append(user)

    if not matches:
        print("\nNo available freelancers match this project's requirements.")
        return

    print_screen("MATCHING FREELANCERS", hint=None)
    print(f"    Project: {project.title}")
    print("-" * 50)

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

    print_screen("ASSIGNED FREELANCER")

    project_id_input = input("Enter Project ID: ")

    if is_cancel(project_id_input):
        return_to("Projects Menu")
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

    print(f"    ID: {freelancer.user_id}")
    print(f"    Name: {freelancer.name}")
    print(f"    Email: {freelancer.email}")
    print(f"    Phone: {freelancer.phone}")
    print(f"    Skills: {skills}")
    print(f"    Hourly Rate: {freelancer.hourly_rate}")
    print(f"    Status: {'Active' if freelancer.active else 'Inactive'}")
    print("-" * 50)


def choose_project(freelancer, manager):
    print_screen("CHOOSE PROJECT")

    proj_id = input("Enter Project ID: ")

    if is_cancel(proj_id):
        return_to("Projects Menu")
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
    elif not freelancer_matches_project(freelancer, project):
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

        manager.save_data(msg=False)

        print("Project chosen successfully!")


def sort_projects_menu(user, manager):
    user_projects = manager.get_user_projects(user)

    if not user_projects:
        print("\nNo projects yet.")
        return

    print_menu("SORT PROJECTS")
    print("[1] Sort by Deadline")
    print("[2] Sort by Budget (highest first)")
    print("[3] Sort by Priority")
    print("[0] Back")
    print("-" * 50)

    choice = input("\nEnter your choice (0-3): ").strip()

    if is_cancel(choice) or choice == "0":
        return_to("Projects Menu")
        return

    if choice == "1":
        print_projects(manager.sort_projects_by_deadline(user_projects))
    elif choice == "2":
        print_projects(manager.sort_projects_by_budget(user_projects))
    elif choice == "3":
        print_projects(manager.sort_projects_by_priority(user_projects))
    else:
        print("\n[ERROR] Invalid choice. Please enter a value between (0-3).\n")


def delete_project(client, manager):
    print_screen("REMOVE PROJECT")

    project_id_input = input("Enter Project ID to delete: ")

    if is_cancel(project_id_input):
        return_to("Projects Menu")
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

    if not confirm_yes(
        f"Are you sure you want to delete '{project.title}'? (y/n): ",
        "Projects Menu",
    ):
        return

    invoice_codes = [
        invoice.invoice_code
        for invoice in manager.invoices
        if invoice.project_id == project_id
    ]

    manager.projects = [p for p in manager.projects if p.project_id != project_id]
    manager.milestones = [m for m in manager.milestones if m.project_id != project_id]
    manager.invoices = [i for i in manager.invoices if i.project_id != project_id]
    manager.payments = [
        p for p in manager.payments if p.invoice_code not in invoice_codes
    ]

    if project_id in client.project_ids:
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
        client.user_id,
        "PROJECT_DELETED",
        f"Client {client.user_id} deleted project {project_id} "
        f"with its milestones, invoices, and payments.",
    )

    manager.save_data(msg=False)
    print(f"Project '{project_id}' deleted successfully.")


def withdraw_from_project(freelancer, manager):

    print_screen("WITHDRAW PROJECT")

    project_id_input = input("Enter Project ID to withdraw from: ")

    if is_cancel(project_id_input):
        return_to("Projects Menu")
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

    if not confirm_yes(
        f"Are you sure you want to withdraw from '{project.title}'? (y/n): ",
        "Projects Menu",
    ):
        return

    old_status = project.status

    manager.unassign_freelancer_from_project(project)
    project.status = "Open"

    manager.add_audit_log(
        freelancer.user_id,
        "PROJECT_WITHDRAWN",
        f"Freelancer {freelancer.user_id} withdrew from project {project.project_id} "
        f"(was {old_status}).",
    )

    manager.save_data(msg=False)
    print(f"You have withdrawn from '{project.title}'. The project is now Open again.")
