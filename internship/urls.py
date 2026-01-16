from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('all-faculty/', views.all_faculty_view, name='all_faculty'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('apply/', views.apply_internship, name='apply_internship'),
    path('weekly-log/<int:application_id>/', views.submit_weekly_log, name='submit_weekly_log'),
    path('review/<int:application_id>/', views.review_application, name='review_application'),
    path('review-log/<int:log_id>/', views.review_log, name='review_log'),
    path('completion/<int:application_id>/', views.submit_completion, name='submit_completion'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('download/pdf/', views.download_report_pdf, name='download_pdf'),
    path('download/excel/', views.download_report_excel, name='download_excel'),
    
    # Progress Proof URLs
    path('progress-proof/submit/<int:application_id>/', views.submit_progress_proof, name='submit_progress_proof'),
    path('progress-proof/view/<int:application_id>/', views.view_progress_proofs, name='view_progress_proofs'),
    path('progress-proof/verify/<int:proof_id>/', views.verify_progress_proof, name='verify_progress_proof'),
    path('progress-monitoring/', views.progress_monitoring_dashboard, name='progress_monitoring'),
    
    # Serve files from database
    path('file/<str:model_name>/<int:file_id>/<str:field_name>/', views.serve_file_from_db, name='serve_file'),
]
