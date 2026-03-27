from django.core.management import call_command
from django.core.management.base import BaseCommand  # type: ignore


class Command(BaseCommand):
    help = 'Run all seed commands in order'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding exercises...'))
        call_command('seed_exercises')

        self.stdout.write(self.style.MIGRATE_HEADING('Seeding template plans...'))
        call_command('seed_plans')

        self.stdout.write(self.style.MIGRATE_HEADING('Seeding demo user and sessions...'))
        call_command('seed_sessions')

        self.stdout.write(self.style.SUCCESS('All seed data created successfully'))
