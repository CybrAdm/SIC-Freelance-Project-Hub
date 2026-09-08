from datetime import datetime
import re
from main import manager, Project, Milestone
from client_project_service import (
    MissingFreelancerError,
    ProjectIterator,
    get_project_health,
    get_late_projects,
    sort_projects_by_deadline,
    sort_projects_by_budget,
    sort_projects_by_priority,
)

def admin_create_project():
    print("\n Greetings, Admin.\nCreate New Project")

    # 1. Select Client
    while True:
        client_id = input("Enter the client ID you want to assign this project to: ").strip()
        if not client_id:
            print("The client ID can't be empty.")
            continue

        client = manager.find_user(client_id)
        if not client:
            print(f"Error found: the user with ID '{client_id}' doesn't exist.")
            continue

        if client.role != "Client":
            print(f"Error found: the user with ID '{client_id}' isn't a client.")
            continue
        else:
            break

    # 2. Project ID
    while True:
        project_id = input("Please enter the ID of your new project: ").strip()
        if not project_id:
            print("The project ID can't be empty.")
            continue

        if manager.find_project(project_id):
            print("Error found: the project ID already exists. Please try another ID.")
        else:
            break

    # 3. Title and Description
    title = input("Please enter the title of your new project: ").strip()
    if not title:
        title = "Untitled Project"

    description = input("please enter the description of your new project: ").strip()

    # 4. Budget
    while True:
        try:
            budget_input = input("Enter the budget: ").strip()
            budget = float(budget_input)
            if budget > 0:
                break
            else:
                print("The budget must be a positive number.")
        except ValueError:
            print("Wrong input. Please enter a valid number.")

    # 5. Deadline (Regex Validation)
    while True:
        deadline = input("Enter the deadline exactly in this format YYYY-MM-DD pleasee: ").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", deadline):
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
                break
            except ValueError:
                print("The calendar date you entered is wrong. Please try again.")
        else:
            print("The format of the date you entered is wrong. Please make sure it's YYYY-MM-DD or else it'll crash.")

    # 6. Priority
    priority = input("Enter the priority level of the project [Low | Medium | High] or just press enter for medium: ").strip().capitalize()
    if priority not in ["Low", "Medium", "High"]:
        priority = "Medium"

    # 7. Optional Freelancer Assignment
    freelancer_id = None
    assign_choice = input("Assign a freelancer now? (yes or no): ").strip().lower()
    if assign_choice == "yes":
        fl_id = input("Enter a freelancer ID:").strip()
        try:
            fl_user = manager.find_user(fl_id)
            if not fl_user:
                raise MissingFreelancerError(f"The freelancer with ID '{fl_id}' doesnt exist.")
            elif fl_user.role != "Freelancer":
                raise MissingFreelancerError(f"The user with ID '{fl_user.name}' isnt a freelancer.")
            else:
                freelancer_id = fl_id
                if project_id not in fl_user.project_ids:
                    fl_user.project_ids.append(project_id)
        except MissingFreelancerError as e:
            print(f"Warning found: {e} Project will remain unassigned for now.")
            freelancer_id = None

    if freelancer_id:
        status = "In Progress"
    else:
        status = "Pending"

    new_project = Project(
        project_id=project_id,
        title=title,
        description=description,
        client_id=client_id,
        freelancer_id=freelancer_id,
        budget=budget,
        deadline=deadline,
        status=status,
    )
    new_project.priority = priority

    if project_id not in client.project_ids:
        client.project_ids.append(project_id)

    manager.add_project(new_project)
    manager.add_audit_log("ADMIN", "CREATE_PROJECT", f"Created project {project_id} for client {client_id}")
    manager.save_data()

    print(f"Success: Project '{title}' (ID: {project_id}) created successfully.")
    return new_project


