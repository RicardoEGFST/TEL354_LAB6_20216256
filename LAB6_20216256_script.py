import yaml

# ----------- CLASES ----------- #
class Student:
    def __init__(self, name_std, code_std, mac_std):
        self.name_std = name_std
        self.code_std = code_std
        self.mac_std = mac_std

class Server:
    def __init__(self, server_name, server_ip, provided_services):
        self.server_name = server_name
        self.server_ip = server_ip
        self.provided_services = provided_services  # list of dicts: {"service_name":..., "protocol_type":..., "port_num":...}

class Subject:
    def __init__(self, subject_code, current_status, subject_title, enrolled_students, associated_servers):
        self.subject_code = subject_code
        self.current_status = current_status
        self.subject_title = subject_title
        self.enrolled_students = enrolled_students  # list of student codes
        self.associated_servers = associated_servers  # list of dicts: {"server_name":..., "allowed_services":[...]}

# ----------- LOAD / SAVE YAML ----------- #
def load_data_from_yaml(file_path):
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)
        
        students_data = {}
        for s_data in raw_data.get("alumnos", []):
            student_code = str(s_data["codigo"])
            students_data[student_code] = Student(s_data["nombre"], student_code, s_data["mac"])
        
        servers_data = {}
        for s_data in raw_data.get("servidores", []):
            servers_data[s_data["nombre"]] = Server(s_data["nombre"], s_data["ip"], s_data["servicios"])
        
        subjects_data = {}
        for c_data in raw_data.get("cursos", []):
            students_in_subject = [str(code) for code in c_data.get("alumnos", [])]
            
            subjects_data[c_data["codigo"]] = Subject(
                c_data["codigo"], 
                c_data["estado"], 
                c_data["nombre"],
                students_in_subject,
                c_data.get("servidores", [])
            )
        
        print("Data loaded successfully.")
        return students_data, subjects_data, servers_data
        
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return {}, {}, {}
    except yaml.YAMLError as e:
        print(f"Error reading YAML: {e}")
        return {}, {}, {}
    except Exception as e:
        print(f"An error occurred during data loading: {e}")
        return {}, {}, {}

def save_data_to_yaml(file_path, students_data, subjects_data, servers_data):
    try:
        output_data = {}
        
        output_data["alumnos"] = []
        for student_obj in students_data.values():
            output_data["alumnos"].append({
                "nombre": student_obj.name_std,
                "codigo": int(student_obj.code_std) if student_obj.code_std.isdigit() else student_obj.code_std,
                "mac": student_obj.mac_std
            })
        
        output_data["cursos"] = []
        for subject_obj in subjects_data.values():
            subject_entry = {
                "codigo": subject_obj.subject_code,
                "estado": subject_obj.current_status,
                "nombre": subject_obj.subject_title
            }
            
            if subject_obj.enrolled_students:
                subject_entry["alumnos"] = [int(code) if code.isdigit() else code for code in subject_obj.enrolled_students]
            
            if subject_obj.associated_servers:
                subject_entry["servidores"] = subject_obj.associated_servers
            
            output_data["cursos"].append(subject_entry)
        
        output_data["servidores"] = []
        for server_obj in servers_data.values():
            output_data["servidores"].append({
                "nombre": server_obj.server_name,
                "ip": server_obj.server_ip,
                "servicios": server_obj.provided_services
            })
        
        with open(file_path, "w", encoding='utf-8') as f:
            f.write("# Student Records\n")
            f.write("alumnos:\n")
            for student_rec in output_data["alumnos"]:
                f.write(f"  - nombre: {student_rec['nombre']}\n")
                f.write(f"    codigo: {student_rec['codigo']}\n")
                f.write(f"    mac: {student_rec['mac']}\n")
            
            f.write("\n# Course Offerings:\n")
            f.write("cursos:\n")
            for course_rec in output_data["cursos"]:
                f.write(f"  - codigo: {course_rec['codigo']}\n")
                f.write(f"    estado: {course_rec['estado']}\n")
                f.write(f"    nombre: {course_rec['nombre']}\n")
                
                if "alumnos" in course_rec:
                    f.write("    alumnos:\n")
                    for s_code in course_rec["alumnos"]:
                        f.write(f"      - {s_code}\n")
                
                if "servidores" in course_rec:
                    f.write("    servidores:\n")
                    for serv_rec in course_rec["servidores"]:
                        f.write(f"      - nombre: {serv_rec['nombre']}\n")
                        if "servicios_permitidos" in serv_rec:
                            f.write("        servicios_permitidos:\n")
                            for allowed_serv in serv_rec["servicios_permitidos"]:
                                f.write(f"          - {allowed_serv}\n")
            
            f.write("\n# Server Configurations\n")
            f.write("servidores:\n")
            for server_rec in output_data["servidores"]:
                f.write(f"  - nombre: \"{server_rec['nombre']}\"\n")
                f.write(f"    ip: {server_rec['ip']}\n")
                f.write("    servicios:\n")
                for serv_info in server_rec["servicios"]:
                    f.write(f"      - nombre: {serv_info['nombre']}\n")
                    f.write(f"        protocolo: {serv_info['protocolo']}\n")
                    f.write(f"        puerto: {serv_info['puerto']}\n")
        
        print("Data saved successfully.")
        
    except Exception as e:
        print(f"An error occurred during data export: {e}")

