from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from internship.models import UserProfile, InternshipApplication, WeeklyLog, InternshipCompletion, ProgressProof
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Load HICAS student and faculty data directly into database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading HICAS data...')
        
        # Clear existing data
        User.objects.all().delete()
        
        # Create ONE admin
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
        self.stdout.write(self.style.SUCCESS('✓ Created admin: admin/admin123'))
        
        # Faculty data (40 faculty members)
        faculty_data = [
            # B.Com Accounting & Finance
            ('BCOM_AF', 'Dr.A.Maheswari', 'Assistant Professor'),
            ('BCOM_AF', 'Dr.D.Sasikala', 'Professor & Head'),
            ('BCOM_AF', 'Dr.K.Renugadevi', 'Assistant Professor'),
            ('BCOM_AF', 'Dr.S.Swathi', 'Assistant Professor'),
            ('BCOM_AF', 'Dr.T.Kavitha', 'Assistant Professor'),
            ('BCOM_AF', 'Ms.Lalitha Parameswari', 'Assistant Professor'),
            
            # B.Com CA
            ('BCOM_CA', 'DR.S.Tamilarasi', 'Associate Professor'),
            ('BCOM_CA', 'Dr.G.Gunavelan', 'Professor'),
            ('BCOM_CA', 'Dr.K.Latha', 'Professor'),
            ('BCOM_CA', 'Dr.K.Mangaiyarkkarasi', 'Assistant Professor'),
            ('BCOM_CA', 'Dr.M.Mahalakshmi', 'Professor'),
            ('BCOM_CA', 'Dr.M.Parameswari', 'Professor'),
            ('BCOM_CA', 'Dr.M.S.Loganathan', 'Professor & Head'),
            ('BCOM_CA', 'Dr.P.Nithya Devi', 'Assistant Professor'),
            ('BCOM_CA', 'Dr.S.Santhini', 'Assistant Professor'),
            ('BCOM_CA', 'Dr.T.Deepa', 'Associate Professor'),
            ('BCOM_CA', 'Mr.P.Jeevanandham', 'Assistant Professor'),
            ('BCOM_CA', 'Mrs.W.Mercy Kamalia', 'Assistant Professor'),
            
            # Other departments
            ('CSE', 'Dr.R.Kumar', 'Professor'),
            ('CSE', 'Dr.S.Priya', 'Assistant Professor'),
            ('IT', 'Dr.M.Anand', 'Associate Professor'),
            ('IT', 'Dr.K.Lakshmi', 'Assistant Professor'),
            ('ECE', 'Dr.V.Ramesh', 'Professor'),
            ('ECE', 'Dr.P.Kavitha', 'Assistant Professor'),
            ('MATHEMATICS', 'Dr.A.Ganesan', 'Professor'),
            ('MATHEMATICS', 'Dr.S.Meena', 'Assistant Professor'),
            ('PHYSICS', 'Dr.T.Venkatesh', 'Professor'),
            ('PHYSICS', 'Dr.R.Divya', 'Associate Professor'),
            ('ENGLISH', 'Dr.L.Mary', 'Professor'),
            ('ENGLISH', 'Dr.K.Priya', 'Assistant Professor'),
            ('BBA', 'Dr.N.Suresh', 'Professor'),
            ('BBA', 'Dr.M.Sangeetha', 'Assistant Professor'),
            ('BCA', 'Dr.P.Mohan', 'Associate Professor'),
            ('BCA', 'Dr.S.Deepa', 'Assistant Professor'),
            ('BSC_BIO', 'Dr.K.Radhika', 'Professor'),
            ('BSC_BIO', 'Dr.M.Karthik', 'Assistant Professor'),
            ('BSC_DS', 'Dr.V.Arun', 'Associate Professor'),
            ('BSC_DS', 'Dr.R.Nisha', 'Assistant Professor'),
            ('BSC_AI', 'Dr.S.Prakash', 'Professor'),
            ('BSC_AI', 'Dr.L.Sindhu', 'Assistant Professor'),
        ]
        
        faculty_profiles = []
        for i, (dept, name, designation) in enumerate(faculty_data, 1):
            username = f'faculty{i}'
            user = User.objects.create_user(
                username=username,
                password='faculty123',
                email=f'{username}@hicas.ac.in'
            )
            profile = UserProfile.objects.create(
                user=user,
                employee_id=f'FC{i:05d}',
                full_name=name,
                role='faculty',
                department=dept,
                email_id=f'{username}@hicas.ac.in',
                mobile_number=f'98765{10000 + i}'
            )
            faculty_profiles.append(profile)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(faculty_profiles)} faculty members'))
        
        # Student data (324 students)
        students_data = [
            # Format: (register_no, name, department, year)
            ('22PCAF01', 'ABINAYA P', 'BCOM_AF', 3),
            ('22PCAF02', 'ABITHA V', 'BCOM_AF', 3),
            ('22PCAF03', 'ABITHA L', 'BCOM_AF', 3),
            ('22PCAF04', 'AFNA SHERIN T', 'BCOM_AF', 3),
            ('22PCAF05', 'AISHWARYA S', 'BCOM_AF', 3),
            ('23PCAF01', 'AKSHAYA R', 'BCOM_AF', 2),
            ('23PCAF02', 'AKSHAYA V', 'BCOM_AF', 2),
            ('23PCAF03', 'ALFI ROZI K', 'BCOM_AF', 2),
            ('24PCAF01', 'AMIRTHAVARSHINI S', 'BCOM_AF', 1),
            ('24PCAF02', 'AMRITHAVALLI R', 'BCOM_AF', 1),
            
            # B.Com CA students
            ('22PCCA001', 'AARTHI K', 'BCOM_CA', 3),
            ('22PCCA002', 'ABARNA S', 'BCOM_CA', 3),
            ('22PCCA003', 'ABINAYA M', 'BCOM_CA', 3),
            ('22PCCA004', 'ADITHYA VARSHINI M S', 'BCOM_CA', 3),
            ('22PCCA005', 'AFRIN Z', 'BCOM_CA', 3),
            ('23PCCA001', 'AGALYA R', 'BCOM_CA', 2),
            ('23PCCA002', 'AISHWARYA M', 'BCOM_CA', 2),
            ('24PCCA001', 'AJITHA B', 'BCOM_CA', 1),
            ('24PCCA002', 'AKSHARA V', 'BCOM_CA', 1),
            
            # B.Sc Computer Science
            ('22PSCS001', 'AKASH R', 'CSE', 3),
            ('22PSCS002', 'AKHILA S', 'CSE', 3),
            ('22PSCS003', 'AKSHAYA M', 'CSE', 3),
            ('23PSCS001', 'ALANKAR P', 'CSE', 2),
            ('23PSCS002', 'ALIA FATHIMA N', 'CSE', 2),
            ('24PSCS001', 'AMALA MARY K', 'CSE', 1),
            ('24PSCS002', 'AMIRTHAVARSHINI J', 'CSE', 1),
            
            # B.Sc IT
            ('22PSIT001', 'ANANDHAVALLI K', 'IT', 3),
            ('22PSIT002', 'ANANNYA S', 'IT', 3),
            ('23PSIT001', 'ANANYA SRIRAM', 'IT', 2),
            ('23PSIT002', 'ANGEL JENIFER S', 'IT', 2),
            ('24PSIT001', 'ANGELINA ANTO S', 'IT', 1),
            
            # BBA
            ('22PBBA001', 'ANISHKA K', 'BBA', 3),
            ('22PBBA002', 'ANJALI M', 'BBA', 3),
            ('23PBBA001', 'ANNAPOORANI R', 'BBA', 2),
            ('24PBBA001', 'ANSHIKA AGARWAL', 'BBA', 1),
            
            # BCA
            ('22PBCA001', 'ANUSHKA M', 'BCA', 3),
            ('22PBCA002', 'ANUSUYA P', 'BCA', 3),
            ('23PBCA001', 'ARCHANA S', 'BCA', 2),
            ('24PBCA001', 'AROKIYA MARY J', 'BCA', 1),
            
            # B.Sc Mathematics
            ('22PSMA001', 'ARTHI M', 'MATHEMATICS', 3),
            ('22PSMA002', 'ARUNDHATHI R', 'MATHEMATICS', 3),
            ('23PSMA001', 'ASWINI S', 'MATHEMATICS', 2),
            ('24PSMA001', 'ATHIRA K', 'MATHEMATICS', 1),
            
            # B.Sc Physics
            ('22PSPH001', 'AYSHA NISHA A', 'PHYSICS', 3),
            ('23PSPH001', 'BANUPRIYA M', 'PHYSICS', 2),
            ('24PSPH001', 'BHAGYA S', 'PHYSICS', 1),
            
            # BA English
            ('22PAEN001', 'BHAGYA LAKSHMI R', 'ENGLISH', 3),
            ('23PAEN001', 'BHAIRAVI S', 'ENGLISH', 2),
            ('24PAEN001', 'BHAVANA M', 'ENGLISH', 1),
            
            # Add more students (continuing to reach 324 total)
            # Adding diverse names across departments
        ]
        
        # Generate more students to reach 324 total
        first_names = ['Priya', 'Divya', 'Kavya', 'Sneha', 'Keerthi', 'Lakshmi', 'Meera', 'Nisha', 'Pooja', 'Radha',
                       'Sahana', 'Tanvi', 'Uma', 'Varsha', 'Yamini', 'Aishwarya', 'Bhavana', 'Chitra', 'Deepa', 'Geetha',
                       'Harini', 'Indira', 'Jaya', 'Kamala', 'Lalitha', 'Malini', 'Nandini', 'Pavithra', 'Ramya', 'Shalini']
        last_names = ['Kumar', 'Sharma', 'Reddy', 'Patel', 'Krishnan', 'Nair', 'Iyer', 'Gupta', 'Singh', 'Mehta']
        
        all_depts = ['BCOM_AF', 'BCOM_CA', 'CSE', 'IT', 'BBA', 'BCA', 'MATHEMATICS', 'PHYSICS', 'ENGLISH',
                     'BSC_BIO', 'BSC_DS', 'BSC_AI', 'ECE', 'BCOM_CS', 'BCOM_PA']
        
        # Add remaining students
        for i in range(len(students_data) + 1, 325):
            dept = random.choice(all_depts)
            year = random.choice([1, 2, 3, 4])
            name = f'{random.choice(first_names)} {random.choice(last_names)}'
            reg_no = f'{22 + (4-year):02d}P{dept[:3]}{i:03d}'
            students_data.append((reg_no, name, dept, year))
        
        student_profiles = []
        for i, (reg_no, name, dept, year) in enumerate(students_data, 1):
            username = f'student{i}'
            user = User.objects.create_user(
                username=username,
                password='student123',
                email=f'{username}@student.hicas.ac.in'
            )
            profile = UserProfile.objects.create(
                user=user,
                employee_id=f'ST{i:05d}',
                full_name=name,
                role='student',
                department=dept,
                register_number=reg_no,
                year_of_study=year,
                email_id=f'{username}@student.hicas.ac.in',
                mobile_number=f'99999{10000 + i}'
            )
            student_profiles.append(profile)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(student_profiles)} students'))
        
        # Create internship applications for final year students
        companies = [
            'TCS', 'Infosys', 'Wipro', 'Cognizant', 'Accenture', 'Deloitte', 'EY', 'KPMG', 'PwC',
            'Amazon', 'Google', 'Microsoft', 'IBM', 'Oracle', 'SAP', 'Cisco', 'Intel',
            'ICICI Bank', 'HDFC Bank', 'Axis Bank', 'Kotak Mahindra', 'State Bank of India',
            'Apollo Hospitals', 'Fortis Healthcare', 'Max Healthcare', 'Manipal Hospitals'
        ]
        
        domains = [
            'Software Development', 'Data Analysis', 'Web Development', 'Mobile App Development',
            'Cybersecurity', 'Cloud Computing', 'AI/ML Engineering', 'DevOps',
            'Accounting & Audit', 'Financial Analysis', 'Tax Consulting', 'Banking Operations',
            'Business Analysis', 'Marketing', 'HR Management', 'Operations Management',
            'Research & Development', 'Quality Assurance', 'Technical Support'
        ]
        
        modes = ['online', 'offline', 'hybrid']
        statuses = ['pending_faculty', 'pending_faculty', 'approved', 'approved', 'rejected_faculty']
        
        # Create applications for 3rd and 4th year students
        applications = []
        for student in student_profiles:
            if student.year_of_study >= 3 and random.random() < 0.6:  # 60% of senior students apply
                # Assign faculty from same department
                dept_faculty = [f for f in faculty_profiles if f.department == student.department]
                assigned_faculty = random.choice(dept_faculty) if dept_faculty else random.choice(faculty_profiles)
                
                start_date = datetime.now().date() - timedelta(days=random.randint(30, 180))
                duration = random.randint(60, 120)
                end_date = start_date + timedelta(days=duration)
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
                    faculty_remarks='Application reviewed' if status != 'pending_faculty' else '',
                    approval_date=start_date if status == 'approved' else None
                )
                applications.append(app)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(applications)} internship applications'))
        
        # Create some weekly logs and progress proofs for approved applications
        logs_count = 0
        proofs_count = 0
        
        for app in applications:
            if app.application_status == 'approved':
                # Create 2-5 weekly logs
                for week in range(1, random.randint(3, 6)):
                    WeeklyLog.objects.create(
                        student=app.student,
                        application=app,
                        week_number=week,
                        work_summary=f'Week {week} activities completed successfully',
                        skills_learned='Problem solving, teamwork, technical skills',
                        hours_worked=random.randint(35, 45),
                        log_status=random.choice(['submitted', 'reviewed']),
                        faculty_feedback='Good progress' if random.random() > 0.5 else ''
                    )
                    logs_count += 1
                
                # Create 2-4 progress proofs
                proof_types = ['work_sample', 'attendance', 'project_milestone', 'task_completion']
                for _ in range(random.randint(2, 5)):
                    ProgressProof.objects.create(
                        application=app,
                        student=app.student,
                        proof_type=random.choice(proof_types),
                        title=f'Progress proof for {app.company_name}',
                        description='Evidence of work completed during internship',
                        verification_status=random.choice(['pending', 'verified', 'verified']),
                        verified_by=app.assigned_faculty if random.random() > 0.3 else None,
                        faculty_remarks='Verified and approved' if random.random() > 0.5 else ''
                    )
                    proofs_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {logs_count} weekly logs'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created {proofs_count} progress proofs'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Data loading complete! ==='))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write(self.style.SUCCESS('Admin: admin/admin123'))
        self.stdout.write(self.style.SUCCESS('Faculty: faculty1-faculty40 / faculty123'))
        self.stdout.write(self.style.SUCCESS('Students: student1-student324 / student123'))
