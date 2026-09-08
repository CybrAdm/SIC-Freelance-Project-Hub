from datetime import datetime
import re
from main import manager, Project, Milestone


# 1. Custom Exception
class MissingFreelancerError(Exception):
    # Raised when assigning a project to a freelancer that doesn't exist.
    pass


# 2. Custom Iterator
class ProjectIterator:
    # Iterates over a list of projects sequentially.
    def __init__(self, projects):
        self._projects= projects
        self._index= 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._projects):
            proj = self._projects[self._index]
            self._index += 1
            return proj
        raise StopIteration

def get_project_health(project):
    if project.status == "Completed":
        return "COMPLETED"

    try:
        deadline_date = datetime.strptime(project.deadline, "%Y-%m-%d").date()
        today = datetime.now().date()

        if today > deadline_date:
            return "LATE"
        elif (deadline_date - today).days <= 3:
            return "AT RISK"
        else:
            return "ON TRACK"
    except (ValueError, TypeError):
        return "ON TRACK"


# 4. Project Operations
def create_project(client_id):
    print("\n--- Create New Project ---")
    while True:
        project_id = input("Please enter the ID of your new project: ").strip()
        if not project_id:
            print("The project ID can't be empty.")
            continue

        if manager.find_project(project_id):
            print("Error found: the project ID already exists. Please try another ID.")
        else:
            break

    title = input("Please enter the title of your new project: ").strip()
    if not title:
        title = "Untitled Project"

    description = input("please enter the description of your new project: ").strip()

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

    priority = input("Enter the priority level of the project [Low | Medium | High] or just press enter for medium: ").strip().capitalize()
    if priority not in ["Low", "Medium", "High"]:
        priority = "Medium"

    new_project = Project(
        project_id=project_id,
        title=title,
        description=description,
        client_id=client_id,
        freelancer_id=None,
        budget=budget,
        deadline=deadline,
        status="Pending",
    )
    new_project.priority = priority

    manager.add_project(new_project)
    manager.save_data()
    print(f"Project '{title}' (ID: {project_id}) created succesfully.")
    return new_project


def view_project():
    project_id = input("Enter Project ID to view: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error: Project not found.")
        return

    health = get_project_health(project)
    if project.freelancer_id:
        freelancer_info = project.freelancer_id
    else:
        freelancer_info = "Unassigned"
    priority = project.priority

    print(f"\n--- Project Details: {project.title} ---")
    print(f"Project ID: {project.project_id}")
    print(f"Description: {project.description}")
    print(f"Client ID: {project.client_id}")
    print(f"Freelancer ID: {freelancer_info}")
    print(f"Budget: ${project.budget}")
    print(f"Deadline: {project.deadline}")
    print(f"Status: {project.status}")
    print(f"Priority: {priority}")
    print(f"Health: {health}")


def view_all_projects(client_id):
    print("\n--- My Projects ---")
    projects = []
    for p in manager.projects:
        if p.client_id == client_id:
            projects.append(p)

    if not projects:
        print("No projects found.")
        return

    # Using custom ProjectIterator
    iterator = ProjectIterator(projects)
    for p in iterator:
        if p.freelancer_id:
            freelancer_info = p.freelancer_id
        else:
            freelancer_info = "Unassigned"
        health = get_project_health(p)
        priority = p.priority
        print(f"ID: {p.project_id} | Title: {p.title} | Status: {p.status} | Priority: {priority} | Health: {health} | Budget: ${p.budget} | Freelancer: {freelancer_info}")


def update_project(client_id):
    print("\n--- Update Project ---")
    project_id = input("Enter Project ID to update: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error: Project not found.")
        return

    if project.client_id != client_id:
        print("Unauthorized: You do not own this project.")
        return

    print("Leave empty to keep current value:")
    new_title = input(f"New Title [{project.title}]: ").strip()
    if new_title:
        project.title = new_title

    new_desc = input(f"New Description [{project.description}]: ").strip()
    if new_desc:
        project.description = new_desc

    new_budget = input(f"New Budget [${project.budget}]: ").strip()
    if new_budget:
        try:
            b_val = float(new_budget)
            if b_val > 0:
                project.budget = b_val
            else:
                print("Budget must be positive. Kept previous value.")
        except ValueError:
            print("Invalid budget. Kept previous value.")

    new_deadline = input(f"New Deadline (YYYY-MM-DD) [{project.deadline}]: ").strip()
    if new_deadline:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", new_deadline):
            try:
                datetime.strptime(new_deadline, "%Y-%m-%d")
                project.deadline = new_deadline
            except ValueError:
                print("Invalid date. Kept previous deadline.")
        else:
            print("Invalid date format. Kept previous deadline.")

    new_status = input(f"New Status (Pending/In Progress/Completed) [{project.status}]: ").strip()
    if new_status:
        if new_status in ["Pending", "In Progress", "Completed"]:
            project.status = new_status
        else:
            print("Invalid status option. Kept previous status.")

    new_priority = input("New Priority (Low/Medium/High): ").strip().capitalize()
    if new_priority:
        if new_priority in ["Low", "Medium", "High"]:
            project.priority = new_priority
        else:
            print("Invalid priority option. Kept previous priority.")

    manager.save_data()
    print("Project updated successfully.")