# ----------- AUTHORIZATION ----------- #
def is_student_authorized(student_code, server_name, service_name, subjects):
    for subject_entry in subjects.values():
        if subject_entry.current_status != "DICTANDO":
            continue
        if student_code not in subject_entry.enrolled_students:
            continue
        for server_entry in subject_entry.associated_servers:
            if server_entry["nombre"] == server_name:
                if service_name in server_entry.get("servicios_permitidos", []):
                    return True
    return False

# ----------- NETWORK FUNCTIONS (simulated) ----------- #
def retrieve_attachment_point(mac_address):
    return "00:00:00:00:01", 1

def determine_network_route(mac_address, ip_address):
    return [("00:00:00:00:01", 1), ("00:00:00:00:02", 2), ("00:00:00:00:03", 3)]

def establish_network_route(path_info, connection_details):
    print(f"Simulating flow installation for route {path_info} and connection {connection_details}")

# ----------- CLI INTERFACE ----------- #
def main_menu(all_students, all_subjects, all_servers):
    while True:
        print("\n" + "="*50)
        print("    UPSM Network Policy Manager")
        print("="*50)
        print("\nChoose an option:")
        print("1) Load Data")
        print("2) Save Data") 
        print("3) Manage Subjects")
        print("4) Manage Students")
        print("5) Manage Servers")
        print("6) Policy Rules")
        print("7) Network Connections")
        print("8) Exit Program")
        
        user_choice = input(">>> ").strip()
        
        if user_choice == "1":
            file_to_load = input("Enter filename (*): ")
            try:
                s, c, v = load_data_from_yaml(file_to_load)
                all_students.clear(); all_students.update(s)
                all_subjects.clear(); all_subjects.update(c)
                all_servers.clear(); all_servers.update(v)
            except FileNotFoundError:
                print("Specified file not found.")
            except Exception as e:
                print(f"Issue encountered during import: {e}")
                
        elif user_choice == "2":
            file_to_save = input("Enter filename: ")
            try:
                save_data_to_yaml(file_to_save, all_students, all_subjects, all_servers)
            except Exception as e:
                print(f"Issue encountered during export: {e}")
                
        elif user_choice == "3":
            subject_management_menu(all_students, all_subjects, all_servers)
            
        elif user_choice == "4":
            student_management_menu(all_students, all_subjects)
            
        elif user_choice == "5":
            server_management_menu(all_servers, all_subjects)
            
        elif user_choice == "6":
            print("Policy Rules - Feature not available in this version")
            
        elif user_choice == "7":
            connection_management_menu(all_students, all_subjects, all_servers)
            
        elif user_choice == "8":
            print("Exiting application...")
            break
        else:
            print("Invalid choice. Please try again.")

