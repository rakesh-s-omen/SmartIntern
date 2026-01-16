from django.core.management.base import BaseCommand
from internship.models import InternshipApplication

class Command(BaseCommand):
    help = 'Migrate offer letter and NOC files from disk to database fields for all InternshipApplications.'

    def handle(self, *args, **options):
        migrated = 0
        for app in InternshipApplication.objects.all():
            changed = False
            # Migrate offer letter
            if app.offer_letter_file and not app.offer_letter_data:
                try:
                    with app.offer_letter_file.open('rb') as f:
                        app.offer_letter_data = f.read()
                        app.offer_letter_name = app.offer_letter_file.name.split('/')[-1]
                        changed = True
                        self.stdout.write(f"Migrated offer letter for application {app.application_id}")
                except Exception as e:
                    self.stderr.write(f"Failed to migrate offer letter for application {app.application_id}: {e}")
            # Migrate NOC file
            if app.noc_file and not app.noc_file_data:
                try:
                    with app.noc_file.open('rb') as f:
                        app.noc_file_data = f.read()
                        app.noc_file_name = app.noc_file.name.split('/')[-1]
                        changed = True
                        self.stdout.write(f"Migrated NOC file for application {app.application_id}")
                except Exception as e:
                    self.stderr.write(f"Failed to migrate NOC file for application {app.application_id}: {e}")
            if changed:
                app.save()
                migrated += 1
        self.stdout.write(self.style.SUCCESS(f"Migration complete. {migrated} applications updated."))