def admin_view_all_projects():
    print("\nViewing all projects...")
    if not manager.projects:
        print("No projects registered in the system.")
        return

    print(f"Total Projects: {len(manager.projects)}")
    print(f"{'ID':<8} {'Title':<20} {'Client':<10} {'Freelancer':<12} {'Budget':<10} {'Status':<14} {'Health':<12} {'Priority':<8}")

    # Using custom ProjectIterator to traverse
    iterator = ProjectIterator(manager.projects)
    for p in iterator:
        if p.freelancer_id:
            freelancer_str = p.freelancer_id
        else:
            freelancer_str = "None"

        health = get_project_health(p)
        priority = p.priority
        budget_str = f"${p.budget:,.0f}"

        title_display = p.title
        if len(title_display) > 18:
            title_display = title_display[:15] + "..."

        print(f"{p.project_id:<8} {title_display:<20} {p.client_id:<10} {freelancer_str:<12} {budget_str:<10} {p.status:<14} {health:<12} {priority:<8}")
    print(".........................")


def admin_view_project_details():
    print("\nViewing project details...")
    project_id = input("Please enter the ID of the project: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error found: the project with that ID doesn't exist.")
        return

    client = manager.find_user(project.client_id)
    if client:
        client_name = f"{client.name} ({project.client_id})"
    else:
        client_name = project.client_id

    if project.freelancer_id:
        freelancer = manager.find_user(project.freelancer_id)
        if freelancer:
            freelancer_name = f"{freelancer.name} ({project.freelancer_id})"
        else:
            freelancer_name = project.freelancer_id
    else:
        freelancer_name = "Unassigned"

    health = get_project_health(project)
    priority = project.priority
    milestones = manager.get_project_milestones(project.project_id)

    print(f"\nPROJECT: {project.title} ({project.project_id})")
    print(f"Description   : {project.description}")
    print(f"Client        : {client_name}")
    print(f"Freelancer    : {freelancer_name}")
    print(f"Budget        : ${project.budget:,.2f}")
    print(f"Deadline      : {project.deadline}")
    print(f"Status        : {project.status}")
    print(f"Priority      : {priority}")
    print(f"Health        : {health}")
    print(f"Milestones ({len(milestones)}):")
    if not milestones:
        print("  No milestones created yet.")
    else:
        for ms in milestones:
            print(f"  - [{ms.milestone_id}] {ms.title} | ${ms.amount} | Due: {ms.deadline} | Status: {ms.status}")


def admin_update_project():
    print("\nUpdating project...")
    project_id = input("Please enter the ID of the project to update: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error found: the project with that ID doesn't exist.")
        return

    print(f"Updating: '{project.title}' (ID: {project.project_id})")
    print("Press Enter without typing to keep the current value.\n")

    new_title = input(f"New Title [{project.title}]: ").strip()
    if new_title:
        project.title = new_title

    new_desc = input(f"New Description [{project.description}]: ").strip()
    if new_desc:
        project.description = new_desc

    new_budget_str = input(f"New Budget [${project.budget}]: ").strip()
    if new_budget_str:
        try:
            b_val = float(new_budget_str)
            if b_val > 0:
                project.budget = b_val
            else:
                print("The budget must be a positive number. Kept previous budget.")
        except ValueError:
            print("Wrong input. Please enter a valid number. Kept previous budget.")

    new_deadline = input(f"New Deadline (YYYY-MM-DD) [{project.deadline}]: ").strip()
    if new_deadline:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", new_deadline):
            try:
                datetime.strptime(new_deadline, "%Y-%m-%d")
                project.deadline = new_deadline
            except ValueError:
                print("The calendar date you entered is wrong. Kept previous deadline.")
        else:
            print("The format of the date you entered is wrong. Please make sure it's YYYY-MM-DD or else it'll crash.")

    new_status = input(f"New Status (Pending/In Progress/Completed) [{project.status}]: ").strip()
    if new_status:
        if new_status in ["Pending", "In Progress", "Completed"]:
            project.status = new_status
        else:
            print("Invalid status option. Kept previous status.")

    current_priority = project.priority
    new_priority = input(f"New Priority (Low/Medium/High) [{current_priority}]: ").strip().capitalize()
    if new_priority:
        if new_priority in ["Low", "Medium", "High"]:
            project.priority = new_priority
        else:
            print("Invalid priority option. Kept previous priority.")

    # Option to reassign client
    reassign_client = input(f"Enter the client ID you want to assign this project to [{project.client_id}] (leave blank to keep): ").strip()
    if reassign_client:
        new_client = manager.find_user(reassign_client)
        if new_client:
            if new_client.role == "Client":
                old_client = manager.find_user(project.client_id)
                if old_client:
                    if project.project_id in old_client.project_ids:
                        old_client.project_ids.remove(project.project_id)
                project.client_id = reassign_client
                if project.project_id not in new_client.project_ids:
                    new_client.project_ids.append(project.project_id)
                print(f"Client updated to '{new_client.name}'.")
            else:
                print(f"Error found: the user with ID '{reassign_client}' isn't a client.")
        else:
            print(f"Error found: the user with ID '{reassign_client}' doesn't exist. Kept current client.")

    # save updated project
    manager.add_audit_log("ADMIN", "UPDATE_PROJECT", f"Updated project {project.project_id}")
    manager.save_data()
    print("Success: Project details updated succesfully.")


