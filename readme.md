SmartIntern - Complete Setup Guide
📋 Quick Setup Instructions
Step 1: Create Project Structure
bash
# Create main project directory
mkdir smartintern_project
cd smartintern_project

# Create Django project
django-admin startproject smartintern .

# Create internship app
python manage.py startapp internship

# Create required directories
mkdir -p internship/management/commands
mkdir -p internship/templates
mkdir -p internship/static/css
mkdir -p internship/static/js
mkdir -p media/offer_letters
mkdir -p media/noc_files
mkdir -p media/completion_certificates
Step 2: Create requirements.txt
txt
Django==4.2.7
pandas==2.1.3
matplotlib==3.8.2
reportlab==4.0.7
openpyxl==3.1.2
Pillow==10.1.0
Step 3: Install Dependencies
bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
Step 4: Configure Django Settings
Update smartintern/settings.py with the code provided in the first artifact.

Step 5: Create All Files
Copy the code from the artifacts into their respective files:

Models → internship/models.py
Forms → internship/forms.py
Views → internship/views.py
URLs → internship/urls.py and smartintern/urls.py
Decorators → internship/decorators.py
Admin → internship/admin.py
Templates → All HTML files in internship/templates/
Sample Data → internship/management/commands/load_sample_data.py
Step 6: Create Empty init.py Files
bash
# Make management/commands a Python package
touch internship/management/__init__.py
touch internship/management/commands/__init__.py
Step 7: Run Migrations
bash
python manage.py makemigrations
python manage.py migrate
Step 8: Load Sample Data
bash
python manage.py load_sample_data
Step 9: Create Superuser (Optional)
bash
python manage.py createsuperuser
Step 10: Run Development Server
bash
python manage.py runserver
Access the application at: http://localhost:8000

🔐 Login Credentials
Admin Accounts
Username: admin1 | Password: admin123
Username: admin2 | Password: admin123
Username: admin3 | Password: admin123
Faculty Accounts
Username: faculty1 | Password: faculty123
Username: faculty2 | Password: faculty123
Username: faculty3 | Password: faculty123
Username: faculty4 | Password: faculty123
Username: faculty5 | Password: faculty123
Student Accounts
Username: student1 | Password: student123
Username: student2 | Password: student123
... up to student10
📁 Complete Project Structure
smartintern_project/
│
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3 (created after migration)
│
├── smartintern/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── internship/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── decorators.py
│   ├── tests.py
│   │
│   ├── migrations/
│   │   └── __init__.py
│   │
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── load_sample_data.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── student_dashboard.html
│   │   ├── faculty_dashboard.html
│   │   ├── admin_dashboard.html
│   │   ├── apply_internship.html
│   │   ├── weekly_log.html
│   │   ├── approval_page.html
│   │   ├── review_log.html
│   │   ├── completion_form.html
│   │   └── analytics.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
│
└── media/
    ├── offer_letters/
    ├── noc_files/
    └── completion_certificates/
🎯 Feature Testing Guide
1. Test Student Workflow
Login as student1 / student123
Click "Apply Internship"
Fill the form:
Company: Google
Domain: Web Development
Mode: Online
Dates: Select appropriate dates
Upload a dummy PDF as offer letter
Submit application
Check status on dashboard
2. Test Faculty Workflow
Login as faculty1 / faculty123
View pending applications
Click "Review" on any application
Approve or reject with remarks
Check recent logs section
Review submitted logs
3. Test Admin Workflow
Login as admin1 / admin123
View system statistics
Click "View Analytics"
Check domain and company charts
Download PDF report
Download Excel report
4. Test Weekly Log Submission
Login as student
Find an approved application
Click "Add Log"
Fill weekly log details:
Week number
Work summary
Skills learned
Hours worked
Submit and verify
5. Test Completion Certificate
Login as student with completed internship
Click "Complete" on approved application
Upload completion certificate
System automatically calculates score
Faculty can verify from their dashboard
🔧 Troubleshooting
Issue: Module not found errors
Solution: Ensure all __init__.py files exist:

