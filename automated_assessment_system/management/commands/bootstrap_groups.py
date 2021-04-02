from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


def create_groups():
    print("CREATING Groups")
    g, created = Group.objects.get_or_create(name="students")
    if created:
        print("CREATE student group")
        # TODO: Add list of permissions
        # TODO: How does object level view views.
        ## Defaults to automated_assessment_system.(add|change|delete|view)_(NameOfModel)
    else:
        print("student group exists")
    g, created = Group.objects.get_or_create(name="faculty")
    if created:
        print("CREATE faculty group")
    else:
        print("student faculty exists")
    g, created = Group.objects.get_or_create(name="admins")
    if created:
        print("CREATE admins group")
    else:
        print("student admins exists")


class Command(BaseCommand):
    help = "Builds a the 3 core user groups in aas"

    def handle(self, *args, **options):
        create_groups()
