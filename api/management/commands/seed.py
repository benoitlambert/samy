from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import CustomUser, Area, Report, ReportAnnotation, Notifications, Votes, ReportImage
import random

from api.enum import (
    ReportUserType, ReportOperation, ReportCategory1, ReportCategory2,
    InCharge, ReportStatus
)

class Command(BaseCommand):
    help = 'Seed the database with test data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Notifications
        notif_new, _ = Notifications.objects.get_or_create(name='new_report')
        notif_status, _ = Notifications.objects.get_or_create(name='status_change')

        # Area - Namur
        namur, _ = Area.objects.update_or_create(
            name='Namur',
            defaults={
                'active': True,
            }
        )
        self.stdout.write(f'  Area: {namur.name} (active={namur.active})')

        # Utilisateur standard
        user, created = CustomUser.objects.get_or_create(
            email='eddy@avello.be',
            defaults={
                'first_name': 'Eddy',
                'last_name': 'Merckx',
                'alias': 'em',
                'is_active': True,
                'is_staff': False,
            }
        )
        if created:
            user.set_password('test')
            user.save()
        self.stdout.write(f'  User: {user.email}')

        # Coordinateur
        coordinator, created = CustomUser.objects.get_or_create(
            email='poulidor@avello.be',
            defaults={
                'first_name': 'Raymond',
                'last_name': 'Poulidor',
                'alias': 'rpoulidor',
                'is_active': True,
                'is_staff': True,
                'is_coordinator': True,
            }
        )
        if created:
            coordinator.set_password('test')
            coordinator.coordinator_area.add(namur)
            coordinator.save()
        self.stdout.write(f'  Coordinator: {coordinator.email}')

        # Admin (superuser)
        admin, created = CustomUser.objects.get_or_create(
            email='binda@avello.be',
            defaults={
                'first_name': 'Alfredo',
                'last_name': 'Binda',
                'alias': 'abinda',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('test')
            admin.save()
        self.stdout.write(f'  Admin: {admin.email}')

        reports_data = [

            {'user_type': ReportUserType.PEDESTRIAN.value,
             'category_1': ReportCategory1.INFRASTRUCTURE.value,
             'category_2': str(ReportCategory2.LANE_HOLE.value),
             'operation': ReportOperation.LOCALE.value,
             'lat': 50.4650, 'lng': 4.8660,
             'comment': 'Trou dangereux'},

            {'user_type': ReportUserType.CYCLIST.value,
             'category_1': ReportCategory1.INCIDENT.value,
             'category_2': str(ReportCategory2.INCIDENT_GLASS_ON_LANE.value),
             'operation': ReportOperation.LOCALE.value,
             'lat': 50.4700, 'lng': 4.8750,
             'comment': 'Verre brisé sur la piste cyclable'},


            {'user_type': ReportUserType.CYCLIST.value,
             'category_1': ReportCategory1.INFRASTRUCTURE.value,
             'category_2': f'{ReportCategory2.LANE_POOR_CONDITION.value},{ReportCategory2.LANE_VANISHED_PAINT.value}',
             'operation': ReportOperation.LOCALE.value,
             'lat': 50.4630, 'lng': 4.8800,
             'comment': 'Piste en mauvais état et marquage effacé'},

            {'user_type': ReportUserType.PEDESTRIAN.value,
             'category_1': ReportCategory1.INFRASTRUCTURE.value,
             'category_2': f'{ReportCategory2.WAL_DANGEROUS_CROSSING.value},{ReportCategory2.WAL_HIGH_SPEED.value}',
             'operation': ReportOperation.BLACK_DOT_WALLONIA.value,
             'lat': 50.4680, 'lng': 4.8680,
             'comment': 'Traversée très dangereuse avenue de la Gare, vitesse excessive'},

            {'user_type': ReportUserType.PEDESTRIAN.value,
             'category_1': ReportCategory1.INFRASTRUCTURE.value,
             'category_2': f'{ReportCategory2.OBSTACLE_ON_THE_SIDEWALK.value},{ReportCategory2.MISSING_PEDESTRIAN_CROSSING.value}',
             'operation': ReportOperation.PEDESTRIAN_ISSUES.value,
             'lat': 50.4710, 'lng': 4.8590,
             'comment': 'Passage pas clair'},
        ]
        for i, data in enumerate(reports_data):
            annotation, _ = ReportAnnotation.objects.get_or_create(
                id=i + 100,
                defaults={
                    'area': namur,
                    'in_charge': 0,
                    'status': 1,
                }
            )

            report, created = Report.objects.get_or_create(
                comment=data['comment'],
                defaults={
                    'user_type': data['user_type'],
                    'operation': data['operation'],
                    'category_1': data['category_1'],
                    'category_2': data['category_2'],
                    'latitude': data['lat'],
                    'longitude': data['lng'],
                    'owner': random.choice([user, coordinator]),
                    'annotation': annotation,
                }
            )
            if created:
                self.stdout.write(f'  Report: {data["comment"][:50]}')

        # Quelques votes
        for report in Report.objects.all()[:3]:
            Votes.objects.get_or_create(
                user=user,
                report=report,
                defaults={'gravity': random.randint(1, 5)}
            )

        self.stdout.write(self.style.SUCCESS('Seed terminé !'))