def subject_management_menu(students_data, subjects_data, servers_data):
    while True:
        print("\n=== SUBJECT MANAGEMENT ===")
        print("1) Create New Subject")
        print("2) List All Subjects (*)")
        print("3) View Subject Details (*)")
        print("4) Update Subject Information (*)")
        print("5) Remove Subject")
        print("6) Return to Main Menu")
        
        subject_option = input(">>> ").strip()
        
        if subject_option == "1":
            create_new_subject(subjects_data)
        elif subject_option == "2":
            display_all_subjects(subjects_data)
        elif subject_option == "3":
            show_subject_details(subjects_data)
        elif subject_option == "4":
            update_existing_subject(subjects_data, students_data)
        elif subject_option == "5":
            delete_subject(subjects_data)
        elif subject_option == "6":
            break
        else:
            print("Invalid option. Please try again.")

def student_management_menu(students_data, subjects_data):
    while True:
        print("\n=== STUDENT MANAGEMENT ===")
        print("1) Enroll New Student")
        print("2) Display All Students (*)")
        print("3) View Student Profile (*)")
        print("4) Modify Student Data")
        print("5) Unenroll Student")
        print("6) Return to Main Menu")
        
        student_option = input(">>> ").strip()
        
        if student_option == "1":
            enroll_new_student(students_data)
        elif student_option == "2":
            show_all_students(students_data)
        elif student_option == "3":
            view_student_profile(students_data)
        elif student_option == "4":
            modify_student_data(students_data)
        elif student_option == "5":
            unenroll_student(students_data, subjects_data)
        elif student_option == "6":
            break
        else:
            print("Invalid option. Please try again.")

def server_management_menu(servers_data, subjects_data):
    while True:
        print("\n=== SERVER MANAGEMENT ===")
        print("1) Register New Server")
        print("2) List All Servers (*)")
        print("3) View Server Configuration (*)")
        print("4) Update Server Details")
        print("5) Remove Server")
        print("6) Return to Main Menu")
        
        server_option = input(">>> ").strip()
        
        if server_option == "1":
            register_new_server(servers_data)
        elif server_option == "2":
            list_all_servers(servers_data)
        elif server_option == "3":
            view_server_configuration(servers_data)
        elif server_option == "4":
            update_server_details(servers_data)
        elif server_option == "5":
            remove_server(servers_data, subjects_data)
        elif server_option == "6":
            break
        else:
            print("Invalid option. Please try again.")

def connection_management_menu(students_data, subjects_data, servers_data):
    while True:
        print("\n=== CONNECTION MANAGEMENT ===")
        print("1) Establish New Connection (*)")
        print("2) Show Active Connections (*)")
        print("3) Display Connection Route")
        print("4) Recalculate Connection Route")
        print("5) Modify Existing Connection")
        print("6) Disconnect Session (*)")
        print("7) Return to Main Menu")
        
        connection_option = input(">>> ").strip()
        
        if connection_option == "1":
            establish_new_connection(students_data, subjects_data, servers_data)
        elif connection_option == "2":
            show_active_connections()
        elif connection_option == "3":
            display_connection_route()
        elif connection_option == "4":
            recalculate_connection_route()
        elif connection_option == "5":
            modify_existing_connection()
        elif connection_option == "6":
            disconnect_session()
        elif connection_option == "7":
            break
        else:
            print("Invalid option. Please try again.")

def create_new_subject(subjects_data):
    print("\n=== ADD NEW SUBJECT ===")
    s_code = input("Subject Code: ").strip()
    
    if s_code in subjects_data:
        print(f"A subject with code '{s_code}' already exists.")
        return
    
    s_title = input("Subject Title: ").strip()
    s_status = input("Status (ACTIVE/INACTIVE/COMPLETED): ").strip().upper()
    
    if s_status not in ["ACTIVE", "INACTIVE", "COMPLETED"]:
        print("Status must be ACTIVE, INACTIVE, or COMPLETED.")
        return
    
    if not s_code or not s_title:
        print("Subject code and title are mandatory.")
        return
    
    new_subject = Subject(s_code, s_status, s_title, [], [])
    
    print("\nDo you want to assign servers to this subject? (y/N): ", end="")
    if input().strip().lower() == 'y':
        print("Assigning servers (press Enter on 'name' to finish):")
        while True:
            server_name_to_add = input("Server Name: ").strip()
            if not server_name_to_add:
                break
            
            permitted_services = []
            print(f"Permitted services for '{server_name_to_add}' (press Enter to finish):")
            while True:
                service_to_add = input("  Service: ").strip()
                if not service_to_add:
                    break
                permitted_services.append(service_to_add)
            
            server_link = {
                "nombre": server_name_to_add,
                "servicios_permitidos": permitted_services
            }
            new_subject.associated_servers.append(server_link)
    
    subjects_data[s_code] = new_subject
    print(f"Subject '{s_title}' created successfully with {len(new_subject.associated_servers)} servers linked.")

