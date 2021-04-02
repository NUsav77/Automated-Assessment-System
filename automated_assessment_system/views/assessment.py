from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from automated_assessment_system.models import (
    AssessmentAttempt,
    Assessment,
    AssessmentAttemptState,
)
from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from django.db.models import Q


class AssessmentAttemptList(LoginRequiredMixin, ListView):
    """
    AssessmentAttempt's goal is to display to the user the assessments they have assigned.
    """

    template_name = "generic_list.html"
    extra_context = {
        "application_name": "List of Assessments",
    }
    fields = ["name"]
    model = AssessmentAttempt

    def dispatch(self, request, *args, **kwargs):
        # Hooks request/response see: https://stackoverflow.com/questions/47808652/what-is-dispatch-used-for-in-django
        if request.user.is_authenticated:
            return super(AssessmentAttemptList, self).dispatch(request, *args, **kwargs)
        else:
            # TODO: Just redirect to login page instead of 403.
            # If they aren't logged in just throw a 403.
            raise PermissionDenied

    def get(self, request, *args, **kwargs):
        user_requesting_page = request.user
        # modify the object_list in context to only show Assessment made by the user requesting page.
        # TODO: Offer way to filter this in url (e.g. show me completed, in progress, not started, all).
        self.object_list = AssessmentAttempt.objects.filter(
            # Using Q() to show how a filter can be ANDED & or OR'd |
            # Show Assessments that has the logged in user as taker.
            Q(user=user_requesting_page)
            & (
                Q(state=AssessmentAttemptState.NOT_STARTED)
                | Q(state=AssessmentAttemptState.IN_PROGRESS)
            )
        )
        """
        TODO: FIXME Need a way to expose this.
                self.object_list_done = AssessmentAttempt.objects.filter(
            Q(user=user_requesting_page)
            & (
                Q(state=AssessmentAttemptState.USER_DONE)
                | Q(state=AssessmentAttemptState.GRADED)
            )
        )
        """
        # get context and prepair and render.
        context = self.get_context_data()
        return render(request, template_name=self.template_name, context=context)
