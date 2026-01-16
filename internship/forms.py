from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, InternshipApplication, WeeklyLog, InternshipCompletion, ProgressProof
import re
from datetime import datetime

# Department code mapping for registration number parsing
REG_DEPT_MAPPING = {
    '30': 'CSE',           # B.Sc Computer Science
    '31': 'IT',            # B.Sc Information Technology
    '32': 'MATHEMATICS',   # B.Sc Mathematics (and other codes)
    '33': 'BSC_AI',        # B.Sc AI & ML
    '34': 'BSC_DS',        # B.Sc Data Science
    '35': 'BCA',           # BCA
    '36': 'ECE',           # Electronics
    '37': 'BSC_BIO',       # Biotechnology
    '38': 'BSC_MICRO',     # Microbiology
    '39': 'PHYSICS',       # Physics
    '40': 'BCOM',          # B.Com
    '41': 'BCOM_CA',       # B.Com CA
    '42': 'BCOM_CS',       # B.Com CS
    '43': 'BCOM_AF',       # B.Com Accounting & Finance
    '44': 'BCOM_IT',       # B.Com IT
    '45': 'BBA',           # BBA
    '46': 'BBA_CA',        # BBA CA
    '47': 'ENGLISH',       # BA English
    '48': 'BSC_VISCOM',    # Visual Communication
    '49': 'BSC_ANIM',      # Animation
    '50': 'BSC_FASHION',   # Fashion
    '51': 'MBA',           # MBA
    '52': 'MCA',           # MCA
    '53': 'MCOM_CA',       # M.Com CA
}

def parse_registration_number(reg_no):
    """
    Parse registration number to extract department, year, and batch.
    Format: 8230 + BatchYear(2 digits) + DeptCode(2 digits) + RollNo(3 digits)
    Example: 82302630101 -> Batch 26, Dept 30 (CSE), Roll 101
    """
    if not reg_no or len(reg_no) < 11:
        return None
    
    try:
        # Check if starts with college code (8230)
        if reg_no[:4] == '8230':
            batch_year = int(reg_no[4:6])  # 26, 25, 24, 23
            dept_code = reg_no[6:8]        # 30, 31, 32...
            
            # Calculate year of study based on batch year
            # Batch 26 = started 2026 = year 1, Batch 25 = year 2, etc.
            current_year = datetime.now().year % 100  # 26 for 2026
            year_of_study = current_year - batch_year + 1
            year_of_study = max(1, min(4, year_of_study))  # Clamp between 1-4
            
            department = REG_DEPT_MAPPING.get(dept_code, 'CSE')
            
            return {
                'department': department,
                'year_of_study': year_of_study,
                'batch_year': f"20{batch_year}",
                'register_number': reg_no
            }
    except (ValueError, IndexError):
        pass
    
    return None


