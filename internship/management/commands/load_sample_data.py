from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from internship.models import UserProfile, InternshipApplication
from datetime import datetime, timedelta
import random
import csv
import os

class Command(BaseCommand):
    help = 'Load sample data into the database from CSV files'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading data from CSV files...')
        
        # Clear existing data
        User.objects.all().delete()
        
        # Get the project root directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # Create only ONE admin
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
        
        self.stdout.write(self.style.SUCCESS('Created 1 admin: admin/admin123'))
        
        # Department mapping from CSV to model choices
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
        
        # Load faculty from CSV
        faculty_csv = os.path.join(base_dir, 'hicas_faculty_data.csv')
        faculty_profiles = []
        faculty_count = 0
        
        try:
            with open(faculty_csv, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    faculty_count += 1
                    dept_name = row['Department']
                    faculty_name = row['Faculty Name']
                    
                    # Get department code
                    dept_code = dept_mapping.get(dept_name, 'CSE')
                    
                    # Create username from name
                    username = f"faculty{faculty_count}"
                    
                    user = User.objects.create_user(
                        username=username,
                        password='faculty123',
                        email=f"{username}@hicas.ac.in"
                    )
                    profile = UserProfile.objects.create(
                        user=user,
                        employee_id=f"FC{faculty_count:05d}",
                        full_name=faculty_name,
                        role='faculty',
                        department=dept_code,
                        email_id=f"{username}@hicas.ac.in",
                        mobile_number=f"98765{random.randint(10000, 99999)}"
                    )
                    faculty_profiles.append(profile)
            
            self.stdout.write(self.style.SUCCESS(f'Created {faculty_count} faculty members from CSV'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Faculty CSV file not found at {faculty_csv}'))
            return
        
        # Load students from CSV
        students_csv = os.path.join(base_dir, 'hicas_students_simulated.csv')
        student_profiles = []
        student_count = 0
        
        try:
            with open(students_csv, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    student_count += 1
                    dept_name = row['Department']
                    student_name = row['Student Name']
                    register_number = row['RegisterNumber']
                    email = row['Email']
                    year = int(row['Year'])
                    
                    # Get department code
                    dept_code = dept_mapping.get(dept_name, 'CSE')
                    
                    # Create username from register number
                    username = f"student{student_count}"
                    
                    user = User.objects.create_user(
                        username=username,
                        password='student123',
                        email=email
                    )
                    profile = UserProfile.objects.create(
                        user=user,
                        employee_id=f"ST{student_count:05d}",
                        full_name=student_name,
                        role='student',
                        department=dept_code,
                        register_number=register_number,
                        year_of_study=year,
                        email_id=email,
                        mobile_number=f"98765{random.randint(10000, 99999)}"
                    )
                    student_profiles.append(profile)
            
            self.stdout.write(self.style.SUCCESS(f'Created {student_count} students from CSV'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Students CSV file not found at {students_csv}'))
            return
        
        # Create sample internship applications for some students (10% of students)
        self.stdout.write('Creating sample internship applications...')
        
        companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Netflix', 'Adobe',
            'IBM', 'Oracle', 'SAP', 'Infosys', 'TCS', 'Wipro', 'Cognizant',
            'Accenture', 'Deloitte', 'PwC', 'EY', 'KPMG', 'Intel', 'Cisco'
        ]
        
        domains = [
            'Software Development', 'Data Analysis', 'Web Development', 'Mobile App Development',
            'AI & Machine Learning', 'Cloud Computing', 'Cybersecurity', 'Business Analysis',
            'Digital Marketing', 'UI/UX Design', 'Quality Assurance', 'DevOps', 'Database Administration',
            'Network Administration', 'Content Writing', 'Graphic Design', 'Video Editing'
        ]
        
        modes = ['online', 'offline', 'hybrid']
        statuses = ['pending_faculty', 'approved', 'approved', 'rejected_faculty']
        
        # Create applications for 10% of students
        sample_size = max(50, int(len(student_profiles) * 0.1))
        selected_students = random.sample(student_profiles, min(sample_size, len(student_profiles)))
        
        applications = []
        for student in selected_students:
            start_date = datetime.now().date() - timedelta(days=random.randint(30, 180))
            duration = random.randint(60, 120)
            end_date = start_date + timedelta(days=duration)
            
            # Assign faculty from the same department
            faculty_in_dept = [f for f in faculty_profiles if f.department == student.department]
            if faculty_in_dept:
                # Find faculty with least assignments
                faculty_with_counts = [(f, InternshipApplication.objects.filter(assigned_faculty=f).count()) for f in faculty_in_dept]
                assigned_faculty = min(faculty_with_counts, key=lambda x: x[1])[0]
            else:
                assigned_faculty = random.choice(faculty_profiles) if faculty_profiles else None
            
            status = random.choice(statuses)
            
            app = InternshipApplication.objects.create(
                student=student,
                assigned_faculty=assigned_faculty,
                company_name=random.choice(companies),
                internship_domain=random.choice(domains),
                internship_mode=random.choice(modes),
                start_date=start_date,
                end_date=end_date,
                application_status=status,
                faculty_remarks='Application reviewed and processed' if status != 'pending_faculty' else '',
                approval_date=start_date if status == 'approved' else None
            )
            applications.append(app)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(applications)} internship applications'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Data loading completed successfully! ==='))
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  - 1 Admin')
        self.stdout.write(f'  - {faculty_count} Faculty members')
        self.stdout.write(f'  - {student_count} Students')
        self.stdout.write(f'  - {len(applications)} Internship applications')
        self.stdout.write(f'\n🔑 Login credentials:')
        self.stdout.write(f'  Admin: admin / admin123')
        self.stdout.write(f'  Faculty: faculty1 to faculty{faculty_count} / faculty123')
        self.stdout.write(f'  Students: student1 to student{student_count} / student123')
