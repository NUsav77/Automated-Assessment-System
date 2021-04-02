from django.core.management.base import BaseCommand
from automated_assessment_system.cron import grader


class Command(BaseCommand):
    help = "Grades assessments in the USER_DONE state"

    def handle(self, *args, **options):
        grader()
