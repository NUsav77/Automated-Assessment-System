from django import forms
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import (
    HttpResponseNotFound,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
)
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from automated_assessment_system.forms import (
    AssessmentResponseForm,
    MC_SET,
    TF_SET,
)
from automated_assessment_system.models import (
    AssessmentAttempt,
    AssessmentResponse,
)


def assessment_attempt(request, slug):
    """
    assessment_attempt is the functional way of creating a view.

    """

    # Verify person is logged in.
    if not request.user.is_authenticated:
        return redirect("login")
    if not slug:
        return HttpResponseNotFound("Missing slug")

    # Get the assessment assigned to the user.
    attempt = get_object_or_404(
        AssessmentAttempt, Q(slug__exact=slug) & Q(user_id=request.user.id)
    )
    # Not allowed to take an assessment that is done or graded.
    # if attempt.is_done() | attempt.is_graded():
    #    return HttpResponseNotAllowed("Attempt is completed or is graded")

    # Get questions in the assessment.
    questions = attempt.get_questions()
    # paginate the results (so we can save at each call).
    paginator = Paginator(questions, 1)
    # Get the URL parameter in the POST request.
    page = request.GET.get("page")
    question_pager = paginator.get_page(page)
    # Only get one object as Paginator() call is asking for 1.
    question_object = question_pager.object_list[0]

    # Handle all GET requests
    if request.method == "GET":
        # Create a form based off the first question.
        assessment_question_response_form = AssessmentResponseForm(
            question=question_object
        )
        # If this is the first attempt signal to the template to display a start button first!
        is_new_attempt = is_first_attempt(request, attempt)

        # If the template user pressed the button to end the assessment, update state and redirect.
        should_end = request.GET.get("end")
        if should_end == "True":
            # XXX: we don't guard for somebody manually sending a request like ?end=True&start=True
            attempt.state_transition_to_user_done()
            attempt.save()
            # Redirect to list.
            return redirect("assessment-list")

        return render(
            request=request,
            template_name="test_taker_template.html",
            context={
                "is_new_attempt": is_new_attempt,  # Signals to show start assessment.
                "is_saved": False,  # Signals to user that their save operation worked.
                "form": assessment_question_response_form,  # responses to the question
                "error": assessment_question_response_form.errors,  # errors reported by response form
                "question_text": question_object.text,  # The question being asked.
                "is_paginated": True,  # Used to show pagination options.
                "page_obj": question_pager,  # see above.
            },
        )

    elif request.method == "POST":
        arf = AssessmentResponseForm(request.POST, question=question_object)
        if arf.is_valid():
            is_selected = set(arf.cleaned_data["selection"])
            if isinstance(arf.fields["selection"], forms.MultipleChoiceField):
                not_selected = MC_SET.difference(is_selected)
            elif isinstance(arf.fields["selection"], forms.ChoiceField):
                not_selected = TF_SET.difference(is_selected)
            else:
                # Form Type note known.
                return HttpResponseBadRequest("Form type not supported")

            save_form_results(attempt, is_selected, not_selected, question_object)
            return render(
                request=request,
                template_name="test_taker_template.html",
                context={
                    "is_new_attempt": False,
                    "is_saved": True,
                    "form": arf,
                    "error": arf.errors,
                    "question_text": question_object.text,
                    "is_paginated": True,
                    "page_obj": question_pager,
                },
            )
        else:
            # Form Failed to validate
            return render(
                request=request,
                template_name="test_taker_template.html",
                context={
                    "is_new_attempt": False,
                    "is_saved": False,
                    "form": arf,
                    "error": arf.errors,
                    "question_text": question_object.text,
                    "is_paginated": True,
                    "page_obj": question_pager,
                },
            )
    else:
        # HTTP request other than POST and GET.
        return HttpResponseNotAllowed("Bad method")


def is_first_attempt(request, attempt):
    """
    is_first_attempt checks if the user ever answered a question for this attempt.
    """
    new_attempt = False
    response_count = AssessmentResponse.objects.filter(attempt=attempt).count()
    if response_count == 0:
        new_attempt = True
    should_start = request.GET.get("start")
    if should_start == "True":
        attempt.state_transition_to_in_progress()
        attempt.save()
        new_attempt = False  # need to unset for next GET.
        # Don't redirect on start.
    return new_attempt


def save_form_results(attempt, is_selected, not_selected, question_object):
    """
    save_form_results will update the answers in the database for the question_object.
    """
    for option in is_selected:
        try:
            _ = AssessmentResponse.objects.get(
                attempt=attempt, selection=option, question=question_object
            )
        except AssessmentResponse.DoesNotExist:
            ar = AssessmentResponse(
                attempt=attempt, selection=option, question=question_object
            )
            ar.save()
    for option in not_selected:
        try:
            # If it wasn't selected but it exists in the db, remove it.
            ar = AssessmentResponse.objects.get(
                attempt=attempt, selection=option, question=question_object
            )
            ar.delete()
        except AssessmentResponse.DoesNotExist:
            # If it wasn't selected we don't need to add it.
            pass
