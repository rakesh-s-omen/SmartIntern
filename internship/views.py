from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q

@login_required
def application_details(request, application_id):
    """Show details of an internship application, including feedback and files."""
    application = get_object_or_404(InternshipApplication, application_id=application_id)
    # Only allow faculty assigned to this application, the student, or admin to view
    user_profile = request.user.profile
    if not (
        (user_profile.role == 'faculty' and application.assigned_faculty == user_profile)
        or (user_profile.role == 'student' and application.student == user_profile)
        or user_profile.role == 'admin'
    ):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return render(request, 'application_details.html', {'application': application})
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import random
import string
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from .models import UserProfile, InternshipApplication, WeeklyLog, InternshipCompletion, ProgressProof, PasswordResetOTP
from .forms import (UserRegistrationForm, InternshipApplicationForm, 
                    WeeklyLogForm, CompletionForm, FacultyReviewForm,
                    ProgressProofForm, ProgressProofVerificationForm, FacultyLogReviewForm)
from .decorators import role_required


def home_view(request):
    """Landing page for the application"""
    return render(request, 'home.html')


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def forgot_password_view(request):
    """Handle forgot password - send OTP via phone"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Debug logging
        print(f"DEBUG forgot_password: username='{username}', phone='{phone}'")
        
        # Validation
        if not username:
            messages.error(request, 'Please enter your username.')
            return render(request, 'forgot_password.html')
        
        if not phone:
            messages.error(request, 'Please enter your phone number.')
            return render(request, 'forgot_password.html')
        
        try:
            user = User.objects.get(username=username)
            profile = user.profile
            
            # Check if profile has a mobile number
            if not profile.mobile_number:
                messages.error(request, 'No phone number registered for this account. Please contact admin.')
                return render(request, 'forgot_password.html')
            
            # Clean phone numbers - remove all non-digits and take last 10
            stored_phone = ''.join(filter(str.isdigit, str(profile.mobile_number)))[-10:]
            input_phone = ''.join(filter(str.isdigit, str(phone)))[-10:]
            
            # Debug info
            print(f"DEBUG: Stored='{stored_phone}', Input='{input_phone}', Match={stored_phone == input_phone}")
            
            if stored_phone != input_phone:
                messages.error(request, f'Phone number does not match. Expected last 4 digits: ...{stored_phone[-4:]}')
                return render(request, 'forgot_password.html')
            
            # Generate OTP
            otp = generate_otp()
            expires_at = timezone.now() + timedelta(minutes=5)
            
            # Delete any existing OTPs for this user
            PasswordResetOTP.objects.filter(user=user).delete()
            
            # Create new OTP
            PasswordResetOTP.objects.create(
                user=user,
                otp=otp,
                expires_at=expires_at
            )
            
            # In production, you would send SMS here using Twilio/MSG91 etc.
            # For demo, we'll display the OTP
            
            # Mask phone number for display
            masked_phone = f'XXXXXX{phone[-4:]}' if len(phone) >= 4 else phone
            
            print(f"DEBUG: OTP generated: {otp} for user {username}")
            messages.success(request, f'OTP sent to {masked_phone}. (Demo OTP: {otp})')
            return render(request, 'verify_otp.html', {'username': username})
            
        except User.DoesNotExist:
            messages.error(request, 'User not found. Please check your username.')
        except Exception as e:
            print(f"DEBUG: Error in forgot_password: {e}")
            messages.error(request, f'An error occurred: {str(e)}')
    
    return render(request, 'forgot_password.html')


def verify_otp_view(request):
    """Verify OTP and reset password"""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        otp = request.POST.get('otp', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Debug logging
        print(f"DEBUG verify_otp: username={username}, otp={otp}, pwd_len={len(new_password) if new_password else 0}")
        
        # Basic validation
        if not username:
            messages.error(request, 'Username is required.')
            return redirect('forgot_password')
        
        if not otp or len(otp) != 6:
            messages.error(request, 'Please enter a valid 6-digit OTP.')
            return render(request, 'verify_otp.html', {'username': username})
        
        # Validate passwords
        if not new_password or not confirm_password:
            messages.error(request, 'Please enter both password fields.')
            return render(request, 'verify_otp.html', {'username': username})
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'verify_otp.html', {'username': username})
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'verify_otp.html', {'username': username})
        
        try:
            user = User.objects.get(username=username)
            otp_record = PasswordResetOTP.objects.filter(
                user=user,
                otp=otp,
                is_used=False
            ).order_by('-created_at').first()
            
            print(f"DEBUG: OTP record found: {otp_record is not None}")
            
            if not otp_record:
                messages.error(request, 'Invalid OTP. Please check and try again.')
                return render(request, 'verify_otp.html', {'username': username})
            
            if not otp_record.is_valid():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return render(request, 'verify_otp.html', {'username': username})
            
            # OTP is valid - reset password
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            otp_record.is_used = True
            otp_record.save()
            
            print(f"DEBUG: Password reset successful for {username}")
            messages.success(request, 'Password reset successful! Please login with your new password.')
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            print(f"DEBUG: Error in verify_otp: {e}")
            messages.error(request, f'An error occurred: {str(e)}')
    
    # For GET requests, redirect to forgot password
    return redirect('forgot_password')


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Authenticate the user before logging in
                # Username is now the registration number
                username = form.cleaned_data.get('register_number')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Registration successful! Welcome, {user.profile.full_name}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Registration completed but auto-login failed. Please login manually.')
                    return redirect('login')
            except Exception as e:
                messages.error(request, f'Error during registration: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    profile = request.user.profile
    
    if profile.role == 'student':
        applications = InternshipApplication.objects.filter(student=profile).select_related('assigned_faculty')
        logs = WeeklyLog.objects.filter(student=profile).order_by('-submission_date')[:10]
        completions = InternshipCompletion.objects.filter(student=profile)
        
        # Build weekly submission status for each application
        applications_with_weeks = []
        for app in applications:
            app_logs = WeeklyLog.objects.filter(application=app).order_by('week_number')
            submitted_weeks = {log.week_number: log for log in app_logs}
            
            # Calculate expected weeks based on duration
            if app.start_date and app.end_date:
                total_days = (app.end_date - app.start_date).days
                expected_weeks = max(1, total_days // 7)
            else:
                expected_weeks = 12  # Default
            
            week_status = []
            for week_num in range(1, expected_weeks + 1):
                if week_num in submitted_weeks:
                    log = submitted_weeks[week_num]
                    week_status.append({
                        'week': week_num,
                        'status': log.review_status,
                        'submitted': True,
                        'log': log,
                        'feedback': log.faculty_feedback if log.review_status == 'reviewed' else None
                    })
                else:
                    week_status.append({
                        'week': week_num,
                        'status': 'not_submitted',
                        'submitted': False,
                        'log': None,
                        'feedback': None
                    })
            
            applications_with_weeks.append({
                'application': app,
                'weeks': week_status,
                'submitted_count': len(submitted_weeks),
                'total_weeks': expected_weeks
            })
        
        context = {
            'profile': profile,
            'applications': applications,
            'applications_with_weeks': applications_with_weeks,
            'logs': logs,
            'completions': completions,
            'total_applications': applications.count(),
            'approved_applications': applications.filter(application_status='approved').count(),
        }
        return render(request, 'student_dashboard.html', context)
    
    elif profile.role == 'faculty':
        # Applications assigned to this faculty ONLY (strict access control)
        # Show all applications assigned to this faculty (pending and approved)
        my_assigned_applications = InternshipApplication.objects.filter(
            assigned_faculty=profile,
            application_status__in=['pending_faculty', 'pending_company', 'approved']
        ).select_related('student').distinct()

        # Pending submissions (from assigned students only)
        pending_logs = WeeklyLog.objects.filter(
            application__assigned_faculty=profile,
            review_status='pending'
        ).select_related('student', 'application').order_by('-submission_date')

        # Reviewed submissions (from assigned students only)
        reviewed_logs = WeeklyLog.objects.filter(
            application__assigned_faculty=profile,
            review_status='reviewed'
        ).select_related('student', 'application').order_by('-review_date')[:20]

        # Pending applications for approval
        pending_applications = InternshipApplication.objects.filter(
            assigned_faculty=profile,
            application_status__in=['pending_faculty', 'pending_company']
        ).select_related('student')

        pending_completions = InternshipCompletion.objects.filter(
            application__assigned_faculty=profile,
            faculty_verification_status='pending'
        ).select_related('student', 'application')

        # Get assigned students list with progress
        assigned_students_progress = []
        for app in my_assigned_applications:
            logs = WeeklyLog.objects.filter(application=app)
            submitted = logs.count()
            reviewed = logs.filter(review_status='reviewed').count()
            pending = logs.filter(review_status='pending').count()

            # Calculate expected weeks
            if app.start_date and app.end_date:
                total_days = (app.end_date - app.start_date).days
                expected = max(1, total_days // 7)
            else:
                expected = 12

            assigned_students_progress.append({
                'student': app.student,
                'application': app,
                'submitted_weeks': submitted,
                'reviewed_weeks': reviewed,
                'pending_weeks': pending,
                'expected_weeks': expected,
                'progress_pct': int((submitted / expected) * 100) if expected > 0 else 0
            })

        context = {
            'profile': profile,
            'pending_applications': pending_applications,
            'my_assigned_applications': my_assigned_applications,
            'pending_logs': pending_logs,
            'reviewed_logs': reviewed_logs,
            'pending_completions': pending_completions,
            'assigned_students_progress': assigned_students_progress,
        }
        return render(request, 'faculty_dashboard.html', context)
    
    else:  # admin
        total_students = UserProfile.objects.filter(role='student').count()
        total_applications = InternshipApplication.objects.count()
        approved_applications = InternshipApplication.objects.filter(application_status='approved').count()
        total_completions = InternshipCompletion.objects.filter(completion_status=True).count()
        
        # Progress by department
        dept_progress = []
        for dept_code, dept_name in UserProfile.DEPARTMENT_CHOICES:
            dept_students = UserProfile.objects.filter(role='student', department=dept_code).count()
            dept_apps = InternshipApplication.objects.filter(student__department=dept_code).count()
            dept_logs = WeeklyLog.objects.filter(student__department=dept_code).count()
            if dept_students > 0 or dept_apps > 0:
                dept_progress.append({
                    'code': dept_code,
                    'name': dept_name,
                    'students': dept_students,
                    'applications': dept_apps,
                    'submissions': dept_logs
                })
        
        # Faculty load summary
        faculty_load = UserProfile.objects.filter(role='faculty').annotate(
            assigned_count=Count('assigned_applications')
        ).order_by('-assigned_count')[:10]
        
        context = {
            'profile': profile,
            'total_students': total_students,
            'total_applications': total_applications,
            'approved_applications': approved_applications,
            'total_completions': total_completions,
            'dept_progress': dept_progress,
            'faculty_load': faculty_load,
        }
        return render(request, 'admin_dashboard.html', context)


@login_required
@role_required(['faculty'])
def approve_application(request, application_id):
    """Faculty approves or rejects internship applications, with feedback."""
    application = get_object_or_404(
        InternshipApplication, 
        application_id=application_id,
        assigned_faculty=request.user.profile
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        faculty_remarks = request.POST.get('faculty_remarks', '').strip()
        if not faculty_remarks:
            messages.error(request, 'Feedback/remarks are required.')
            return redirect('dashboard')

        application.faculty_remarks = faculty_remarks
        if action == 'approve':
            application.application_status = 'approved'
            application.approved_date = timezone.now()
            application.save()
            messages.success(request, f'Application approved for {application.student.full_name}!')
        elif action == 'reject':
            application.application_status = 'rejected_faculty'
            application.save()
            messages.error(request, f'Application rejected for {application.student.full_name}.')
        else:
            messages.error(request, 'Invalid action.')
        return redirect('dashboard')

    # For GET requests, redirect to dashboard
    return redirect('dashboard')


@login_required
def all_faculty_view(request):
    """View all faculty with their assigned students - Admin only"""
    profile = request.user.profile
    
    if profile.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    # Get all faculty with their assignment counts
    faculty_list = UserProfile.objects.filter(role='faculty').annotate(
        assigned_count=Count('assigned_applications'),
        approved_count=Count('assigned_applications', filter=Q(assigned_applications__application_status='approved')),
        pending_count=Count('assigned_applications', filter=Q(assigned_applications__application_status__in=['pending_faculty', 'pending_company']))
    ).order_by('-assigned_count', 'full_name')
    
    # Get pending reviews count for each faculty
    total_pending_reviews = 0
    for faculty in faculty_list:
        faculty.pending_reviews = WeeklyLog.objects.filter(
            application__assigned_faculty=faculty,
            review_status='pending'
        ).count()
        total_pending_reviews += faculty.pending_reviews
    
    context = {
        'profile': profile,
        'faculty_list': faculty_list,
        'total_faculty': faculty_list.count(),
        'total_pending_reviews': total_pending_reviews,
    }
    return render(request, 'all_faculty.html', context)


@login_required
def all_students_view(request):
    """View all students with their internship status - Admin only"""
    profile = request.user.profile
    if profile.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')

    student_list = UserProfile.objects.filter(role='student').annotate(
        app_count=Count('internship_applications'),
        approved_count=Count('internship_applications', filter=Q(internship_applications__application_status='approved')),
        completed_count=Count('internship_applications', filter=Q(internship_applications__completion__completion_status=True))
    ).order_by('full_name')

    context = {
        'profile': profile,
        'student_list': student_list,
    }
    return render(request, 'all_students.html', context)


@login_required
def profile_view(request):
    """Display user profile page"""
    profile = request.user.profile
    
    context = {
        'profile': profile,
    }
    
    if profile.role == 'student':
        # Get student-specific data
        applications = InternshipApplication.objects.filter(student=profile)
        total_applications = applications.count()
        approved_applications = applications.filter(application_status='approved').count()
        
        # Get total weeks submitted
        total_weeks = WeeklyLog.objects.filter(student=profile).count()
        reviewed_weeks = WeeklyLog.objects.filter(student=profile, review_status='reviewed').count()
        
        # Get assigned faculty info
        assigned_faculty = None
        active_app = applications.filter(application_status='approved').first()
        if active_app and active_app.assigned_faculty:
            assigned_faculty = active_app.assigned_faculty
        
        context.update({
            'total_applications': total_applications,
            'approved_applications': approved_applications,
            'total_weeks': total_weeks,
            'reviewed_weeks': reviewed_weeks,
            'assigned_faculty': assigned_faculty,
        })
        
    elif profile.role == 'faculty':
        # Get faculty-specific data
        assigned_students = InternshipApplication.objects.filter(
            assigned_faculty=profile,
            application_status='approved'
        ).count()
        
        pending_reviews = WeeklyLog.objects.filter(
            application__assigned_faculty=profile,
            review_status='pending'
        ).count()
        
        completed_reviews = WeeklyLog.objects.filter(
            application__assigned_faculty=profile,
            review_status='reviewed'
        ).count()
        
        context.update({
            'assigned_students': assigned_students,
            'pending_reviews': pending_reviews,
            'completed_reviews': completed_reviews,
        })
    
    return render(request, 'profile.html', context)


@role_required(['student'])
def apply_internship(request):
    if request.method == 'POST':
        form = InternshipApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user.profile

            # Store uploaded offer letter in DB
            offer_file = request.FILES.get('offer_letter_file')
            if offer_file:
                application.offer_letter_data = offer_file.read()
                application.offer_letter_name = offer_file.name
            noc_file = request.FILES.get('noc_file')
            if noc_file:
                application.noc_file_data = noc_file.read()
                application.noc_file_name = noc_file.name

            # Auto-assign a faculty from the same department
            from django.db.models import Count
            available_faculty = UserProfile.objects.filter(
                role='faculty',
                department=request.user.profile.department
            ).annotate(
                assigned_count=Count('assigned_applications')
            ).order_by('assigned_count').first()

            if available_faculty:
                application.assigned_faculty = available_faculty
                application.application_status = 'pending_faculty'
            else:
                application.application_status = 'pending_faculty'

            application.save()
            messages.success(request, f'Application submitted successfully! Assigned to {available_faculty.full_name if available_faculty else "faculty review"}')
            return redirect('dashboard')
    else:
        form = InternshipApplicationForm()
    return render(request, 'apply_internship.html', {'form': form})


@role_required(['student'])
def submit_weekly_log(request, application_id):
    application = get_object_or_404(
        InternshipApplication, 
        application_id=application_id, 
        student=request.user.profile,
        application_status='approved'  # Can only submit logs for approved applications
    )
    
    # Get existing logs for this application
    existing_logs = WeeklyLog.objects.filter(
        application=application
    ).order_by('week_number')
    submitted_weeks = list(existing_logs.values_list('week_number', flat=True))
    
    # Calculate expected weeks
    if application.start_date and application.end_date:
        total_days = (application.end_date - application.start_date).days
        expected_weeks = max(1, total_days // 7)
    else:
        expected_weeks = 12
    
    if request.method == 'POST':
        form = WeeklyLogForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if file is uploaded (extra validation)
            if not request.FILES.get('submission_file'):
                messages.error(request, 'File upload is MANDATORY. Please upload your weekly work.')
                return render(request, 'weekly_log.html', {
                    'form': form, 
                    'application': application,
                    'existing_logs': existing_logs,
                    'submitted_weeks': submitted_weeks,
                    'expected_weeks': expected_weeks
                })
            
            log = form.save(commit=False)
            log.student = request.user.profile
            log.application = application
            
            # Store file info
            uploaded_file = request.FILES['submission_file']
            log.submission_file_name = uploaded_file.name
            log.submission_file_type = uploaded_file.content_type
            
            log.save()
            messages.success(request, f'Week {log.week_number} submission uploaded successfully!')
            return redirect('dashboard')
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        # Suggest next week number
        next_week = max(submitted_weeks) + 1 if submitted_weeks else 1
        form = WeeklyLogForm(initial={'week_number': next_week})
    
    return render(request, 'weekly_log.html', {
        'form': form, 
        'application': application,
        'existing_logs': existing_logs,
        'submitted_weeks': submitted_weeks,
        'expected_weeks': expected_weeks
    })


@role_required(['faculty', 'admin'])
def review_application(request, application_id):
    # Admin can review any application
    # Faculty can review: assigned applications OR applications from their department
    if request.user.profile.role == 'admin':
        application = get_object_or_404(InternshipApplication, application_id=application_id)
    else:
        # Faculty can review if assigned to them OR from their department
        application = get_object_or_404(
            InternshipApplication,
            application_id=application_id
        )
        # Check if faculty has permission
        if application.assigned_faculty != request.user.profile and application.student.department != request.user.profile.department:
            messages.error(request, 'You do not have permission to review this application.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = FacultyReviewForm(request.POST)
        if form.is_valid():
            application.application_status = form.cleaned_data['status']
            application.faculty_remarks = form.cleaned_data['remarks']
            application.approval_date = datetime.now().date()
            application.save()
            messages.success(request, 'Application reviewed successfully!')
            return redirect('dashboard')
    else:
        form = FacultyReviewForm()
    
    return render(request, 'approval_page.html', {'form': form, 'application': application})


@role_required(['faculty'])
def approve_application(request, application_id):
    # Faculty can only approve applications assigned to them
    application = get_object_or_404(
        InternshipApplication,
        application_id=application_id,
        assigned_faculty=request.user.profile
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            application.application_status = 'approved'
            application.faculty_remarks = 'Approved from faculty dashboard'
            messages.success(request, f'Application for {application.student.full_name} has been approved!')
        elif action == 'reject':
            application.application_status = 'rejected'
            application.faculty_remarks = 'Rejected from faculty dashboard'
            messages.error(request, f'Application for {application.student.full_name} has been rejected.')
        
        application.approval_date = datetime.now().date()
        application.save()
    
    return redirect('dashboard')


@role_required(['faculty'])
def review_log(request, log_id):
    # Faculty can ONLY review logs from students assigned to them
    log = get_object_or_404(
        WeeklyLog,
        log_id=log_id,
        application__assigned_faculty=request.user.profile
    )
    
    if request.method == 'POST':
        form = FacultyLogReviewForm(request.POST)
        if form.is_valid():
            log.faculty_feedback = form.cleaned_data['faculty_feedback']
            log.review_status = 'reviewed'
            log.reviewed_by = request.user.profile
            log.review_date = datetime.now()
            log.log_status = 'reviewed'  # Legacy field
            log.save()
            messages.success(request, f'Week {log.week_number} reviewed successfully!')
            return redirect('dashboard')
    else:
        form = FacultyLogReviewForm()
    
    return render(request, 'review_log.html', {'log': log, 'form': form})


@role_required(['student'])
def submit_completion(request, application_id):
    application = get_object_or_404(InternshipApplication, application_id=application_id, student=request.user.profile)
    
    if request.method == 'POST':
        form = CompletionForm(request.POST, request.FILES)
        if form.is_valid():
            completion = form.save(commit=False)
            completion.student = request.user.profile
            completion.application = application
            
            # Calculate duration
            duration = (application.end_date - application.start_date).days
            completion.total_duration = duration
            completion.completion_status = True
            
            completion.save()
            completion.completion_score = completion.calculate_completion_score()
            completion.save()
            
            messages.success(request, 'Completion certificate submitted!')
            return redirect('dashboard')
    else:
        form = CompletionForm()
    
    return render(request, 'completion_form.html', {'form': form, 'application': application})


@role_required(['faculty', 'admin'])
def analytics_view(request):
    # Domain-wise count
    domain_data = InternshipApplication.objects.values('internship_domain').annotate(
        count=Count('application_id')
    ).order_by('-count')
    
    # Company-wise count
    company_data = InternshipApplication.objects.values('company_name').annotate(
        count=Count('application_id')
    ).order_by('-count')[:10]
    
    # Completion percentage
    total_apps = InternshipApplication.objects.filter(application_status='approved').count()
    completed = InternshipCompletion.objects.filter(completion_status=True).count()
    completion_pct = (completed / total_apps * 100) if total_apps > 0 else 0
    
    # Generate charts
    domain_chart = generate_bar_chart(domain_data, 'internship_domain', 'Domain-wise Internships')
    company_chart = generate_bar_chart(company_data, 'company_name', 'Top 10 Companies')
    
    context = {
        'domain_data': domain_data,
        'company_data': company_data,
        'completion_percentage': completion_pct,
        'domain_chart': domain_chart,
        'company_chart': company_chart,
        'total_students': UserProfile.objects.filter(role='student').count(),
        'total_internships': InternshipApplication.objects.count(),
    }
    
    return render(request, 'analytics.html', context)


def generate_bar_chart(data, label_field, title):
    if not data:
        return None
    
    try:
        df = pd.DataFrame(list(data))
        
        if df.empty or label_field not in df.columns:
            return None
        
        # Limit to top 10 and truncate long labels
        df = df.head(10)
        df[label_field] = df[label_field].astype(str).str[:20]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(range(len(df)), df['count'], color='#4CAF50')
        
        ax.set_xlabel(label_field.replace('_', ' ').title())
        ax.set_ylabel('Count')
        ax.set_title(title)
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df[label_field], rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, val in zip(bars, df['count']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                   str(int(val)), ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close(fig)
        
        graphic = base64.b64encode(image_png).decode('utf-8')
        return graphic
    except Exception as e:
        print(f"Chart generation error: {e}")
        plt.close('all')
        return None


@role_required(['faculty', 'admin'])
def download_report_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="internship_report.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("SmartIntern Analytics Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Domain-wise data
    domain_data = InternshipApplication.objects.values('internship_domain').annotate(
        count=Count('application_id')
    )
    
    domain_table_data = [['Domain', 'Count']]
    for item in domain_data:
        domain_table_data.append([item['internship_domain'], str(item['count'])])
    
    domain_table = Table(domain_table_data)
    domain_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Paragraph("Domain-wise Internships", styles['Heading2']))
    elements.append(domain_table)
    
    doc.build(elements)
    return response


@role_required(['faculty', 'admin'])
def download_report_excel(request):
    # Domain-wise data
    domain_data = InternshipApplication.objects.values('internship_domain').annotate(
        count=Count('application_id')
    )
    df_domain = pd.DataFrame(list(domain_data))
    
    # Company-wise data
    company_data = InternshipApplication.objects.values('company_name').annotate(
        count=Count('application_id')
    )
    df_company = pd.DataFrame(list(company_data))
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="internship_report.xlsx"'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df_domain.to_excel(writer, sheet_name='Domain Wise', index=False)
        df_company.to_excel(writer, sheet_name='Company Wise', index=False)
    
    return response


@login_required
@role_required(['student'])
def submit_progress_proof(request, application_id):
    """Student submits progress proof (images, videos, PDFs) for an internship"""
    application = get_object_or_404(InternshipApplication, application_id=application_id, student=request.user.profile)
    
    if request.method == 'POST':
        form = ProgressProofForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            proof.application = application
            proof.student = request.user.profile
            proof.save()
            messages.success(request, 'Progress proof submitted successfully!')
            return redirect('view_progress_proofs', application_id=application_id)
    else:
        form = ProgressProofForm()
    
    context = {
        'form': form,
        'application': application,
    }
    return render(request, 'submit_progress_proof.html', context)


@login_required
def view_progress_proofs(request, application_id):
    """View all progress proofs for an internship"""
    application = get_object_or_404(InternshipApplication, application_id=application_id)
    
    # Check permissions
    if request.user.profile.role == 'student':
        if application.student != request.user.profile:
            messages.error(request, 'Access denied')
            return redirect('dashboard')
    elif request.user.profile.role == 'faculty':
        if application.student.department != request.user.profile.department:
            messages.error(request, 'Access denied')
            return redirect('dashboard')
    
    proofs = ProgressProof.objects.filter(application=application).order_by('-submission_date')
    
    context = {
        'application': application,
        'proofs': proofs,
        'total_proofs': proofs.count(),
        'verified_proofs': proofs.filter(verification_status='verified').count(),
        'pending_proofs': proofs.filter(verification_status='pending').count(),
    }
    return render(request, 'view_progress_proofs.html', context)


@login_required
@role_required(['faculty', 'admin'])
def verify_progress_proof(request, proof_id):
    """Faculty verifies progress proof"""
    proof = get_object_or_404(ProgressProof, proof_id=proof_id)
    
    # Faculty can only verify proofs from their department
    if request.user.profile.role == 'faculty':
        if proof.student.department != request.user.profile.department:
            messages.error(request, 'Access denied')
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProgressProofVerificationForm(request.POST)
        if form.is_valid():
            proof.verification_status = form.cleaned_data['verification_status']
            proof.faculty_remarks = form.cleaned_data['faculty_remarks']
            proof.verified_by = request.user.profile
            proof.verification_date = datetime.now()
            proof.save()
            messages.success(request, f'Progress proof {proof.verification_status}!')
            return redirect('view_progress_proofs', application_id=proof.application.application_id)
    else:
        form = ProgressProofVerificationForm()
    
    context = {
        'form': form,
        'proof': proof,
    }
    return render(request, 'verify_progress_proof.html', context)


@login_required
@role_required(['faculty', 'admin'])
def progress_monitoring_dashboard(request):
    """Dashboard for monitoring student internship progress"""
    profile = request.user.profile
    
    # Filter by department for faculty
    if profile.role == 'faculty':
        students = UserProfile.objects.filter(role='student', department=profile.department)
        applications = InternshipApplication.objects.filter(
            student__department=profile.department,
            application_status='approved'
        )
    else:  # admin
        students = UserProfile.objects.filter(role='student')
        applications = InternshipApplication.objects.filter(application_status='approved')
    
    # Get progress statistics
    total_proofs = ProgressProof.objects.filter(application__in=applications).count()
    verified_proofs = ProgressProof.objects.filter(
        application__in=applications, 
        verification_status='verified'
    ).count()
    pending_proofs = ProgressProof.objects.filter(
        application__in=applications, 
        verification_status='pending'
    ).count()
    
    # Get recent proofs
    recent_proofs = ProgressProof.objects.filter(
        application__in=applications
    ).order_by('-submission_date')[:20]
    
    # Applications with low proof submissions (less than 3 proofs)
    low_activity_apps = []
    for app in applications:
        proof_count = ProgressProof.objects.filter(application=app).count()
        if proof_count < 3:
            low_activity_apps.append({
                'application': app,
                'proof_count': proof_count
            })
    
    context = {
        'total_applications': applications.count(),
        'total_proofs': total_proofs,
        'verified_proofs': verified_proofs,
        'pending_proofs': pending_proofs,
        'recent_proofs': recent_proofs,
        'low_activity_apps': low_activity_apps[:10],  # Top 10 low activity
    }
    return render(request, 'progress_monitoring_dashboard.html', context)


@login_required
def serve_file_from_db(request, model_name, file_id, field_name):
    """Serve files stored in database (for InternshipApplication, use *_data fields)."""
    from django.http import HttpResponse
    import mimetypes

    models_map = {
        'application': InternshipApplication,
        'completion': InternshipCompletion,
        'proof': ProgressProof,
    }

    model = models_map.get(model_name)
    if not model:
        return HttpResponse('Invalid model', status=400)

    try:
        obj = model.objects.get(pk=file_id)

        # Check permissions
        if hasattr(obj, 'student'):
            if request.user.profile.role == 'student' and obj.student != request.user.profile:
                return HttpResponse('Access denied', status=403)
            elif request.user.profile.role == 'faculty' and obj.student.department != request.user.profile.department:
                return HttpResponse('Access denied', status=403)

        # For InternshipApplication, use *_data and *_name fields
        if model_name == 'application' and field_name in ['offer_letter_file', 'noc_file']:
            data_field = f"{field_name.replace('_file','')}_data"
            name_field = f"{field_name.replace('_file','')}_name"
            file_data = getattr(obj, data_field, None)
            file_name = getattr(obj, name_field, None)
            file_type = None
            # Fallback: If no DB data, try reading from disk (for new uploads not yet migrated)
            if not file_data and getattr(obj, field_name):
                try:
                    with getattr(obj, field_name).open('rb') as f:
                        file_data = f.read()
                        file_name = getattr(obj, field_name).name.split('/')[-1]
                except Exception:
                    file_data = None
                    file_name = None
        else:
            data_field = f"{field_name}_data"
            name_field = f"{field_name}_name"
            type_field = f"{field_name}_type"
            file_data = getattr(obj, data_field, None)
            file_name = getattr(obj, name_field, 'file')
            file_type = getattr(obj, type_field, None) if hasattr(obj, type_field) else None

        if not file_data:
            return HttpResponse('File not found', status=404)

        # Determine content type
        if file_type:
            content_type = file_type
        else:
            content_type, _ = mimetypes.guess_type(file_name)
            if not content_type:
                content_type = 'application/octet-stream'

        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{file_name}"'
        return response

    except model.DoesNotExist:
        return HttpResponse('File not found', status=404)


@login_required
def admin_user_profile(request, user_id):
    """Admin can view any user's profile by user_id"""
    profile = request.user.profile
    if profile.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)
    user_profile = user.profile
    context = {'profile': user_profile, 'admin_view': True}
    return render(request, 'profile.html', context)