def delete_subject(subjects_data):
    subject_code_to_delete = input("Enter the code of the subject to remove: ").strip()
    
    if subject_code_to_delete not in subjects_data:
        print(f"Subject with code '{subject_code_to_delete}' not found.")
        return
    
    subject_to_delete = subjects_data[subject_code_to_delete]
    confirmation_del = input(f"Are you sure you want to remove subject '{subject_to_delete.subject_title}' ({subject_code_to_delete})? (y/N): ").strip().lower()
    
    if confirmation_del == 'y':
        del subjects_data[subject_code_to_delete]
        print(f"Subject '{subject_to_delete.subject_title}' removed successfully.")
    else:
        print("Operation cancelled.")

# ----------- CRUD FUNCTIONS FOR SUBJECTS ----------- #

def display_all_subjects(subjects_data):
    if not subjects_data:
        print("No subjects are registered.")
        return
    
    print("\n=== LIST OF SUBJECTS ===")
    print(f"{'Code':<10} {'Title':<20} {'Status':<15} {'Students':<10} {'Servers':<10}")
    print("-" * 75)
    
    for subject_item in subjects_data.values():
        print(f"{subject_item.subject_code:<10} {subject_item.subject_title:<20} {subject_item.current_status:<15} {len(subject_item.enrolled_students):<10} {len(subject_item.associated_servers):<10}")

def show_subject_details(subjects_data):
    target_code = input("Enter the subject code: ").strip()
    
    if target_code not in subjects_data:
        print(f"Subject with code '{target_code}' not found.")
        return
    
    chosen_subject = subjects_data[target_code]
    print(f"\n=== DETAILS FOR SUBJECT {target_code} ===")
    print(f"Title: {chosen_subject.subject_title}")
    print(f"Status: {chosen_subject.current_status}")
    print(f"Code: {chosen_subject.subject_code}")
    
    print(f"\nEnrolled Students ({len(chosen_subject.enrolled_students)}):")
    if chosen_subject.enrolled_students:
        for student_id in chosen_subject.enrolled_students:
            print(f"  - {student_id}")
    else:
        print("  No students enrolled.")
    
    print(f"\nAssigned Servers ({len(chosen_subject.associated_servers)}):")
    if chosen_subject.associated_servers:
        for server_info in chosen_subject.associated_servers:
            services_available = server_info.get('servicios_permitidos', [])
            print(f"  - {server_info['nombre']}: {services_available}")
    else:
        print("  No servers assigned.")