def admin_delete_project():
    print("\nDeleting project...")
    project_id = input("Please enter the ID of the project to delete: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error found: the project with that ID doesn't exist.")
        return

    print(f"WARNING: You are about to permanently delete '{project.title}' ({project.project_id}).")
    print("This action will also remove all associated milestones!")
    confirm = input("Are you sure? (yes or no): ").strip().lower()

    if confirm == "yes":
        # Remove from client project list
        client = manager.find_user(project.client_id)
        if client:
            if project_id in client.project_ids:
                client.project_ids.remove(project_id)

        # Remove from freelancer project list
        if project.freelancer_id:
            freelancer = manager.find_user(project.freelancer_id)
            if freelancer:
                if project_id in freelancer.project_ids:
                    freelancer.project_ids.remove(project_id)

        manager.projects = [p for p in manager.projects if p.project_id != project_id]
        manager.milestones = [m for m in manager.milestones if m.project_id != project_id]

        manager.add_audit_log("ADMIN", "DELETE_PROJECT", f"Deleted project {project_id} and associated milestones")
        manager.save_data()
        print(f"Success: Project '{project_id}' deleted succesfully.")
    else:
        print("Deletion cancelled. No changes were made.")


def admin_assign_freelancer():
    print("\nAssigning freelancer...")
    project_id = input("Please enter the ID of the project: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error found: the project with that ID doesn't exist.")
        return

    if project.freelancer_id:
        current_fl = manager.find_user(project.freelancer_id)
        if current_fl:
            current_str = f"{current_fl.name} ({project.freelancer_id})"
        else:
            current_str = project.freelancer_id
        print(f"Currently assigned to: {current_str}")
        print("Type 'none' if you want to unassign this project.")
    else:
        print("Currently: Unassigned")

    fl_id = input("Enter a freelancer ID:").strip()
    if len(fl_id) == 0:
        print("Action cancelled.")
        return

    if fl_id.lower() == "none":
        if project.freelancer_id:
            old_fl = manager.find_user(project.freelancer_id)
            if old_fl:
                if project.project_id in old_fl.project_ids:
                    old_fl.project_ids.remove(project.project_id)
        project.freelancer_id = None
        project.status = "Pending"
        manager.add_audit_log("ADMIN", "UNASSIGN_FREELANCER", f"Unassigned freelancer from project {project_id}")
        manager.save_data()
        print(f"Project '{project_id}' is now unassigned and status is 'Pending'.")
        return

    try:
        freelancer = manager.find_user(fl_id)
        if not freelancer:
            raise MissingFreelancerError(f"The freelancer with ID '{fl_id}' doesnt exist.")
        elif freelancer.role != "Freelancer":
            raise MissingFreelancerError(f"The user with ID '{freelancer.name}' isnt a freelancer.")
        else:
            # Unassign previous freelancer if any
            if project.freelancer_id:
                if project.freelancer_id != fl_id:
                    prev_fl = manager.find_user(project.freelancer_id)
                    if prev_fl:
                        if project_id in prev_fl.project_ids:
                            prev_fl.project_ids.remove(project_id)

            project.freelancer_id = fl_id
            project.status = "In Progress"

            if project_id not in freelancer.project_ids:
                freelancer.project_ids.append(project_id)

            manager.add_audit_log("ADMIN", "ASSIGN_FREELANCER", f"Assigned freelancer {fl_id} to project {project_id}")
            manager.save_data()
            print(f"Success: Freelancer '{freelancer.name}' assigned to Project '{project.title}' succesfully.")
    except MissingFreelancerError as e:
        print(f"Warning found: {e}")


