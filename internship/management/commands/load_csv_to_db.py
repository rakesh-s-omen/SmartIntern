from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from internship.models import UserProfile, InternshipApplication, WeeklyLog, ProgressProof
from datetime import datetime, timedelta
import random
import csv
import os

class Command(BaseCommand):
    help = 'Load CSV files directly into PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing users and reload from CSV (WARNING: destroys all data)',
        )

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading CSV data into PostgreSQL...')
        
        # Only delete all users if --reset flag is provided
        if kwargs.get('reset'):
            self.stdout.write(self.style.WARNING('⚠ RESET MODE: Deleting all existing users...'))
            User.objects.all().delete()
        else:
            self.stdout.write(self.style.SUCCESS('✓ Preserving existing users (use --reset to delete all)'))
        
        # Get CSV file paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        faculty_csv = os.path.join(base_dir, 'hicas_faculty_data.csv')
        students_csv = os.path.join(base_dir, 'hicas_students_simulated.csv')
        
        # Department mapping
        dept_mapping = {
            'B.Com Accounting & Finance': 'BCOM_AF',
            'B.Com CA': 'BCOM_CA',
            'B.Com CS': 'BCOM_CS',
            'B.Com Commerce': 'BCOM',
            'B.Com IT': 'BCOM_IT',
            'B.Com International Business': 'BCOM_IB',
            'B.Com Professional Accounting': 'BCOM_PA',
            'B.Sc AI & ML': 'BSC_AI',
            'B.Sc Animation & Visual Effects': 'BSC_ANIM',
            'B.Sc Biotechnology': 'BSC_BIO',
            'B.Sc CS with Cognitive Systems': 'BSC_CS_COG',
            'B.Sc CS with Cyber Security': 'BSC_CS_CYB',
            'B.Sc Catering Science & Hotel Management': 'BSC_CATERING',
            'B.Sc Computer Science': 'CSE',
            'B.Sc Computer Technology': 'BSC_CT',
            'B.Sc Costume Design & Fashion': 'BSC_FASHION',
            'B.Sc Data Science & Analytics': 'BSC_DS',
            'B.Sc Electronics and Communication Systems': 'ECE',
            'B.Sc Food Processing Technology & Management': 'BSC_FOOD',
            'B.Sc Information Technology': 'IT',
            'B.Sc Mathematics': 'MATHEMATICS',
            'B.Sc Microbiology': 'BSC_MICRO',
            'B.Sc Physics': 'PHYSICS',
            'B.Sc Visual Communication': 'BSC_VISCOM',
            'BA English Literature': 'ENGLISH',
            'BBA': 'BBA',
            'BBA CA': 'BBA_CA',
            'BBA Logistics': 'BBA_LOG',
            'BCA - Bachelor of Computer Applications': 'BCA',
            'M.Com CA': 'MCOM_CA',
            'M.Com International Business': 'MCOM_IB',
            'M.Sc Biotechnology': 'MSC_BIO',
        }
        
        # Create admin only if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                password='admin123',
                email='admin@hicas.ac.in',
                is_superuser=True,
                is_staff=True
            )
            UserProfile.objects.create(
                user=admin_user,
                employee_id='AD00001',
                full_name='System Administrator',
                role='admin',
                department='CSE',
                email_id='admin@hicas.ac.in',
                mobile_number='9876543210'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created admin'))
        else:
            self.stdout.write('✓ Admin already exists, skipping...')
        
        # Pre-hash password once for all users (much faster)
        hashed_password = make_password('faculty123')
        
        # Load faculty from CSV using bulk_create
        faculty_profiles = []
        faculty_users = []
        faculty_count = 0
        faculty_data = []  # Store faculty data for profile creation
        used_usernames = set()
        
        # Prefixes to remove from names (handles formats like "Dr.A.Name" or "Dr. Name")
        prefixes_to_remove = ['dr', 'ms', 'mr', 'mrs', 'prof']
        
        self.stdout.write('Loading faculty from CSV...')
        with open(faculty_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                faculty_count += 1
                dept_name = row['Department']
                faculty_name = row['Faculty Name']
                
                dept_code = dept_mapping.get(dept_name, 'CSE')
                
                # Create username from first and last name only
                # Handle formats like "Dr.A.Maheswari" or "Ms.Lalitha Parameswari"
                import re
                
                # First, remove common prefixes (Dr., Ms., Mr., etc.) at the start
                clean_name = faculty_name.strip()
                for prefix in prefixes_to_remove:
                    # Match prefix at start with optional dot, case insensitive
                    pattern = rf'^{prefix}\.?\s*'
                    clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)
                
                # Now split by dots and spaces to get name parts
                # Handle "A.Maheswari" -> ['A', 'Maheswari']
                parts = re.split(r'[\.\s]+', clean_name)
                
                # Filter out single letter initials and empty strings
                name_parts = [p for p in parts if len(p) > 1]
                
                # Get first and last name
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
                    base_username = f'{first_name}_{last_name}'.lower()
                elif len(name_parts) == 1:
                    base_username = name_parts[0].lower()
                else:
                    # Fallback: use all parts if no multi-char names found
                    base_username = '_'.join(parts).lower()
                
                # Remove any remaining special characters
                base_username = re.sub(r'[^a-z0-9_]', '', base_username)
                
                # Handle duplicates by adding a number
                username = base_username
                counter = 1
                while username in used_usernames:
                    username = f'{base_username}{counter}'
                    counter += 1
                used_usernames.add(username)
                
                # Store faculty data for later profile creation
                faculty_data.append({
                    'username': username,
                    'name': faculty_name,
                    'dept_code': dept_code
                })
                
                # Create user objects (don't save yet)
                user = User(
                    username=username,
                    password=hashed_password,
                    email=f'{username}@hicas.ac.in'
                )
                faculty_users.append(user)
                
                if faculty_count % 100 == 0:
                    self.stdout.write(f'  Loaded {faculty_count} faculty...')
        
        # Bulk create all users at once (ignore_conflicts skips existing usernames)
        self.stdout.write('Creating faculty users in database...')
        User.objects.bulk_create(faculty_users, batch_size=500, ignore_conflicts=True)
        
        # Create profiles using stored faculty data (skip if profile exists)
        self.stdout.write('Creating faculty profiles...')
        profiles_to_create = []
        
        for idx, fdata in enumerate(faculty_data):
            user = User.objects.get(username=fdata['username'])
            
            profile = UserProfile(
                user=user,
                employee_id=f'FC{idx+1:05d}',
                full_name=fdata['name'],
                role='faculty',
                department=fdata['dept_code'],
                email_id=f'{fdata["username"]}@hicas.ac.in',
                mobile_number=f'98765{10000 + idx+1}'
            )
            profiles_to_create.append(profile)
            
            if len(profiles_to_create) % 100 == 0:
                self.stdout.write(f'  Prepared {len(profiles_to_create)} profiles...')
        
        UserProfile.objects.bulk_create(profiles_to_create, batch_size=500, ignore_conflicts=True)
        faculty_profiles = list(UserProfile.objects.filter(role='faculty'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(faculty_profiles)} faculty from CSV'))
        
        # Pre-hash student password
        student_hashed_password = make_password('student123')
        
        # Load students from CSV using bulk_create
        student_users = []
        student_count = 0
        
        self.stdout.write('Loading students from CSV...')
        with open(students_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                student_count += 1
                reg_no = row['RegisterNumber']
                username = reg_no  # Use registration number as username
                
                user = User(
                    username=username,
                    password=student_hashed_password,
                    email=f'{reg_no}@student.hicas.ac.in'
                )
                student_users.append(user)
                
                if student_count % 500 == 0:
                    self.stdout.write(f'  Loaded {student_count} students...')
        
        # Bulk create student users (ignore_conflicts skips existing usernames)
        self.stdout.write('Creating student users in database...')
        User.objects.bulk_create(student_users, batch_size=1000, ignore_conflicts=True)
        
        # Create student profiles
        self.stdout.write('Creating student profiles...')
        with open(students_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # Get all student users ordered by username (registration number)
            student_users_dict = {u.username: u for u in User.objects.filter(username__regex=r'^\d')}
            profiles_to_create = []
            
            for idx, row in enumerate(reader):
                reg_no = row['RegisterNumber']
                name = row['Student Name']
                dept_name = row['Department']
                year = int(row['Year'])
                dept_code = dept_mapping.get(dept_name, 'CSE')
                
                user = student_users_dict.get(reg_no)
                if not user:
                    continue
                
                profile = UserProfile(
                    user=user,
                    employee_id=f'ST{idx+1:05d}',
                    full_name=name,
                    role='student',
                    department=dept_code,
                    register_number=reg_no,
                    year_of_study=year,
                    email_id=f'{reg_no}@student.hicas.ac.in',
                    mobile_number=f'99999{10000 + idx+1}'
                )
                profiles_to_create.append(profile)
                
                if len(profiles_to_create) % 500 == 0:
                    self.stdout.write(f'  Prepared {len(profiles_to_create)} profiles...')
        
        UserProfile.objects.bulk_create(profiles_to_create, batch_size=1000, ignore_conflicts=True)
        student_profiles = list(UserProfile.objects.filter(role='student'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(student_profiles)} students from CSV'))
        
        # Create internship applications with real HICAS placement companies
        companies_with_roles = [
            # Top recruiters from HICAS 2024-2025
            ('Zoho Corporation', ['Software Developer', 'Web Developer', 'Technical Support Engineer']),
            ('Ramco Cements Ltd.', ['Management Trainee', 'Quality Control Analyst', 'Marketing Executive']),
            ('Verzeo Edutech', ['Content Developer', 'Educational Consultant', 'Training Coordinator']),
            ('Digital Intelligence Systems (DISYS)', ['Data Analyst', 'Business Intelligence Developer', 'Systems Engineer']),
            ('QSPIDERS', ['Software Testing Engineer', 'Automation Tester', 'Quality Analyst']),
            ('Accenture', ['Associate Software Engineer', 'Business Analyst', 'Application Developer']),
            ('TCS (Tata Consultancy Services)', ['Assistant Systems Engineer', 'Digital Analyst', 'IT Consultant']),
            ('Infosys Limited', ['Systems Engineer', 'Technology Analyst', 'Digital Specialist']),
            ('Wipro', ['Project Engineer', 'Software Developer', 'Business Analyst']),
            ('Capgemini', ['Analyst', 'Senior Analyst', 'Consultant']),
            ('Cognizant', ['Programmer Analyst', 'Associate Projects', 'Process Executive']),
            ('L&T Infotech', ['Software Engineer', 'Graduate Engineer Trainee', 'Systems Analyst']),
            ('Hexaware Technologies', ['Software Developer', 'Quality Analyst', 'Technical Support']),
            ('KGISL', ['Software Trainee', 'Junior Developer', 'Tech Support Executive']),
            
            # Banking & Finance
            ('HDFC Bank', ['Personal Banker', 'Relationship Manager', 'Sales Officer']),
            ('ESAF Small Finance Bank', ['Relationship Officer', 'Branch Operations', 'Customer Service']),
            ('ICICI Bank', ['Probationary Officer', 'Sales Executive', 'Credit Analyst']),
            ('Bajaj Allianz Life Insurance', ['Insurance Advisor', 'Sales Manager', 'Claims Processor']),
            ('SBI Cards', ['Sales Officer', 'Customer Service Executive', 'Collections Officer']),
            ('Policy Bazaar', ['Insurance Advisor', 'Sales Consultant', 'Customer Relationship Manager']),
            
            # Analytics & Consulting
            ('Cognizoft Analytics', ['Data Analyst', 'Business Intelligence Analyst', 'Research Analyst']),
            ('Neeyamo Enterprise Solutions', ['HR Analyst', 'Payroll Analyst', 'Operations Associate']),
            ('Birlasoft', ['Associate Consultant', 'Software Engineer', 'Business Analyst']),
            ('Value Momentum', ['Financial Analyst', 'Business Analyst', 'Risk Analyst']),
            
            # Manufacturing & Industrial
            ('Chettinadu Cement', ['Management Trainee', 'Quality Control Executive', 'Production Engineer']),
            ('Wildcraft India', ['Retail Executive', 'Marketing Coordinator', 'Supply Chain Analyst']),
            ('Sanmina', ['Production Trainee', 'Quality Engineer', 'Manufacturing Associate']),
            ('Foxconn', ['Production Executive', 'Quality Control', 'Process Engineer']),
            ('Pegatron', ['Manufacturing Engineer', 'Quality Assurance', 'Production Planner']),
            
            # BPO & Customer Service
            ('Sutherland', ['Customer Service Representative', 'Technical Support', 'Process Associate']),
            ('Vee Technologies', ['Data Entry Operator', 'Process Associate', 'Quality Analyst']),
            ('Patra India BPO Services', ['Process Associate', 'Quality Analyst', 'Team Lead']),
            ('24.7 AI Company', ['Customer Support Associate', 'Technical Support Engineer', 'Process Trainer']),
            ('Careernet Technologies', ['Recruitment Consultant', 'HR Executive', 'Talent Acquisition']),
            
            # IT Services & Development
            ('Mallow Technologies', ['Full Stack Developer', 'Backend Developer', 'DevOps Engineer']),
            ('Codingmart Technologies', ['Software Developer', 'Mobile App Developer', 'UI/UX Developer']),
            ('Tringapps Research Labs', ['Research Associate', 'Software Developer', 'Testing Engineer']),
            ('Prolific Systems & Technologies', ['Software Engineer', 'Systems Administrator', 'Network Engineer']),
            ('Kriya IT', ['Junior Developer', 'Technical Support', 'Systems Analyst']),
            ('RND Soft', ['Software Developer', 'Web Developer', 'Quality Analyst']),
            ('Chain-Sys India', ['Developer Trainee', 'Database Administrator', 'Support Engineer']),
            ('Orion India Systems', ['Software Engineer', 'Application Developer', 'Technical Consultant']),
            
            # Specialized Services
            ('Zifo RnD Solutions', ['Research Associate', 'Laboratory Technician', 'Clinical Data Analyst']),
            ('IDC Engineering India', ['Design Engineer', 'CAD Technician', 'Project Coordinator']),
            ('Albatroz Solutions', ['Business Development Executive', 'Marketing Analyst', 'Sales Coordinator']),
            ('Literact Fintech Solutions', ['Financial Analyst', 'Product Analyst', 'Operations Executive']),
            ('EPI Source India', ['Clinical Data Management', 'Medical Coding', 'Quality Analyst']),
            
            # Education & Training
            ('Unschool Educational Consultant', ['Academic Counselor', 'Content Writer', 'Training Coordinator']),
            ('Skill Forge', ['Trainer', 'Curriculum Developer', 'Training Coordinator']),
            ('Focus Edumatics', ['Educational Consultant', 'Content Developer', 'Academic Coordinator']),
            ('EdVedha', ['Subject Matter Expert', 'Content Developer', 'Academic Counselor']),
            ('Shree Vari Educational Groups', ['Teacher', 'Academic Coordinator', 'Counselor']),
            
            # Logistics & Operations
            ('Gati - Kintetsu Express', ['Operations Executive', 'Supply Chain Coordinator', 'Logistics Analyst']),
            ('Lakshmi Corporate Services', ['Operations Manager', 'Business Analyst', 'Client Relations']),
        ]
        
        modes = ['online', 'offline', 'hybrid']
        statuses = ['pending_faculty', 'pending_faculty', 'approved', 'approved', 'rejected_faculty']
        
        applications = []
        for student in student_profiles:
            if student.year_of_study >= 3 and random.random() < 0.5:
                # Assign faculty from same department
                dept_faculty = [f for f in faculty_profiles if f.department == student.department]
                assigned_faculty = random.choice(dept_faculty) if dept_faculty else random.choice(faculty_profiles)
                
                # Select company and matching role
                company_name, roles = random.choice(companies_with_roles)
                role = random.choice(roles)
                
                # Start from September 2025 (internship program starts)
                from datetime import date
                base_start = date(2025, 9, 1)  # Sept 1, 2025
                # Random start within first 8 weeks of Sept-Oct 2025
                start_date = base_start + timedelta(days=random.randint(0, 56))
                duration = random.randint(60, 120)  # 60-120 days internship
                end_date = start_date + timedelta(days=duration)
                status = random.choice(statuses)
                
                app = InternshipApplication.objects.create(
                    student=student,
                    assigned_faculty=assigned_faculty,
                    company_name=company_name,
                    internship_domain=role,
                    internship_mode=random.choice(modes),
                    start_date=start_date,
                    end_date=end_date,
                    application_status=status,
                    faculty_remarks='Application reviewed' if status != 'pending_faculty' else '',
                    approval_date=start_date if status == 'approved' else None
                )
                applications.append(app)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(applications)} internship applications'))
        
        # Create weekly logs and progress proofs
        logs_count = 0
        proofs_count = 0
        
        # Sample faculty feedback messages
        feedback_messages = [
            'Good progress! Keep up the excellent work.',
            'Nice effort. Focus more on documentation.',
            'Excellent work this week. Well structured.',
            'Satisfactory progress. Try to be more detailed next time.',
            'Great job! Your technical skills are improving.',
            'Well done. Keep learning new technologies.',
            'Good work on the project. Continue with the momentum.',
            'Impressive progress! Your dedication shows.',
        ]
        
        for app in applications:
            if app.application_status == 'approved':
                # Calculate weeks based on internship duration (at least 8-12 weeks for most)
                total_days = (app.end_date - app.start_date).days
                max_weeks = min(12, max(4, total_days // 7))  # 4 to 12 weeks
                num_weeks = random.randint(max(4, max_weeks - 4), max_weeks)  # Most weeks submitted
                
                for week in range(1, num_weeks + 1):
                    # Earlier weeks are more likely to be reviewed
                    is_reviewed = random.random() < (0.95 - (week * 0.05))
                    review_status = 'reviewed' if is_reviewed else 'pending'
                    
                    # Submission date based on internship start + week number
                    submission_date = app.start_date + timedelta(days=week * 7)
                    
                    # Make review_date timezone-aware
                    from django.utils import timezone
                    review_dt = None
                    if is_reviewed:
                        from datetime import datetime as dt
                        review_date_naive = dt.combine(submission_date + timedelta(days=random.randint(1, 3)), dt.min.time())
                        review_dt = timezone.make_aware(review_date_naive)
                    
                    log = WeeklyLog.objects.create(
                        student=app.student,
                        application=app,
                        week_number=week,
                        work_summary=f'Week {week}: Completed assigned tasks including development, testing, and documentation work at {app.company_name}.',
                        skills_learned='Technical skills, teamwork, problem solving, communication',
                        hours_worked=random.randint(35, 45),
                        log_status='reviewed' if is_reviewed else 'submitted',
                        review_status=review_status,
                        submission_date=submission_date,
                        faculty_feedback=random.choice(feedback_messages) if is_reviewed else '',
                        reviewed_by=app.assigned_faculty if is_reviewed else None,
                        review_date=review_dt
                    )
                    logs_count += 1
                
                proof_types = ['work_sample', 'attendance', 'project_milestone', 'task_completion']
                for _ in range(random.randint(2, 4)):
                    ProgressProof.objects.create(
                        application=app,
                        student=app.student,
                        proof_type=random.choice(proof_types),
                        title=f'Progress proof - {app.company_name}',
                        description='Work evidence during internship',
                        verification_status=random.choice(['pending', 'verified', 'verified']),
                        verified_by=app.assigned_faculty if random.random() > 0.3 else None
                    )
                    proofs_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {logs_count} weekly logs'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {proofs_count} progress proofs'))
        
        self.stdout.write(self.style.SUCCESS('\n=== CSV data loaded into PostgreSQL ==='))
        self.stdout.write(self.style.SUCCESS('Admin: admin/admin123'))
        self.stdout.write(self.style.SUCCESS(f'Faculty: Use faculty name as username (e.g., john_smith) / faculty123'))
        self.stdout.write(self.style.SUCCESS(f'Students: Use Registration Number as username / student123'))
        self.stdout.write(self.style.SUCCESS(f'Example Faculty: {faculty_data[0]["username"]} / faculty123'))
        self.stdout.write(self.style.SUCCESS(f'Example Student: 82302630101 / student123'))