def update_existing_subject(subjects_data, students_data):
    target_code = input("Enter the subject code to update: ").strip()
    
    if target_code not in subjects_data:
        print(f"Subject with code '{target_code}' not found.")
        return
    
    subject_to_modify = subjects_data[target_code]
    print(f"\nSubject: {subject_to_modify.subject_title} ({subject_to_modify.subject_code})")
    print("1. Add a Student")
    print("2. Remove a Student")
    print("3. Manage Assigned Servers")
    print("4. Change Subject Status")
    
    update_option = input("Select an option: ").strip()
    
    if update_option == "1":
        student_id_to_add = input("Enter the student's code to add: ").strip()
        if student_id_to_add not in students_data:
            print(f"Student with code '{student_id_to_add}' not found in student records.")
            return
        
        if student_id_to_add in subject_to_modify.enrolled_students:
            print(f"Student '{student_id_to_add}' is already enrolled in this subject.")
            return
        
        subject_to_modify.enrolled_students.append(student_id_to_add)
        print(f"Student '{student_id_to_add}' successfully added to subject '{target_code}'.")
        
    elif update_option == "2":
        if not subject_to_modify.enrolled_students:
            print("No students are enrolled in this subject.")
            return
        
        print("Currently enrolled students:")
        for idx, s_id in enumerate(subject_to_modify.enrolled_students, 1):
            print(f"{idx}. {s_id}")
        
        try:
            index_to_remove = int(input("Select the number of the student to remove: ")) - 1
            if 0 <= index_to_remove < len(subject_to_modify.enrolled_students):
                removed_student = subject_to_modify.enrolled_students.pop(index_to_remove)
                print(f"Student '{removed_student}' removed from subject '{target_code}'.")
            else:
                print("Invalid number entered.")
        except ValueError:
            print("Please enter a valid number.")
    
    elif update_option == "3":
        manage_subject_servers(subject_to_modify)
    
    elif update_option == "4":
        new_subject_status = input(f"Current status: {subject_to_modify.current_status}. New status (ACTIVE/INACTIVE/COMPLETED): ").strip().upper()
        if new_subject_status in ["ACTIVE", "INACTIVE", "COMPLETED"]:
            subject_to_modify.current_status = new_subject_status
            print(f"Subject status updated to '{new_subject_status}'.")
        else:
            print("Invalid status. Use: ACTIVE, INACTIVE, or COMPLETED.")
    else:
        print("Invalid option.")

def manage_subject_servers(subject_to_modify):
    print(f"\n=== MANAGE SERVERS FOR SUBJECT {subject_to_modify.subject_code} ===")
    print("1. Add a Server")
    print("2. Remove a Server")
    print("3. Modify Allowed Services")
    
    server_management_choice = input("Select an option: ").strip()
    
    if server_management_choice == "1":
        new_server_name = input("Server name to add: ").strip()
        
        for server_in_list in subject_to_modify.associated_servers:
            if server_in_list["nombre"] == new_server_name:
                print(f"Server '{new_server_name}' is already assigned to this subject.")
                return
        
        allowed_services_for_new_server = []
        print("Enter permitted services (press Enter to finish):")
        while True:
            svc = input("Service: ").strip()
            if not svc:
                break
            allowed_services_for_new_server.append(svc)
        
        new_server_entry = {
            "nombre": new_server_name,
            "servicios_permitidos": allowed_services_for_new_server
        }
        subject_to_modify.associated_servers.append(new_server_entry)
        print(f"Server '{new_server_name}' added with {len(allowed_services_for_new_server)} services.")
    
    elif server_management_choice == "2":
        if not subject_to_modify.associated_servers:
            print("No servers are assigned to this subject.")
            return
        
        print("Assigned servers:")
        for idx, server_rec in enumerate(subject_to_modify.associated_servers, 1):
            print(f"{idx}. {server_rec['nombre']}")
        
        try:
            idx_to_remove = int(input("Select the number of the server to remove: ")) - 1
            if 0 <= idx_to_remove < len(subject_to_modify.associated_servers):
                removed_server_rec = subject_to_modify.associated_servers.pop(idx_to_remove)
                print(f"Server '{removed_server_rec['nombre']}' removed from the subject.")
            else:
                print("Invalid number entered.")
        except ValueError:
            print("Please enter a valid number.")
    
    elif server_management_choice == "3":
        if not subject_to_modify.associated_servers:
            print("No servers are assigned to this subject.")
            return
        
        print("Assigned servers with current services:")
        for idx, server_rec in enumerate(subject_to_modify.associated_servers, 1):
            current_services = server_rec.get('servicios_permitidos', [])
            print(f"{idx}. {server_rec['nombre']}: {current_services}")
        
        try:
            idx_to_modify = int(input("Select the number of the server to modify: ")) - 1
            if 0 <= idx_to_modify < len(subject_to_modify.associated_servers):
                server_to_update = subject_to_modify.associated_servers[idx_to_modify]
                print(f"\nModifying services for '{server_to_update['nombre']}'")
                print(f"Current services: {server_to_update.get('servicios_permitidos', [])}")
                
                new_permitted_services = []
                print("Enter new services (press Enter to finish):")
                while True:
                    svc_to_add = input("Service: ").strip()
                    if not svc_to_add:
                        break
                    new_permitted_services.append(svc_to_add)
                
                server_to_update['servicios_permitidos'] = new_permitted_services
                print(f"Services updated for '{server_to_update['nombre']}'.")
            else:
                print("Invalid number entered.")
        except ValueError:
            print("Please enter a valid number.")
    else:
        print("Invalid option.")

