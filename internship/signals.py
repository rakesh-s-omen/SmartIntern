from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import InternshipApplication, InternshipCompletion, ProgressProof


@receiver(pre_save, sender=InternshipApplication)
def save_application_files_to_db(sender, instance, **kwargs):
    """Save file content to database before saving the model"""
    if instance.offer_letter_file and hasattr(instance.offer_letter_file, 'read'):
        instance.offer_letter_data = instance.offer_letter_file.read()
        instance.offer_letter_name = instance.offer_letter_file.name
        instance.offer_letter_file.seek(0)  # Reset file pointer
    
    if instance.noc_file and hasattr(instance.noc_file, 'read'):
        instance.noc_file_data = instance.noc_file.read()
        instance.noc_file_name = instance.noc_file.name
        instance.noc_file.seek(0)


@receiver(pre_save, sender=InternshipCompletion)
def save_completion_files_to_db(sender, instance, **kwargs):
    """Save completion certificate to database"""
    if instance.completion_certificate and hasattr(instance.completion_certificate, 'read'):
        instance.completion_certificate_data = instance.completion_certificate.read()
        instance.completion_certificate_name = instance.completion_certificate.name
        instance.completion_certificate.seek(0)


@receiver(pre_save, sender=ProgressProof)
def save_proof_files_to_db(sender, instance, **kwargs):
    """Save progress proof file to database"""
    if instance.proof_file and hasattr(instance.proof_file, 'read'):
        instance.proof_file_data = instance.proof_file.read()
        instance.proof_file_name = instance.proof_file.name
        # Extract content type from file name
        if '.' in instance.proof_file.name:
            ext = instance.proof_file.name.split('.')[-1].lower()
            content_types = {
                'pdf': 'application/pdf',
                'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'png': 'image/png',
                'mp4': 'video/mp4', 'avi': 'video/x-msvideo', 'mov': 'video/quicktime',
                'doc': 'application/msword', 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            instance.proof_file_type = content_types.get(ext, 'application/octet-stream')
        instance.proof_file.seek(0)
