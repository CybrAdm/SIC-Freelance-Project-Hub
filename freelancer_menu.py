import re
from main import manager, Freelancer  


def register_freelancer():
    print("\n=== FREELANCER REGISTRATION ===")
 #هدخل باينات المستقل الجديد
 #هتأكد من صحة البيانات المدخلة باستخدام Regex للبريد الالكتروني ورقم الهاتف
 #  الاسم   والبريد الالكتروني ورقم الهاتف وكلمة المرور والمهارات وسعر الساعة  

    # 1. التحقق من عدم تكرار المعرف (ID)
    while True:
        user_id = input("Enter new ID : ")
        if manager.find_user(user_id):
            print("Error: ID already exists. Please try a different one.")
        else:
            break
            
    name = input("Enter Name: ")

    # 2. استخدام Regex للتحقق من البريد الإلكتروني
    while True:
        email = input("Enter Email: ")
        if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            break
        print("Invalid email format. Try again.")
        
    # استخدام Regex للتحقق من رقم الهاتف
    while True:
        phone = input("Enter Phone: ")
        if re.match(r"^\+?\d{10,15}$", phone):
            break
        print("Invalid phone format. Try again.")
        
    password = input("Enter Password: ")
    
    # استقبال المهارات كقائمة
    skills_input = input("Enter Skills : ")
    skills = [skill.strip() for skill in skills_input.split(",")]
    
    # التحقق من صحة سعر الساعة
    while True:
        try:
            hourly_rate = float(input("Enter Hourly Rate ($): "))
            if hourly_rate > 0:
                break
            print("Rate must be a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            
    # إنشاء كائن المستقل وإضافته للنظام وحفظه
    new_freelancer = Freelancer(user_id, name, email, phone, password, skills, hourly_rate)
    manager.add_user(new_freelancer)
    manager.save_data()
    print(f"\nRegistration successful! Welcome to the platform, {name}.")


def view_profile(freelancer):
    print(freelancer.profile_summary())


def update_profile(freelancer):

    print("\n--- Update Profile ---")
    print("1. Update Hourly Rate")
    print("2. Add New Skill")
    
    sub_choice = input("Enter choice (1 or 2): ")
    if sub_choice == '1':
        try:
            new_rate = float(input("Enter new hourly rate ($): "))
            if new_rate > 0:
                freelancer.hourly_rate = new_rate
                manager.save_data()
                print("Hourly rate updated successfully!")
            else:
                print("Rate must be a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    elif sub_choice == '2':
        new_skill = input("Enter new skill: ")
        freelancer.skills.append(new_skill)
        manager.save_data()
        print("Skill added successfully!")
    else:
        print("Invalid choice.")


def view_assigned_projects(freelancer):
    print("\n--- Assigned Projects ---")
    has_projects = False
    for project in manager.projects:
        if project.freelancer_id == freelancer.user_id:
            print(f"Project ID: {project.project_id} | Title: {project.title} | Status: {project.status}")
            has_projects = True
    
    if not has_projects:
        print("No assigned projects found.")


def view_project_details(freelancer):
    proj_id = input("Enter Project ID for details: ")
    project = manager.find_project(proj_id)
    
    if project and project.freelancer_id == freelancer.user_id:
        print(f"\n--- Project Details: {project.title} ---")
        print(f"Description: {project.description}")
        print(f"Budget: ${project.budget}")
        print(f"Deadline: {project.deadline}")
        print(f"Status: {project.status}")
    else:
        print("Project not found or not assigned to you.")


def update_milestone(freelancer):

    project_id = input("Enter Project ID to view milestones: ")
    milestones = manager.get_project_milestones(project_id)
    
    if not milestones:
        print("No milestones found for this project.")
        return
        
    print("\n--- Milestones ---")
    for ms in milestones:
        print(f"ID: {ms.milestone_id} | Title: {ms.title} | Status: {ms.status} | Amount: ${ms.amount}")
        
    ms_id = input("\nEnter Milestone ID to update (or press Enter to cancel): ")
    if not ms_id:
        return
        
    target_milestone = manager.find_milestone(ms_id)
    
    if target_milestone and target_milestone.status != "Completed":
        print(f"Current Status: {target_milestone.status}")
        print("1. Set to 'In Progress'")
        print("2. Set to 'Completed'")
        
        status_choice = input("Enter choice (1 or 2): ")
        
        if status_choice == '1':
            target_milestone.update_status("In Progress")
            manager.save_data()
            print(f"Milestone {ms_id} is now In Progress.")
            
        elif status_choice == '2':
            target_milestone.update_status("Completed")
            freelancer.earnings += target_milestone.amount
            manager.save_data()
            print(f"Milestone {ms_id} marked as Completed. Earnings updated!")
        else:
            print("Invalid choice.")
    elif target_milestone and target_milestone.status == "Completed":
        print("This milestone is already completed and cannot be changed.")
    else:
        print("Invalid Milestone ID.")


def view_earnings(freelancer):
    print(f"\nTotal Earnings: ${freelancer.earnings}")



def freelancer_menu(user_id):
    current_freelancer = manager.find_user(user_id)
    
    if current_freelancer is None or current_freelancer.role != "Freelancer":
        print("Error: User is not a valid Freelancer.")
        return

    while True:
        print("\n=== FREELANCER MENU ===")
        print("1. View Profile")
        print("2. Update Profile")
        print("3. View Assigned Projects")
        print("4. View Project Details")
        print("5. Update Milestones")
        print("6. View Earnings")
        print("7. Logout")

        choice = input("Enter your choice: ")

        if choice == '1':
            view_profile(current_freelancer)
        elif choice == '2':
            update_profile(current_freelancer)
        elif choice == '3':
            view_assigned_projects(current_freelancer)
        elif choice == '4':
            view_project_details(current_freelancer)
        elif choice == '5':
            update_milestone(current_freelancer)
        elif choice == '6':
            view_earnings(current_freelancer)
        elif choice == '7':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")