# ----------- CRUD FUNCTIONS FOR STUDENTS ----------- #

def show_all_students(students_data):
    if not students_data:
        print("No students are registered.")
        return
    
    print("\n=== LIST OF STUDENTS ===")
    filter_by_name = input("Filter by name? (press Enter to show all): ").strip().lower()
    
    print(f"{'Code':<10} {'Name':<25} {'MAC Address':<20}")
    print("-" * 55)
    
    for student_record in students_data.values():
        if not filter_by_name or filter_by_name in student_record.name_std.lower():
            print(f"{student_record.code_std:<10} {student_record.name_std:<25} {student_record.mac_std:<20}")

def view_student_profile(students_data):
    student_code_lookup = input("Enter the student code: ").strip()
    
    if student_code_lookup not in students_data:
        print(f"Student with code '{student_code_lookup}' not found.")
        return
    
    found_student = students_data[student_code_lookup]
    print(f"\n=== STUDENT PROFILE ===")
    print(f"Code: {found_student.code_std}")
    print(f"Name: {found_student.name_std}")
    print(f"MAC Address: {found_student.mac_std}")

def enroll_new_student(students_data):
    print("\n=== ENROLL NEW STUDENT ===")
    new_student_code = input("Student Code: ").strip()
    
    if new_student_code in students_data:
        print(f"A student with code '{new_student_code}' already exists.")
        return
    
    new_student_name = input("Student Name: ").strip()
    new_student_mac = input("MAC Address: ").strip()
    
    if not new_student_code or not new_student_name or not new_student_mac:
        print("All fields are required.")
        return
    
    students_data[new_student_code] = Student(new_student_name, new_student_code, new_student_mac)
    print(f"Student '{new_student_name}' enrolled successfully.")

def modify_student_data(students_data):
    student_code_to_update = input("Enter the student code to update: ").strip()
    
    if student_code_to_update not in students_data:
        print(f"Student with code '{student_code_to_update}' not found.")
        return
    
    student_to_update = students_data[student_code_to_update]
    print(f"\nUpdating student: {student_to_update.name_std}")
    
    new_name_input = input(f"New name (current: {student_to_update.name_std}): ").strip()
    new_mac_input = input(f"New MAC (current: {student_to_update.mac_std}): ").strip()
    
    if new_name_input:
        student_to_update.name_std = new_name_input
    if new_mac_input:
        student_to_update.mac_std = new_mac_input
    
    print("Student data updated successfully.")

def unenroll_student(students_data, subjects_data):
    student_code_to_remove = input("Enter the student code to unenroll: ").strip()
    
    if student_code_to_remove not in students_data:
        print(f"Student with code '{student_code_to_remove}' not found.")
        return
    
    student_record_to_remove = students_data[student_code_to_remove]
    confirm_unenroll = input(f"Are you sure you want to unenroll '{student_record_to_remove.name_std}' ({student_code_to_remove})? (y/N): ").strip().lower()
    
    if confirm_unenroll == 'y':
        for subject_record in subjects_data.values():
            if student_code_to_remove in subject_record.enrolled_students:
                subject_record.enrolled_students.remove(student_code_to_remove)
        
        del students_data[student_code_to_remove]
        print(f"Student '{student_record_to_remove.name_std}' successfully unenrolled.")
    else:
        print("Operation cancelled.")

# ----------- CRUD FUNCTIONS FOR SERVERS ----------- #

def list_all_servers(servers_data):
    if not servers_data:
        print("No servers are registered.")
        return
    
    print("\n=== LIST OF SERVERS ===")
    print(f"{'Name':<20} {'IP Address':<15} {'Services Offered':<15}")
    print("-" * 55)
    
    for server_entry in servers_data.values():
        print(f"{server_entry.server_name:<20} {server_entry.server_ip:<15} {len(server_entry.provided_services):<15}")

