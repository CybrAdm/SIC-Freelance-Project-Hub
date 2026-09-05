import re
from main import manager, Freelancer

def register_freelancer():
    print("\n=== FREELANCER REGISTRATION ===")
    
    while True:
        user_id = input("Enter ID : ")
        if manager.find_user(user_id):
            print("Error: ID already exists. Please try a different one.")
        else:
            break
            
    name = input("Enter Name: ")
    
    while True:
        email = input("Enter Email: ")
        if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            break
        print("Invalid email format. Try again.")
        
    while True:
        phone = input("Enter Phone: ")
        if re.match(r"^\+?\d{10,15}$", phone):
            break
        print("Invalid phone format. Try again.")
        
    password = input("Enter Password: ")
    
    skills_input = input("Enter Skills (comma-separated, e.g., Python, Linux, Networking): ")
    skills = [skill.strip() for skill in skills_input.split(",")]
    
    while True:
        try:
            hourly_rate = float(input("Enter Hourly Rate ($): "))
            if hourly_rate > 0:
                break
            print("Rate must be a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            
    new_freelancer = Freelancer(user_id, name, email, phone, password, skills, hourly_rate)
    manager.add_user(new_freelancer)
    manager.save_data()
    print(f"\nRegistration successful! Welcome to the platform, {name}.")


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
            print(current_freelancer.profile_summary())

        elif choice == '2':
            print("\n--- Update Profile ---")
            print("1. Update Hourly Rate")
            print("2. Add New Skill")
            
            sub_choice = input("Enter choice (1 or 2): ")
            if sub_choice == '1':
                try:
                    new_rate = float(input("Enter new hourly rate ($): "))
                    if new_rate > 0:
                        current_freelancer.hourly_rate = new_rate
                        manager.save_data()
                        print("Hourly rate updated successfully!")
                    else:
                        print("Rate must be a positive number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    
            elif sub_choice == '2':
                new_skill = input("Enter new skill: ")
                current_freelancer.skills.append(new_skill)
                manager.save_data()
                print("Skill added successfully!")
            else:
                print("Invalid choice.")

        elif choice == '3':
            print("\n--- Assigned Projects ---")
            has_projects = False
            for project in manager.projects:
                if project.freelancer_id == current_freelancer.user_id:
                    print(f"Project ID: {project.project_id} | Title: {project.title} | Status: {project.status}")
                    has_projects = True
            
            if not has_projects:
                print("No assigned projects found.")
                
        elif choice == '4':
            proj_id = input("Enter Project ID for details: ")
            project = manager.find_project(proj_id)
            
            if project and project.freelancer_id == current_freelancer.user_id:
                print(f"\n--- Project Details: {project.title} ---")
                print(f"Description: {project.description}")
                print(f"Budget: ${project.budget}")
                print(f"Deadline: {project.deadline}")
                print(f"Status: {project.status}")
            else:
                print("Project not found or not assigned to you.")

        elif choice == '5':
            project_id = input("Enter Project ID to view milestones: ")
            milestones = manager.get_project_milestones(project_id)
            
            if not milestones:
                print("No milestones found for this project.")
                continue
                
            print("\n--- Milestones ---")
            for ms in milestones:
                print(f"ID: {ms.milestone_id} | Title: {ms.title} | Status: {ms.status} | Amount: ${ms.amount}")
                
            ms_id = input("\nEnter Milestone ID to update (or press Enter to cancel): ")
            if not ms_id:
                continue
                
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
                    current_freelancer.earnings += target_milestone.amount
                    manager.save_data()
                    print(f"Milestone {ms_id} marked as Completed. Earnings updated!")
                else:
                    print("Invalid choice.")
            elif target_milestone and target_milestone.status == "Completed":
                print("This milestone is already completed and cannot be changed.")
            else:
                print("Invalid Milestone ID.")

        elif choice == '6':
            print(f"\nTotal Earnings: ${current_freelancer.earnings}")

        elif choice == '7':
            print("Logging out...")
            break
            
        else:
            print("Invalid choice. Please try again.")

'''
=========================================
الشرح الشامل للكود (دليل التشغيل والمناقشة)
=========================================

1. دالة التسجيل (register_freelancer):
   - التحقق من الـ ID: يتم استدعاء `manager.find_user()` للتأكد من عدم وجود مستقل بنفس المعرف[cite: 2].
   - تطبيق الـ Regex: تم استيراد مكتبة `re` لمطابقة البريد الإلكتروني ورقم الهاتف مع الأنماط الصحيحة؛ لمنع إدخال بيانات عشوائية[cite: 2].
   - تجهيز المهارات: يتم استقبال المهارات كنص واحد مفصول بفواصل، ثم تحويله إلى قائمة (List) باستخدام `split()` لتخزينه كـ Array.
   - التحقق من السعر (Exception Handling): تم استخدام `try...except` لمنع انهيار البرنامج إذا أدخل المستخدم نصوصاً بدلاً من الأرقام في خانة سعر الساعة.
   - الإنشاء والحفظ: يتم تمرير البيانات لبناء كائن جديد من كلاس `Freelancer`، ويُضاف إلى `manager`، ثم تُحفظ التعديلات في ملف الـ JSON[cite: 2].

2. دالة القائمة الرئيسية (freelancer_menu):
   - الاستدعاء: هذه الدالة لا تعمل إلا عند استلام `user_id` صحيح بعد نجاح تسجيل الدخول. تستخرج الدالة بيانات المستقل فوراً للعمل عليها[cite: 2].
   - عرض الملف (الخيار 1): يستدعي `profile_summary()` وهو الكود الذي يثبت تطبيقك للـ Polymorphism (تعدد الأشكال)، حيث تعرض الدالة بيانات مخصصة للمستقل[cite: 2].
   - تحديث الملف (الخيار 2): يسمح بتعديل سعر الساعة والمهارات. أي تعديل يتبعه فوراً `manager.save_data()` لضمان الحفظ.
   - تصفية المشاريع (الخيارات 3 و 4): يقوم بمرور (Loop) على جميع المشاريع في النظام، ولا يعرض سوى المشاريع التي يتطابق فيها `freelancer_id` مع معرف المستقل الحالي[cite: 2]. 
   - دورة حياة مهام العمل (الخيار 5):
     أ. يعرض مهام مشروع معين.
     ب. يمنع تعديل المهام المكتملة مسبقاً.
     ج. يتيح النقل التدريجي للحالة: إما إلى "قيد التنفيذ" (In Progress) أو "مكتملة" (Completed)[cite: 2].
     د. إذا تم تحويلها إلى "مكتملة"، يقوم الكود بإضافة قيمة المهمة إلى الأرباح الإجمالية `earnings` لحفظها[cite: 2].
   - عرض الأرباح (الخيار 6): يطبع إجمالي الرصيد الذي تم تجميعه من المهام المكتملة[cite: 2].
'''