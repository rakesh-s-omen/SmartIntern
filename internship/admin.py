from django.contrib import admin
from .models import UserProfile, InternshipApplication, WeeklyLog, InternshipCompletion, ProgressProof

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'role', 'department', 'email_id']
    list_filter = ['role', 'department']
    search_fields = ['full_name', 'employee_id', 'email_id']

@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    list_display = ['application_id', 'student', 'company_name', 'internship_domain', 'application_status', 'start_date']
    list_filter = ['application_status', 'internship_domain', 'internship_mode']
    search_fields = ['company_name', 'student__full_name']

@admin.register(WeeklyLog)
class WeeklyLogAdmin(admin.ModelAdmin):
    list_display = ['log_id', 'student', 'week_number', 'hours_worked', 'log_status', 'submission_date']
    list_filter = ['log_status']
    search_fields = ['student__full_name']

@admin.register(InternshipCompletion)
class InternshipCompletionAdmin(admin.ModelAdmin):
    list_display = ['completion_id', 'student', 'total_duration', 'completion_score', 'faculty_verification_status']
    list_filter = ['faculty_verification_status', 'completion_status']
    search_fields = ['student__full_name']

@admin.register(ProgressProof)
class ProgressProofAdmin(admin.ModelAdmin):
    list_display = ['proof_id', 'student', 'application', 'proof_type', 'title', 'verification_status', 'submission_date']
    list_filter = ['verification_status', 'proof_type', 'submission_date']
    search_fields = ['student__full_name', 'title', 'application__company_name']