def view_server_configuration(servers_data):
    server_name_lookup = input("Enter the server name: ").strip()
    
    if server_name_lookup not in servers_data:
        print(f"Server '{server_name_lookup}' not found.")
        return
    
    found_server = servers_data[server_name_lookup]
    print(f"\n=== SERVER CONFIGURATION FOR {server_name_lookup} ===")
    print(f"Name: {found_server.server_name}")
    print(f"IP Address: {found_server.server_ip}")
    
    print(f"\nAvailable Services ({len(found_server.provided_services)}):")
    if found_server.provided_services:
        for service_info in found_server.provided_services:
            print(f"  - {service_info['nombre']} ({service_info['protocolo']}:{service_info['puerto']})")
    else:
        print("  No services are configured for this server.")

def register_new_server(servers_data):
    print("\n=== REGISTER NEW SERVER ===")
    new_server_name = input("Server Name: ").strip()
    
    if new_server_name in servers_data:
        print(f"A server with name '{new_server_name}' already exists.")
        return
    
    new_server_ip = input("IP Address: ").strip()
    
    if not new_server_name or not new_server_ip:
        print("Server name and IP address are required.")
        return
    
    server_services = []
    print("\nConfiguring services (press Enter on 'name' to finish):")
    
    while True:
        service_id = input("Service Name: ").strip()
        if not service_id:
            break
        
        service_protocol = input("Protocol (TCP/UDP): ").strip().upper()
        try:
            service_port = int(input("Port Number: ").strip())
        except ValueError:
            print("Port must be a number.")
            continue
        
        server_services.append({
            "nombre": service_id,
            "protocolo": service_protocol,
            "puerto": service_port
        })
    
    servers_data[new_server_name] = Server(new_server_name, new_server_ip, server_services)
    print(f"Server '{new_server_name}' registered successfully with {len(server_services)} services.")

def update_server_details(servers_data):
    server_name_to_update = input("Enter the server name to update: ").strip()
    
    if server_name_to_update not in servers_data:
        print(f"Server '{server_name_to_update}' not found.")
        return
    
    server_to_update = servers_data[server_name_to_update]
    print(f"\nModifying server: {server_to_update.server_name}")
    
    new_ip_input = input(f"New IP Address (current: {server_to_update.server_ip}): ").strip()
    
    if new_ip_input:
        server_to_update.server_ip = new_ip_input
    
    print("1. Add a Service")
    print("2. Remove a Service")
    print("3. Keep Services Unchanged")
    
    service_update_choice = input("Select an option: ").strip()
    
    if service_update_choice == "1":
        service_to_add_name = input("Name of the new service: ").strip()
        service_to_add_protocol = input("Protocol (TCP/UDP): ").strip().upper()
        try:
            service_to_add_port = int(input("Port Number: ").strip())
            server_to_update.provided_services.append({
                "nombre": service_to_add_name,
                "protocolo": service_to_add_protocol,
                "puerto": service_to_add_port
            })
            print("Service added successfully.")
        except ValueError:
            print("Port must be a number.")
    
    elif service_update_choice == "2":
        if not server_to_update.provided_services:
            print("No services available to remove.")
        else:
            print("Configured services:")
            for idx, service_rec in enumerate(server_to_update.provided_services, 1):
                print(f"{idx}. {service_rec['nombre']}")
            
            try:
                service_idx_to_remove = int(input("Select the number of the service to remove: ")) - 1
                if 0 <= service_idx_to_remove < len(server_to_update.provided_services):
                    removed_service = server_to_update.provided_services.pop(service_idx_to_remove)
                    print(f"Service '{removed_service['nombre']}' removed successfully.")
                else:
                    print("Invalid number entered.")
            except ValueError:
                print("Please enter a valid number.")
    
    print("Server details updated successfully.")