bash
touch internship/__init__.py
touch internship/management/__init__.py
touch internship/management/commands/__init__.py
Issue: Template not found
Solution: Check that templates are in internship/templates/ directory and APP_DIRS is True in settings.py

Issue: Static files not loading
Solution:

bash
python manage.py collectstatic
Issue: Database errors
Solution: Delete db.sqlite3 and migrations, then:

bash
rm -rf internship/migrations
python manage.py makemigrations internship
python manage.py migrate
python manage.py load_sample_data
Issue: File upload errors
Solution: Ensure media directories exist and have write permissions:

bash
mkdir -p media/{offer_letters,noc_files,completion_certificates}
chmod -R 755 media/
📊 Database Schema
UserProfile
Links to Django User model
Stores role (student/faculty/admin)
Department and contact information
InternshipApplication
Links to UserProfile (student)
Company and domain details
Application status workflow
File attachments
WeeklyLog
Links to student and application
Progress tracking
Faculty feedback
Missed log detection
InternshipCompletion
Links to application
Certificate upload
Auto-calculated score
Verification workflow
🎨 Customization
Change Color Scheme
Edit the CSS variables in base.html:

css
:root {
    --primary-color: #4CAF50;  /* Change this */
    --secondary-color: #2196F3; /* Change this */
}
Add New Department
Update DEPARTMENT_CHOICES in models.py:

python
DEPARTMENT_CHOICES = [
    ('CSE', 'Computer Science'),
    ('ECE', 'Electronics'),
    # Add more here
]
Modify Scoring Algorithm
Edit calculate_completion_score() in InternshipCompletion model.

🚀 Production Deployment
1. Security Settings
Update settings.py:

python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'generate-new-secret-key'
2. Use Production Database
Change to PostgreSQL or MySQL:

python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smartintern_db',
        'USER': 'dbuser',
        'PASSWORD': 'dbpass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
3. Static Files
bash
python manage.py collectstatic
4. Use Production Server
Install gunicorn:

bash
pip install gunicorn
gunicorn smartintern.wsgi:application
📈 Analytics Features
Available Reports
Domain-wise Distribution: Bar chart showing internship counts by domain
Company-wise Analysis: Top 10 companies hiring interns
Completion Rate: Percentage of completed internships
PDF Report: Comprehensive report with tables
Excel Report: Multi-sheet workbook with detailed data
Chart Generation
Uses matplotlib to create:

Bar charts for distributions
Base64 encoding for inline display
Customizable colors and styles
🔒 Security Features
Password Hashing: Django's PBKDF2 algorithm
CSRF Protection: Enabled by default
Login Required: Decorators on all views
Role-Based Access: Custom decorators check user roles
File Validation: Extension and size checks
SQL Injection Protection: Django ORM
XSS Protection: Template auto-escaping
📝 Additional Notes
Sample data includes realistic names and scenarios
All forms include validation
File uploads are handled securely
Analytics use pandas for data processing
Charts are generated dynamically
PDF reports use reportlab
Excel reports use openpyxl
✅ Testing Checklist
 User registration works
 Login/logout functionality
 Student can apply for internship
 Faculty can approve applications
 Weekly logs submission
 Faculty feedback on logs
 Completion certificate upload
 Score calculation
 Analytics page loads
 Charts display correctly
 PDF download works
 Excel download works
 Role-based access control
 File uploads successful
 All dashboards functional
🎓 Demo Presentation Tips
Start with admin login to show overview
Switch to student to demonstrate application flow
Use faculty account to show approval process
Submit weekly logs as student
Show analytics dashboard
Download and show generated reports
Highlight security features
Demonstrate scoring system
📞 Support
This is a complete, production-ready system with:

✅ 3 user roles with proper access control
✅ Full CRUD operations
✅ File upload/download
✅ Analytics with charts
✅ PDF and Excel report generation
✅ Sample data (10 students, 5 faculty, 3 admins)
✅ 30 internship records
✅ 100+ weekly logs
✅ Responsive Bootstrap UI
✅ Security features
✅ Ready to run and demo
The system is now complete and ready for deployment!

allow new user with the reg number aligning with existing users like 82302630101 if register 82302630143 as new user map him acc to the batch dept and all and at registeration page ask only name not username ma username as reg number