def admin_filter_projects():
    print("\nFiltering projects...")
    print("1. View Active Projects (In Progress)")
    print("2. View Late / Overdue Projects")
    print("3. View Completed Projects")
    print("4. View Pending (Unassigned) Projects")

    choice = input("Enter filter choice (1-4): ").strip()

    if choice == "1":
        filtered = list(filter(lambda p: p.status == "In Progress", manager.projects))
        label = "Active Projects (In Progress)"
    elif choice == "2":
        filtered = get_late_projects()
        label = "Late / Overdue Projects"
    elif choice == "3":
        filtered = list(filter(lambda p: p.status == "Completed", manager.projects))
        label = "Completed Projects"
    elif choice == "4":
        filtered = list(filter(lambda p: p.status == "Pending", manager.projects))
        label = "Pending Projects"
    else:
        print("Invalid choice.")
        return

    print(f"\n--- {label} ({len(filtered)}) ---")
    if not filtered:
        print("No projects found under this filter.")
        return

    for p in filtered:
        health = get_project_health(p)
        print(f"ID: {p.project_id} | Title: {p.title} | Status: {p.status} | Health: {health} | Due: {p.deadline} | Budget: ${p.budget:,.2f}")


def admin_sort_projects():
    print("\nSorting projects...")
    print("1. Sort by Deadline (Earliest to Latest)")
    print("2. Sort by Budget (Highest to Lowest)")
    print("3. Sort by Priority (High -> Medium -> Low)")

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        sorted_list = sort_projects_by_deadline()
        label = "Sorted by Deadline"
    elif choice == "2":
        sorted_list = sort_projects_by_budget()
        label = "Sorted by Budget (Highest First)"
    elif choice == "3":
        sorted_list = sort_projects_by_priority()
        label = "Sorted by Priority"
    else:
        print("Invalid choice.")
        return

    print(f"\n--- Projects: {label} ---")
    if not sorted_list:
        print("No projects available to sort.")
        return

    for p in sorted_list:
        priority = p.priority
        print(f"ID: {p.project_id} | Priority: {priority:<6} | Deadline: {p.deadline} | Budget: ${p.budget:<9,.2f} | Title: {p.title}")


def admin_project_report():
    print("\nViewing project health report...")

    total_count = len(manager.projects)
    if total_count == 0:
        print("No projects found in the system.")
        print("========================================")
        return

    completed_projects = list(filter(lambda p: p.status == "Completed", manager.projects))
    active_projects = list(filter(lambda p: p.status == "In Progress", manager.projects))
    pending_projects = list(filter(lambda p: p.status == "Pending", manager.projects))
    late_projects = get_late_projects()
    at_risk_projects = list(filter(lambda p: get_project_health(p) == "AT RISK", manager.projects))

    total_budget = sum(float(p.budget) for p in manager.projects)

    print(f"Total Projects Registered : {total_count}")
    print(f"Total Contracted Budget   : ${total_budget:,.2f}")
    print("-" * 40)
    print(f"Completed Projects        : {len(completed_projects)}")
    print(f"Active (In Progress)      : {len(active_projects)}")
    print(f"Pending (Unassigned)      : {len(pending_projects)}")
    print(f"At Risk (Due in <= 3 days): {len(at_risk_projects)}")
    print(f"Late / Overdue Projects   : {len(late_projects)}")
    print("========================================")


