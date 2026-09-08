from classes import Milestone
from validators import (
    is_cancel,
    print_menu,
    print_screen,
    return_to,
    validate_project_id,
    validate_milestone_id,
    validate_amount,
    validate_date,
)

def milestones_menu(auth, user):
    while True:
        print_menu("MILESTONES MENU")

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
        elif is_cancel(choice) or choice == "0":
            return_to(f"{user.role} Menu")
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

    print_screen("MILESTONES", hint=None)

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

        print_screen("MILESTONE DETAILS")
        ms_id = input("Enter Milestone ID: ").strip()

        if is_cancel(ms_id):
            return_to("Milestones Menu")
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
                print(f"    ID: {milestone.milestone_id}")
                print(f"    Title: {milestone.title}")
                print(f"    Description: {milestone.description}")
                print(f"    Project ID: {milestone.project_id}")
                print(f"    Amount: ${milestone.amount}")
                print(f"    Deadline: {milestone.deadline}")
                print(f"    Status: {milestone.status}")

                history = milestone.history
                if not history:
                    print("    History: No status change recorded yet.")
                else:
                    print("    History:")
                    for idx, entry in enumerate(history, 1):
                        timestamp = entry.get("timestamp", "Unknown time")
                        print(
                            f"      {idx}. {entry.get('old_status')} -> {entry.get('new_status')} "
                            f"({timestamp})"
                        )
                print("-" * 50)

        while True:

            again = input("\nView another milestone? (y/n): ").strip().lower()

            if again == "y":
                break
            if is_cancel(again):
                return_to("Milestones Menu")
                return
            print("[ERROR] Please enter y or n.")

def add_milestone(client, manager):
    print_screen("ADD MILESTONE")

    while True:
        project_id_input = input("Enter Project ID: ").strip()

        if is_cancel(project_id_input):
            return_to("Milestones Menu")
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
        client.user_id,
        "MILESTONE_ADDED",
        f"Client {client.user_id} added milestone {ms_id} to project {project_id}.",
    )

    manager.save_data(msg=False)
    print(f"Milestone '{title}' (ID: {ms_id}) added successfully.")

def review_milestone(client, manager):

    print_screen("REVIEW MILESTONE")

    ms_id_input = input("Enter Milestone ID to review: ")

    if is_cancel(ms_id_input):
        return_to("Milestones Menu")
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

    print(f"    Title: {milestone.title}")
    print(f"    Description: {milestone.description}")
    print(f"    Amount: ${milestone.amount}")
    print(f"    Deadline: {milestone.deadline}")
    print("-" * 50)
    print("[1] Approve")
    print("[2] Reject")
    print("[0] Back")
    print("-" * 50)

    review_choice = input("Enter your choice (0-2): ").strip()

    if is_cancel(review_choice) or review_choice == "0":
        return_to("Milestones Menu")
        return

    if review_choice == "1":
        old_status = milestone.status
        milestone.update_status("Approved")

        manager.add_audit_log(
            client.user_id,
            "MILESTONE_APPROVED",
            f"Client {client.user_id} approved {milestone.milestone_id} "
            f"from {old_status} to {milestone.status}.",
        )

        manager.save_data(msg=False)
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

        manager.save_data(msg=False)
        print(
            f"Milestone {milestone.milestone_id} rejected and sent back to the freelancer."
        )

    else:
        print("\n[ERROR] Invalid choice. Please enter a value between (0-2).\n")

def view_milestone_history(user, manager):
    print_screen("MILESTONE HISTORY")

    ms_id_input = input("Enter Milestone ID: ")

    if is_cancel(ms_id_input):
        return_to("Milestones Menu")
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

def update_milestone(freelancer, manager):

    print_screen("UPDATE MILESTONE")

    project_id_input = input("Enter Project ID: ")

    if is_cancel(project_id_input):
        return_to("Milestones Menu")
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

    print_screen("MILESTONES", hint=None)

    for counter, ms in enumerate(milestones, 1):
        print(f"[{counter}] ID: {ms.milestone_id}")
        print(f"    Title: {ms.title}")
        print(f"    Status: {ms.status}")
        print(f"    Amount: ${ms.amount}")
        print("-" * 50)

    ms_id = input("Enter Milestone ID to update: ")

    if is_cancel(ms_id):
        return_to("Milestones Menu")
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

    print(f"    Current Status: {target_milestone.status}")
    print("-" * 50)
    print("[1] Set to In Progress")
    print("[2] Submit for Client Review")
    print("[0] Back")
    print("-" * 50)

    status_choice = input("Enter your choice (0-2): ").strip()

    if is_cancel(status_choice) or status_choice == "0":
        return_to("Milestones Menu")
        return

    if status_choice == "1":
        old_status = target_milestone.status
        target_milestone.update_status("In Progress")

        manager.add_audit_log(
            freelancer.user_id,
            "MILESTONE_UPDATED",
            f"Freelancer {freelancer.user_id} updated {target_milestone.milestone_id} "
            f"from {old_status} to {target_milestone.status}.",
        )

        manager.save_data(msg=False)
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

        manager.save_data(msg=False)
        print(f"Milestone {target_milestone.milestone_id} submitted for client review.")

    else:
        print("\n[ERROR] Invalid choice. Please enter a value between (0-2).\n")

