from validators import (
    is_cancel,
    print_menu,
    print_screen,
    return_to,
    validate_name,
    validate_email,
    validate_phone,
    validate_city,
    validate_password,
    validate_company_name,
    validate_skills,
    validate_hourly_rate,
)

from menus.menu_helpers import FINANCE_ERRORS


def profile_menu(auth):
    while True:
        print_menu("PROFILE")
        print("[1] View profile")
        print("[2] Update profile")
        print("[0] Back")
        print("-" * 50)

        sub_choice = input("\nEnter your choice (0-2): ").strip()

        if is_cancel(sub_choice) or sub_choice == "0":
            return_to(f"{auth.current_user.role} Menu")
            break

        if sub_choice == "1":
            print(auth.current_user.profile_summary())
        elif sub_choice == "2":
            update_profile(auth.current_user, auth.manager)
        else:
            print("\n[ERROR] Invalid choice. Please enter a value between (0-2).\n")


def update_profile(current_user, manager):

    print_screen("UPDATE PROFILE")
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

    print("[0] Back")
    print("-" * 50)

    sub_choice = input(f"Enter your choice (0-{max_choice}): ").strip()

    if is_cancel(sub_choice) or sub_choice == "0":
        return_to("Profile Menu")
        return

    elif sub_choice == "1":
        new_name = input("Enter new name: ").strip()

        if is_cancel(new_name):
            return_to("Profile Menu")
            return

        try:
            current_user.name = validate_name(new_name)
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated name.",
            )
            manager.save_data(msg=False)
            print("Name updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "2":
        new_email = input("Enter new email: ")

        if is_cancel(new_email):
            return_to("Profile Menu")
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
            manager.save_data(msg=False)
            print("Email updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "3":
        new_phone = input("Enter new phone number: ")

        if is_cancel(new_phone):
            return_to("Profile Menu")
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
            manager.save_data(msg=False)
            print("Phone number updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "4":
        new_city = input("Enter new city: ")

        if is_cancel(new_city):
            return_to("Profile Menu")
            return

        try:
            city = validate_city(new_city)
            current_user.city = city
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated city.",
            )
            manager.save_data(msg=False)
            print("City updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "5":
        new_password = input("Enter new password: ").strip()

        if is_cancel(new_password):
            return_to("Profile Menu")
            return

        confirm_password = input("Confirm new password: ").strip()

        if is_cancel(confirm_password):
            return_to("Profile Menu")
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
            manager.save_data(msg=False)
            print("Password reset successfully!")

        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "6" and current_user.role == "Client":
        new_company = input("Enter new company name: ").strip()

        if is_cancel(new_company):
            return_to("Profile Menu")
            return

        try:
            company_name = validate_company_name(new_company)
            current_user.company_name = company_name
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated company name.",
            )
            manager.save_data(msg=False)
            print("Company name updated successfully!")
        except ValueError as e:
            print(f"[ERROR] Update failed: {e}")

    elif sub_choice == "6" and current_user.role == "Freelancer":
        new_skills_input = input("Enter new skill(s) (comma-separated): ")

        if is_cancel(new_skills_input):
            return_to("Profile Menu")
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
            manager.save_data(msg=False)
            print("Skill(s) added successfully!")
        except ValueError as e:
            print(f"[ERROR] {e}")

    elif sub_choice == "7" and current_user.role == "Freelancer":
        new_rate_input = input("Enter new hourly rate ($): ")

        if is_cancel(new_rate_input):
            return_to("Profile Menu")
            return

        try:
            current_user.hourly_rate = validate_hourly_rate(new_rate_input)
            manager.add_audit_log(
                current_user.user_id,
                "PROFILE_UPDATED",
                f"User {current_user.user_id} updated hourly rate.",
            )
            manager.save_data(msg=False)
            print("Hourly rate updated successfully!")
        except ValueError as e:
            print(f"[ERROR] {e}")

    else:
        print("\n[ERROR] Invalid choice. Please enter a valid option.\n")


def view_earnings(freelancer, auth):
    try:
        total = auth.manager.calculate_freelancer_earnings(
            freelancer.user_id, requesting_user_id=auth.current_user.user_id
        )
        print_screen("EARNINGS", hint=None)
        print(f"    Total Earnings: ${total}")
        print("-" * 50)
    except FINANCE_ERRORS as error:
        print(f"[ERROR] {error}")


def view_my_activity_log(user, manager):
    logs = []

    for log in manager.audit_logs:
        if log["user_id"] == user.user_id:
            logs.append(log)

    if not logs:
        print("\nNo activity recorded yet.")
        return

    print_screen("MY ACTIVITY LOG", hint=None)

    for counter, log in enumerate(logs, 1):
        print(
            f"[{counter}] {log.get('timestamp', 'Unknown time')} | {log.get('action', '')}"
        )
        print(f"    {log.get('description', '')}")
        print("-" * 50)
