from django.core.management.base import BaseCommand
from api.models import Report, ReportAnnotation, ReportAnnotationComment, Votes, Area, Notifications, Alert, Document


class Command(BaseCommand):
    help = 'Remove all seeded data except users'

    def handle(self, *args, **options):
        models = [Votes, Alert, Report, ReportAnnotation, ReportAnnotationComment, Document, Area, Notifications]

        for model in models:
            count, _ = model.objects.all().delete()
            self.stdout.write(f'  Deleted {count} {model.__name__}')

        self.stdout.write(self.style.SUCCESS('Unseed terminé !'))