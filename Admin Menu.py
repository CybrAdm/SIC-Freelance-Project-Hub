from main import manager, Freelancer

def view_all_freelancers():
    print("\n--- All Freelancers ---")
    freelancers = filter(lambda freelancer_onely: isinstance(freelancer_onely, Freelancer), manager.users)
    for freelancer in freelancers:
        freelancer.profile_summary()


def delete_freelancer():
    freelancer_id = input("Enter the ID of the freelancer to delete: ")
    freelancer = manager.find_user(freelancer_id)
    
    if freelancer and isinstance(freelancer, Freelancer):
        manager.remove_user(freelancer_id)
        manager.save_data()
        print(f"Freelancer with ID {freelancer_id} has been deleted.")

    else:
        print(f"No freelancer found with ID {freelancer_id}.")

def view_freelancer_assignments():
    freelancer_id = input("Enter the ID of the freelancer to view assignments: ")
    freelancer = manager.find_user(freelancer_id)
    
    if freelancer and isinstance(freelancer, Freelancer):
        print(f"\n--- Assignments for {freelancer.name} ---")
        if freelancer.project_ids:
            for project_id in freelancer.project_ids:
                print(f"Project ID: {project_id}")
        else:
            print("No assignments found.")
    else:
        print(f"No freelancer found with ID {freelancer_id}.")  


def view_freelancer_statistics():
    freelancer_id = input("Enter the ID of the freelancer to view statistics: ")
    freelancer = manager.find_user(freelancer_id)
    
    if freelancer and isinstance(freelancer, Freelancer):
        print(f"\n--- Statistics for {freelancer.name} ---")
        print(f"Total Projects: {len(freelancer.project_ids)}")
        print(f"Total Earnings: ${freelancer.earnings:.2f}")
        print(f"Active Status: {'Active' if freelancer.active else 'Inactive'}")
    else:
        print(f"No freelancer found with ID {freelancer_id}.")

def update_freelancer_data():
    freelancer_id = input("Enter the ID of the freelancer to update: ")
    freelancer = manager.find_user(freelancer_id)
    
    if freelancer and isinstance(freelancer, Freelancer):
        print(f"\n--- Update Data for {freelancer.name} ---")
        print("1. Update Name")
        print("2. Update Email")
        print("3. Update Phone")
        print("4. Update hourly rate")
        print("5. Update Active Status")


        choice = input("Enter your choice: ")
        if choice == '1':
            new_name = input("Enter new name: ")
            freelancer.name = new_name
            manager.save_data()
        elif choice == '2':
            new_email = input("Enter new email: ")
            freelancer.email = new_email
            manager.save_data() 
        elif choice == '3':
            new_phone = input("Enter new phone: ")
            freelancer.phone = new_phone
            manager.save_data()
        elif choice == '4':
            new_rate = float(input("Enter new hourly rate: "))
            if new_rate > 0:
                freelancer.hourly_rate = new_rate
                manager.save_data()
            else:
                print("Rate must be a positive number.")    
        elif choice == '5':
            new_status = input("Enter new status (active/inactive): ").lower()
            if new_status in ['active', 'inactive']:
                freelancer.active = (new_status == 'active')
                manager.save_data()
            else:
                print("Invalid status. Please enter 'active' or 'inactive'.")
        

def admin_freelancer_menu():

    while True:
        print("\n--- Admin Freelancer Menu ---")
        print("1. View All Freelancers")
        print("2. Delete a Freelancer")
        print("3. View Freelancer Assignments")
        print("4. Freelancer Statistics")
        print("5. Update data of a Freelancer")
        print("6. Return to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            view_all_freelancers()
        elif choice == '2':
            delete_freelancer()
        elif choice == '3':
            view_freelancer_assignments()
        elif choice == '4':
            view_freelancer_statistics()
        elif choice == '5':
            update_freelancer_data()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")