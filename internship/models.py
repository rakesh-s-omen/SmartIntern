from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    ]
    
    DEPARTMENT_CHOICES = [
        # Commerce Programs
        ('BCOM_AF', 'B.Com Accounting & Finance'),
        ('BCOM_CA', 'B.Com CA'),
        ('BCOM_CS', 'B.Com CS'),
        ('BCOM', 'B.Com Commerce'),
        ('BCOM_IT', 'B.Com IT'),
        ('BCOM_IB', 'B.Com International Business'),
        ('BCOM_PA', 'B.Com Professional Accounting'),
        ('MCOM_CA', 'M.Com CA'),
        ('MCOM_IB', 'M.Com International Business'),
        
        # Computer Science Programs
        ('CSE', 'B.Sc Computer Science'),
        ('BSC_AI', 'B.Sc AI & ML'),
        ('BSC_CS_COG', 'B.Sc CS with Cognitive Systems'),
        ('BSC_CS_CYB', 'B.Sc CS with Cyber Security'),
        ('BSC_CT', 'B.Sc Computer Technology'),
        ('BSC_DS', 'B.Sc Data Science & Analytics'),
        ('IT', 'B.Sc Information Technology'),
        ('BCA', 'BCA - Bachelor of Computer Applications'),
        
        # Science Programs
        ('BSC_BIO', 'B.Sc Biotechnology'),
        ('MSC_BIO', 'M.Sc Biotechnology'),
        ('BSC_MICRO', 'B.Sc Microbiology'),
        ('PHYSICS', 'B.Sc Physics'),
        ('MATHEMATICS', 'B.Sc Mathematics'),
        
        # Electronics
        ('ECE', 'B.Sc Electronics and Communication Systems'),
        
        # Arts & Media Programs
        ('ENGLISH', 'BA English Literature'),
        ('BSC_ANIM', 'B.Sc Animation & Visual Effects'),
        ('BSC_VISCOM', 'B.Sc Visual Communication'),
        ('BSC_FASHION', 'B.Sc Costume Design & Fashion'),
        
        # Management Programs
        ('BBA', 'BBA'),
        ('BBA_CA', 'BBA CA'),
        ('BBA_LOG', 'BBA Logistics'),
        
        # Hospitality & Food
        ('BSC_CATERING', 'B.Sc Catering Science & Hotel Management'),
        ('BSC_FOOD', 'B.Sc Food Processing Technology & Management'),
    ]
    
    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    register_number = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    email_id = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.full_name} ({self.role})"


class InternshipApplication(models.Model):
    STATUS_CHOICES = [
        ('pending_company', 'Pending - Awaiting Company Offer Letter'),
        ('pending_faculty', 'Pending - Faculty Review'),
        ('approved', 'Approved by Faculty'),
        ('rejected_company', 'Rejected - Company Issue'),
        ('rejected_faculty', 'Rejected by Faculty'),
    ]
    
    MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('hybrid', 'Hybrid'),
    ]
    
    application_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='internship_applications')
    assigned_faculty = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_applications', limit_choices_to={'role': 'faculty'})
    company_name = models.CharField(max_length=200)
    internship_domain = models.CharField(max_length=100)
    internship_mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    offer_letter_file = models.FileField(
        upload_to='offer_letters/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'png'])],
        blank=True,
        null=True
    )
    offer_letter_data = models.BinaryField(blank=True, null=True, editable=False)
    offer_letter_name = models.CharField(max_length=255, blank=True, null=True)
    noc_file = models.FileField(
        upload_to='noc_files/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'png'])],
        blank=True,
        null=True
    )
    noc_file_data = models.BinaryField(blank=True, null=True, editable=False)
    noc_file_name = models.CharField(max_length=255, blank=True, null=True)
    application_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_faculty')
    faculty_remarks = models.TextField(blank=True, null=True)
    approval_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.full_name} - {self.company_name}"