def admin_project_management_menu():
    while True:
        print("\n" + "=" * 44)
        print("       ADMIN - PROJECT MANAGEMENT       ")
        print("=" * 44)
        print("1. View All Projects (with Iterator)")
        print("2. View Project Details")
        print("3. Create New Project (for any client)")
        print("4. Update Project Details")
        print("5. Delete Project")
        print("6. Assign / Reassign Freelancer")
        print("7. Filter Projects (filter())")
        print("8. Sort Projects (lambda)")
        print("9. Project Summary & Health Report")
        print("0. Back to Admin Main Menu")
        print("=" * 44)

        choice = input("Enter choice (0-9): ").strip()

        if choice == "1":
            admin_view_all_projects()
        elif choice == "2":
            admin_view_project_details()
        elif choice == "3":
            admin_create_project()
        elif choice == "4":
            admin_update_project()
        elif choice == "5":
            admin_delete_project()
        elif choice == "6":
            admin_assign_freelancer()
        elif choice == "7":
            admin_filter_projects()
        elif choice == "8":
            admin_sort_projects()
        elif choice == "9":
            admin_project_report()
        elif choice == "0":
            print("Returning to Admin Main Menu...")
            break
        else:
            print("Invalid choice. Please select an option between 0 and 9.")


def admin_view_all_milestones():
    print("\nViewing all milestones...")
    if not manager.milestones:
        print("No milestones registered in the system.")
        return

    print(f"Total Milestones: {len(manager.milestones)}")
    print(f"{'MS ID':<10} {'Project ID':<12} {'Title':<22} {'Amount':<10} {'Deadline':<12} {'Status':<12}")

    for ms in manager.milestones:
        t_display = ms.title
        if len(t_display) > 20:
            t_display = t_display[:17] + "..."
        print(f"{ms.milestone_id:<10} {ms.project_id:<12} {t_display:<22} ${ms.amount:<9,.0f} {ms.deadline:<12} {ms.status:<12}")


def admin_view_project_milestones():
    print("\nViewing milestones for project...")
    project_id = input("Please enter the ID of the project: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error found: the project with that ID doesn't exist.")
        return

    milestones = manager.get_project_milestones(project_id)
    print(f"\nMilestones for Project '{project.title}' ({project_id}):")
    if not milestones:
        print("  No milestones found for this project.")
        return

    for ms in milestones:
        print(f"  [{ms.milestone_id}] {ms.title} | ${ms.amount:,.2f} | Due: {ms.deadline} | Status: {ms.status}")


def admin_add_milestone():
    print("\nAdding milestone...")
    project_id = input("Please enter the ID of the project: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error found: the project with that ID doesn't exist.")
        return

    while True:
        ms_id = str(input("Enter Milestone ID (e.g., M001): ")).strip()
        if len(ms_id) == 0:
            continue

        if manager.find_milestone(ms_id):
            print("Error: Milestone ID already exists. Try another.")
        else:
            break

    title = input("Enter Milestone Title: ").strip()
    if not title:
        title = "Untitled Milestone"

    description = input("Enter Milestone Description: ").strip()

    while True:
        try:
            amount_input = input("Enter the budget: ").strip()
            amount = float(amount_input)
            if amount > 0:
                break
            else:
                print("The budget must be a positive number.")
        except ValueError:
            print("Wrong input. Please enter a valid number.")

    while True:
        deadline = input("Enter the deadline exactly in this format YYYY-MM-DD pleasee: ").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", deadline):
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
                break
            except ValueError:
                print("The calendar date you entered is wrong. Please try again.")
        else:
            print("The format of the date you entered is wrong. Please make sure it's YYYY-MM-DD or else it'll crash.")

    new_milestone = Milestone(
        milestone_id=ms_id,
        project_id=project_id,
        title=title,
        description=description,
        amount=amount,
        deadline=deadline,
        status="Pending",
    )

    manager.add_milestone(new_milestone)
    manager.sync_project_milestones(project_id)
    manager.add_audit_log("ADMIN", "ADD_MILESTONE", f"Added milestone {ms_id} to project {project_id}")
    manager.save_data()

    print(f"Success: Milestone '{title}' (ID: {ms_id}) added to project '{project.title}' succesfully.")
    return new_milestone