def remove_server(servers_data, subjects_data):
    server_name_to_remove = input("Enter the name of the server to remove: ").strip()
    
    if server_name_to_remove not in servers_data:
        print(f"Server '{server_name_to_remove}' not found.")
        return
    
    server_to_remove = servers_data[server_name_to_remove]
    confirm_server_removal = input(f"Are you sure you want to remove server '{server_to_remove.server_name}'? (y/N): ").strip().lower()
    
    if confirm_server_removal == 'y':
        for subject_record in subjects_data.values():
            subject_record.associated_servers = [s for s in subject_record.associated_servers if s["nombre"] != server_name_to_remove]
        
        del servers_data[server_name_to_remove]
        print(f"Server '{server_to_remove.server_name}' successfully removed.")
    else:
        print("Operation cancelled.")

# ----------- CRUD FUNCTIONS FOR CONNECTIONS ----------- #

def establish_new_connection(all_students, all_subjects, all_servers):
    student_code_conn = input("Student Code: ").strip()
    server_name_conn = input("Server Name: ").strip()
    service_name_conn = input("Service Name: ").strip()
    
    if student_code_conn not in all_students:
        print("Student record not found.")
        return
    
    if server_name_conn not in all_servers:
        print("Server not found.")
        return
    
    target_server = all_servers[server_name_conn]
    service_exists_on_server = False
    for service_config in target_server.provided_services:
        if service_config["nombre"] == service_name_conn:
            service_exists_on_server = True
            break
    
    if not service_exists_on_server:
        print(f"The service '{service_name_conn}' is not available on server '{server_name_conn}'.")
        return
    
    if is_student_authorized(student_code_conn, server_name_conn, service_name_conn, all_subjects):
        student_mac = all_students[student_code_conn].mac_std
        server_ip = all_servers[server_name_conn].server_ip
        network_path = determine_network_route(student_mac, server_ip)
        
        import time
        connection_identifier = f"session_{int(time.time())}_{student_code_conn}_{server_name_conn}_{service_name_conn}"
        
        connection_info = {
            "mac_address": student_mac, 
            "ip_address": server_ip, 
            "service_requested": service_name_conn,
            "session_id": connection_identifier,
            "student_id": student_code_conn,
            "destination_server": server_name_conn
        }
        
        establish_network_route(network_path, connection_info)
        print(f"Connection successfully established!")
        print(f"Session ID: {connection_identifier}")
    else:
        print("Access denied: The student is not permitted to use this service on that server.")

def show_active_connections():
    print("\n=== CURRENT ACTIVE CONNECTIONS ===")
    print("Simulated function - In a real system, this would query the SDN controller")
    print("No active connections are currently listed.")

def display_connection_route():
    session_id_lookup = input("Enter the connection session ID: ").strip()
    print(f"\n=== CONNECTION ROUTE FOR {session_id_lookup} ===")
    print("Simulated function - In a real system, this would display flow states")

def recalculate_connection_route():
    session_id_recalc = input("Enter the connection session ID to recalculate: ").strip()
    print(f"Recalculating route for session {session_id_recalc}...")
    print("Simulated function - In a real system, this would recalculate and reinstall network flows")

def modify_existing_connection():
    session_id_modify = input("Enter the connection session ID to modify: ").strip()
    print(f"Modifying route for session {session_id_modify}...")
    print("Simulated function - In a real system, this would update flows in the controller")

def disconnect_session():
    session_id_disconnect = input("Enter the connection session ID to disconnect: ").strip()
    confirm_disconnect = input(f"Are you sure you want to terminate session '{session_id_disconnect}'? (y/N): ").strip().lower()
    
    if confirm_disconnect == 'y':
        print(f"Session '{session_id_disconnect}' successfully terminated.")
        print("Simulated function - In a real system, this would remove network flows from the controller")
    else:
        print("Operation cancelled.")

# ----------- MAIN EXECUTION ----------- #
def main():
    all_students_data, all_subjects_data, all_servers_data = {}, {}, {}
    try:
        s, c, v = load_data_from_yaml("data.yaml")
        all_students_data.update(s)
        all_subjects_data.update(c)
        all_servers_data.update(v)
    except FileNotFoundError:
        print("No 'data.yaml' found. Starting with empty data sets.")
    except Exception as e:
        print(f"An error occurred while loading 'data.yaml': {e}")
        print("Starting with empty data sets.")

    main_menu(all_students_data, all_subjects_data, all_servers_data)

if __name__ == "__main__":
    main()