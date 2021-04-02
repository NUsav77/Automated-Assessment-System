from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class AutomatedAssessmentSystemConfig(AppConfig):
    name = "automated_assessment_system"


class MyAdminConfig(AdminConfig):
    default_site = "automated_assessment_system.admin.MyAdminSite"