class UserRegistrationForm(UserCreationForm):
    """Registration form for students - uses registration number as username"""
    
    register_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter Registration Number (e.g., 82302630143)',
            'autofocus': True
        }),
        help_text='Your registration number will be your username'
    )
    full_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'})
    )
    mobile_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'})
    )
    
    class Meta:
        model = User
        fields = ['password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        # Remove username field from the form
        if 'username' in self.fields:
            del self.fields['username']
    
    def clean_register_number(self):
        reg_no = self.cleaned_data.get('register_number', '').strip()
        
        if not reg_no:
            raise forms.ValidationError('Registration number is required')
        
        # Check if user already exists
        if User.objects.filter(username=reg_no).exists():
            raise forms.ValidationError('This registration number is already registered')
        
        # Validate format for numeric registration numbers
        if reg_no.isdigit() and len(reg_no) == 11:
            parsed = parse_registration_number(reg_no)
            if not parsed:
                raise forms.ValidationError('Invalid registration number format')
        
        return reg_no
    
    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number', '').strip()
        if not re.match(r'^[6-9]\d{9}$', mobile):
            raise forms.ValidationError('Enter a valid 10-digit Indian mobile number')
        return mobile
    
    def save(self, commit=True):
        reg_no = self.cleaned_data['register_number']
        
        # Parse registration number to get department and year
        parsed = parse_registration_number(reg_no)
        
        # Create user with registration number as username
        user = User(
            username=reg_no,
            email=f'{reg_no}@student.hicas.ac.in'
        )
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
            
            # Determine department and year from registration number or use defaults
            if parsed:
                department = parsed['department']
                year_of_study = parsed['year_of_study']
            else:
                department = 'CSE'
                year_of_study = 1
            
            UserProfile.objects.create(
                user=user,
                employee_id=f"STU{user.id:05d}",
                full_name=self.cleaned_data['full_name'],
                role='student',  # New registrations are always students
                department=department,
                email_id=f'{reg_no}@student.hicas.ac.in',
                mobile_number=self.cleaned_data['mobile_number'],
                register_number=reg_no,
                year_of_study=year_of_study
            )
        return user


class InternshipApplicationForm(forms.ModelForm):
    class Meta:
        model = InternshipApplication
        fields = ['company_name', 'internship_domain', 'internship_mode', 
                  'start_date', 'end_date', 'offer_letter_file', 'noc_file']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'internship_domain': forms.TextInput(attrs={'class': 'form-control'}),
            'internship_mode': forms.Select(attrs={'class': 'form-control'}),
        }


class WeeklyLogForm(forms.ModelForm):
    """Weekly submission form - MANDATORY file upload"""
    class Meta:
        model = WeeklyLog
        fields = ['week_number', 'description', 'submission_file']
        widgets = {
            'week_number': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1', 
                'max': '52',
                'placeholder': 'Enter week number (1, 2, 3...)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Optional: Describe your work this week...'
            }),
            'submission_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx,.mp4,.avi,.mov',
                'required': True,
                'id': 'submission-file-input'
            }),
        }
        labels = {
            'week_number': 'Week Number',
            'description': 'Description / Comments (Optional)',
            'submission_file': 'Upload Work File (REQUIRED)',
        }
        help_texts = {
            'submission_file': 'Supported: PDF, Images (JPG/PNG), Documents (DOC/DOCX), Videos (MP4/AVI/MOV)'
        }
    
    def clean_submission_file(self):
        file = self.cleaned_data.get('submission_file')
        if not file:
            raise forms.ValidationError('File upload is MANDATORY. Please upload your weekly work.')
        return file


class FacultyLogReviewForm(forms.Form):
    """Form for faculty to review weekly submissions"""
    faculty_feedback = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4,
            'placeholder': 'Provide feedback for this week\'s submission...'
        }),
        required=True,
        label='Your Feedback'
    )


class CompletionForm(forms.ModelForm):
    class Meta:
        model = InternshipCompletion
        fields = ['completion_certificate']
        widgets = {
            'completion_certificate': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FacultyReviewForm(forms.Form):
    status = forms.ChoiceField(
        choices=[
            ('approved', 'Approve - Student can proceed with internship'),
            ('rejected_faculty', 'Reject - Faculty concerns'),
            ('rejected_company', 'Reject - Company/offer letter issues')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Provide detailed feedback for the student...'}),
        required=True,
        label='Feedback/Remarks'
    )


class ProgressProofForm(forms.ModelForm):
    class Meta:
        model = ProgressProof
        fields = ['proof_type', 'title', 'description', 'proof_file']
        widgets = {
            'proof_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Week 2 Work Sample'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your progress, achievements, or activities...'}),
            'proof_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png,.mp4,.avi,.mov,.doc,.docx'}),
        }
        help_texts = {
            'proof_file': 'Supported formats: PDF, Images (JPG/PNG), Videos (MP4/AVI/MOV), Documents (DOC/DOCX). Max size: 100MB'
        }


class ProgressProofVerificationForm(forms.Form):
    verification_status = forms.ChoiceField(
        choices=[('verified', 'Verify'), ('rejected', 'Reject')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    faculty_remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add your feedback...'}),
        required=True,
        label='Remarks'
    )
