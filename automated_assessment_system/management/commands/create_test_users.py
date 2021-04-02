from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from automated_assessment_system.models import User


def create_test_users():
    super_user = User.objects.create_superuser("super@example.com", "pass")
    try:
        admin_user = User.objects.create_user("admin@example.com", "pass")
        admin_user.is_staff = True
        admin_user.save()
        admin_group = Group.objects.get(name="admins")
        admin_group.user_set.add(admin_user)
        admin_group.save()
    except:
        print("Error creating admin user")
    try:
        faculty_user = User.objects.create_user("faculty@example.com", "pass")
        faculty_user.is_staff = True
        faculty_user.save()
        faculty_group = Group.objects.get(name="faculty")
        faculty_group.user_set.add(faculty_user)
        faculty_group.save()
    except:
        print("Error creating faculty user")
    try:
        student_user = User.objects.create_user("student@example.com", "pass")
        student_group = Group.objects.get(name="students")
        student_group.user_set.add(student_user)
        student_group.save()

    except:
        print("Error creating student user")


class Command(BaseCommand):
    help = "creates test users for development"

    def handle(self, *args, **options):
        create_test_users()