class WeeklyLog(models.Model):
    """Weekly progress tracking - WEEK-based, not hours-based"""
    REVIEW_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed by Faculty'),
    ]
    
    log_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='weekly_logs')
    application = models.ForeignKey(InternshipApplication, on_delete=models.CASCADE, related_name='logs')
    week_number = models.IntegerField()  # Week 1, Week 2, Week 3, etc.
    description = models.TextField(blank=True, null=True, help_text='Optional description/comments')
    
    # MANDATORY file upload (nullable for migration, enforced in form)
    submission_file = models.FileField(
        upload_to='weekly_submissions/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'mp4', 'avi', 'mov'])],
        help_text='Upload your weekly work proof (PDF, Image, Document, or Video)',
        blank=True,
        null=True
    )
    submission_file_name = models.CharField(max_length=255, blank=True, null=True)
    submission_file_type = models.CharField(max_length=100, blank=True, null=True)
    
    submission_date = models.DateTimeField(auto_now_add=True)
    
    # Faculty feedback (visible only to this student)
    faculty_feedback = models.TextField(blank=True, null=True)
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_logs')
    review_date = models.DateTimeField(blank=True, null=True)
    
    # Legacy fields (kept for migration compatibility)
    work_summary = models.TextField(blank=True, null=True)
    skills_learned = models.TextField(blank=True, null=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)
    log_status = models.CharField(max_length=20, default='submitted', blank=True)
    missed_log_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['student', 'application', 'week_number']
        ordering = ['week_number']
    
    def __str__(self):
        return f"Week {self.week_number} - {self.student.full_name}"


class InternshipCompletion(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    completion_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='completions')
    application = models.OneToOneField(InternshipApplication, on_delete=models.CASCADE, related_name='completion')
    total_duration = models.IntegerField(help_text='Duration in days')
    completion_certificate = models.FileField(
        upload_to='completion_certificates/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'png'])],
        blank=True,
        null=True
    )
    completion_certificate_data = models.BinaryField(blank=True, null=True, editable=False)
    completion_certificate_name = models.CharField(max_length=255, blank=True, null=True)
    completion_status = models.BooleanField(default=False)
    faculty_verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    completion_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    verification_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_completion_score(self):
        logs = self.application.logs.filter(log_status='reviewed')
        total_logs = logs.count()
        missed_logs = sum(log.missed_log_count for log in logs)
        
        if total_logs == 0:
            return 0
        
        duration_score = min(self.total_duration / 90 * 40, 40)
        log_score = min(total_logs * 3, 40)
        penalty = missed_logs * 5
        
        score = duration_score + log_score - penalty
        return max(min(score, 100), 0)
    
    def __str__(self):
        return f"Completion - {self.student.full_name}"


class ProgressProof(models.Model):
    """Model to track internship progress with proof files (images, videos, PDFs)"""
    PROOF_TYPE_CHOICES = [
        ('work_sample', 'Work Sample'),
        ('attendance', 'Attendance Proof'),
        ('project_milestone', 'Project Milestone'),
        ('task_completion', 'Task Completion'),
        ('presentation', 'Presentation/Demo'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    proof_id = models.AutoField(primary_key=True)
    application = models.ForeignKey(InternshipApplication, on_delete=models.CASCADE, related_name='progress_proofs')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='progress_proofs')
    proof_type = models.CharField(max_length=50, choices=PROOF_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    proof_file = models.FileField(
        upload_to='progress_proofs/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov', 'doc', 'docx'])],
        help_text='Upload proof: PDF, Image (JPG/PNG), or Video (MP4/AVI/MOV)',
        blank=True,
        null=True
    )
    proof_file_data = models.BinaryField(blank=True, null=True, editable=False)
    proof_file_name = models.CharField(max_length=255, blank=True, null=True)
    proof_file_type = models.CharField(max_length=100, blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    faculty_remarks = models.TextField(blank=True, null=True)
    verified_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_proofs')
    verification_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"{self.title} - {self.student.full_name}"


class PasswordResetOTP(models.Model):
    """Model to store OTP for password reset"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"OTP for {self.user.username}"