def admin_update_milestone_status():
    print("\nUpdating milestone status...")
    ms_id = input("Please enter the milestone ID to update: ").strip()
    milestone = manager.find_milestone(ms_id)
    if not milestone:
        print("Error found: the milestone with that ID doesn't exist.")
        return

    print(f"Milestone: '{milestone.title}' ({milestone.milestone_id})")
    print(f"Current Status: {milestone.status}")
    print("1. Set to 'Pending'")
    print("2. Set to 'In Progress'")
    print("3. Set to 'Completed'")

    choice = input("Enter choice (1, 2, or 3): ").strip()
    if choice == "1":
        new_status = "Pending"
    elif choice == "2":
        new_status = "In Progress"
    elif choice == "3":
        new_status = "Completed"
    else:
        new_status = None

    if new_status:
        milestone.update_status(new_status)
        manager.add_audit_log("ADMIN", "UPDATE_MILESTONE", f"Updated milestone {ms_id} status to {new_status}")
        manager.save_data()
        print(f"Success: Milestone status updated to '{new_status}'.")
    else:
        print("Invalid choice. Status unchanged.")


def admin_view_milestone_history():
    print("\nViewing milestone history...")
    ms_id = input("Please enter the milestone ID to view history: ").strip()
    milestone = manager.find_milestone(ms_id)
    if not milestone:
        print("Error found: the milestone with that ID doesn't exist.")
        return

    print(f"\nHistory for Milestone: '{milestone.title}' ({milestone.milestone_id})")
    print(f"Current Status: {milestone.status}")
    history = milestone.history
    if not history:
        print("No status transitions recorded yet.")
    else:
        for idx, entry in enumerate(history, 1):
            old_s = entry.get("old_status")
            new_s = entry.get("new_status")
            print(f"  {idx}. Changed from '{old_s}' to '{new_s}'")


def admin_delete_milestone():
    print("\nDeleting milestone...")
    ms_id = input("Please enter the milestone ID to delete: ").strip()
    milestone = manager.find_milestone(ms_id)
    if not milestone:
        print("Error found: the milestone with that ID doesn't exist.")
        return

    confirm = input("Are you sure? (yes or no): ").strip().lower()
    if confirm == "yes":
        project_id = milestone.project_id
        manager.milestones = [m for m in manager.milestones if m.milestone_id != ms_id]
        manager.sync_project_milestones(project_id)
        manager.add_audit_log("ADMIN", "DELETE_MILESTONE", f"Deleted milestone {ms_id} from project {project_id}")
        manager.save_data()
        print(f"Success: Milestone '{ms_id}' deleted succesfully.")
    else:
        print("Deletion cancelled. No changes were made.")


def admin_milestone_management_menu():
    while True:
        print("\n" + "=" * 44)
        print("      ADMIN - MILESTONE MANAGEMENT      ")
        print("=" * 44)
        print("1. View All Milestones (all projects)")
        print("2. View Milestones for a Project")
        print("3. Add Milestone to Project")
        print("4. Update Milestone Status")
        print("5. View Milestone History")
        print("6. Delete Milestone")
        print("0. Back to Admin Main Menu")
        print("=" * 44)

        choice = input("Enter choice (0-6): ").strip()

        if choice == "1":
            admin_view_all_milestones()
        elif choice == "2":
            admin_view_project_milestones()
        elif choice == "3":
            admin_add_milestone()
        elif choice == "4":
            admin_update_milestone_status()
        elif choice == "5":
            admin_view_milestone_history()
        elif choice == "6":
            admin_delete_milestone()
        elif choice == "0":
            print("Returning to Admin Main Menu...")
            break
        else:
            print("Invalid choice. Please select an option between 0 and 6.")