def delete_project(client_id):
    print("\n--- Delete Project ---")
    project_id = input("Enter Project ID to delete: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error: Project not found.")
        return

    if project.client_id != client_id:
        print("Unauthorized: You do not own this project.")
        return

    confirm = input(f"Are you sure you want to delete '{project.title}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        manager.projects = [p for p in manager.projects if p.project_id != project_id]
        manager.milestones = [m for m in manager.milestones if m.project_id != project_id]
        manager.save_data()
        print(f"Project '{project_id}' deleted succesfully.")
    else:
        print("Deletion cancelled.")


# 5. Project Assignment
def assign_freelancer():
    print("\n--- Assign Freelancer ---")
    project_id = input("Enter Project ID: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error: Project not found.")
        return

    freelancer_id = input("Enter Freelancer ID: ").strip()

    try:
        freelancer = manager.find_user(freelancer_id)
        if not freelancer:
            raise MissingFreelancerError(f"Freelancer with ID '{freelancer_id}' does not exist.")
        elif freelancer.role != "Freelancer":
            raise MissingFreelancerError(f"User with ID '{freelancer_id}' is not a Freelancer.")

        project.freelancer_id = freelancer_id
        project.status = "In Progress"

        if project_id not in freelancer.project_ids:
            freelancer.project_ids.append(project_id)

        manager.save_data()
        print(f"Success: Freelancer '{freelancer.name}' assigned to Project '{project.title}' succesfully.")

    except MissingFreelancerError as e:
        print(f"Assignment Failed: {e}")


# 6. Milestone Operations
def add_milestone():
    print("\n--- Add Milestone ---")
    project_id = input("Enter Project ID: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error: Project not found.")
        return

    while True:
        ms_id = input("Enter Milestone ID (e.g., M001): ").strip()
        if not ms_id:
            continue
        if manager.find_milestone(ms_id):
            print("Error: Milestone ID already exists. Try another.")
        else:
            break

    title = input("Enter Milestone Title: ").strip()
    description = input("Enter Milestone Description: ").strip()

    while True:
        try:
            amount = float(input("Enter Milestone Amount ($): "))
            if amount > 0:
                break
            print("Amount must be positive.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    while True:
        deadline = input("Enter Milestone Deadline (YYYY-MM-DD): ").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", deadline):
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
                break
            except ValueError:
                print("Invalid calendar date. Try again.")
        else:
            print("Invalid format. Must be YYYY-MM-DD.")

    new_milestone = Milestone(ms_id, project_id, title, description, amount, deadline, "Pending")
    manager.add_milestone(new_milestone)
    manager.sync_project_milestones(project_id)
    manager.save_data()
    print(f"Milestone '{title}' (ID: {ms_id}) added succesfully.")


def view_milestones():
    project_id = input("Enter Project ID to view milestones: ").strip()
    project = manager.find_project(project_id)
    if not project:
        print("Error: Project not found.")
        return

    milestones = manager.get_project_milestones(project_id)
    if not milestones:
        print(f"No milestones found for Project '{project_id}'.")
        return

    print("\n--- Milestones ---")
    for ms in milestones:
        print(f"ID: {ms.milestone_id} | Title: {ms.title} | Status: {ms.status} | Amount: ${ms.amount} | Deadline: {ms.deadline}")


def update_milestone():
    ms_id = input("Enter Milestone ID to update: ").strip()
    milestone = manager.find_milestone(ms_id)
    if not milestone:
        print("Error: Milestone not found.")
        return

    print(f"Current Status: {milestone.status}")
    print("1. Set to 'Pending'")
    print("2. Set to 'In Progress'")
    print("3. Set to 'Completed'")

    choice = input("Enter choice (1, 2, or 3): ").strip()
    status_map = {"1": "Pending", "2": "In Progress", "3": "Completed"}
    new_status = status_map.get(choice)

    if new_status:
        milestone.update_status(new_status)
        manager.save_data()
        print(f"Milestone status updated to '{new_status}'.")
    else:
        print("Invalid choice. Status unchanged.")


def view_milestone_history():
    ms_id = input("Enter Milestone ID for history: ").strip()
    milestone = manager.find_milestone(ms_id)
    if not milestone:
        print("Error: Milestone not found.")
        return

    print(f"\n--- Milestone History: {milestone.title} ({milestone.milestone_id}) ---")
    print(f"Current Status: {milestone.status}")
    history = milestone.history
    if not history:
        print("No status change history recorded yet.")
    else:
        for idx, entry in enumerate(history, 1):
            print(f"  {idx}. {entry.get('old_status')} -> {entry.get('new_status')}")


# 7. filter()
def get_active_projects():
    return list(filter(lambda p: p.status == "In Progress", manager.projects))


def get_late_projects():
    now = datetime.now()

    def is_late(p):
        if p.status == "Completed":
            return False
        try:
            deadline_date = datetime.strptime(p.deadline, "%Y-%m-%d")
            if deadline_date < now:
                return True
            else:
                return False
        except ValueError:
            return False

    return list(filter(is_late, manager.projects))


# 8. Lambda Sorting
def sort_projects_by_deadline():
    return sorted(manager.projects, key=lambda p: p.deadline)


def sort_projects_by_budget():
    return sorted(manager.projects, key=lambda p: float(p.budget), reverse=True)


def sort_projects_by_priority():
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    return sorted(manager.projects, key=lambda p: priority_order.get(p.priority, 4))

from admin_project_service import admin_project_management_menu, admin_milestone_management_menu