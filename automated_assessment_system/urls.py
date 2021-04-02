from django.contrib.auth.decorators import login_required
from django.urls import path

from automated_assessment_system.views.assessment import *
from automated_assessment_system.views.assessment_attempt import assessment_attempt
from automated_assessment_system.views.home import HomeView

urlpatterns = [
    ## Everyone can see this.
    path("", HomeView.as_view(), name="home"),
    path(
        "assessment/list",
        login_required(AssessmentAttemptList.as_view()),
        name="assessment-list",
    ),
    # Student can view list of tests
    path(
        "assessment/",
        login_required(AssessmentAttemptList.as_view()),
        name="assessment-list",
    ),
    # Student can take a test identified by slug.
    path(
        "assessment/take/<slug:slug>/",
        login_required(assessment_attempt),
        name="assessment-attempt",
    ),
]
