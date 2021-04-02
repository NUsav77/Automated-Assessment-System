from django.conf.urls import url
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy
from AAS.settings.prod import DEFAULT_FROM_EMAIL, SITE_URL
from django.template import loader
from .forms import AssessmentAdminForm
from .models import (
    User,
    Program,
    Course,
    ProgramOutcome,
    CourseLevelOutcome,
    Question,
    QuestionDetail,
    PossibleAnswer,
    Assessment,
    AssessmentIssuedState,
    AssessmentAttempt,
    AssessmentResponse,
)


class MyAdminSite(admin.AdminSite):
    """
    Provides the class which our custom MyAdminSite() site runs.
    """

    # Text to put at the end of each page's <title>.
    site_title = gettext_lazy("Automated Assessment System site admin")
    # Text to put in each page's <h1>.
    site_header = gettext_lazy("Welcome to the Automated Assessment System site")
    # Text to put at the top of the admin index page.
    index_title = gettext_lazy("Admin")
    enable_nav_sidebar = True


# Exported to use in urls.py
this = MyAdminSite()


class AssessmentAdmin(admin.ModelAdmin):
    """"""

    list_display = [
        "name",
        "term",
        "for_course",
        "total_possible_points",
        "total_number_of_questions",
        "state",
    ]
    list_display_links = ["name", "for_course"]
    # XXX: Custom form to do data cleaning, if needed.
    form = AssessmentAdminForm
    question_generate_tpl = (
        '<input type="number" id="number_of_questions" name="_requested_number_of_questions" '
        'min="1" max="100"> '
    )

    def number_of_questions(self, obj):
        return mark_safe(self.question_generate_tpl)

    def issue_assessment(self, request, queryset):
        """
        issue_assessment sends an email to the selected assessments that are in the created state.
        """
        for assessment in queryset.filter(state=AssessmentIssuedState.CREATED):
            for user in assessment.taker.all():
                # Create an attempt
                # FIXME: wrap create() in try/catch.
                attempt = AssessmentAttempt.create(assessment.id, user.id)
                ctx = {
                    "slug": attempt.slug,
                    "url": SITE_URL,
                    "issuer": assessment.issuer,
                }
                body = loader.render_to_string("new_assessment_email.html", ctx)
                # Before emailing create object for responses.
                # FIXME: wrap email_user in try/catch.
                user.email_user(
                    subject="A new assessment has been assigned to you",
                    message=body,
                    from_email=DEFAULT_FROM_EMAIL,
                )
                # If email users fail we should change the state.
            assessment.state_transition_to_issued()

    issue_assessment.short_description = "Issue assessment to students."
    actions = [issue_assessment]

    def save_model(self, request, obj, form, change):
        """
        Override method to:
        - Set issuer to the authenticated user that created the assessment. Only works on NEW
        items (the change bool check).
        - Generate N number of questions depending on the button pressed.
        """
        if not change:
            # Set issuer.
            obj.issuer = request.user
            if "_requested_number_of_questions" in request.POST:
                # Need to save to get the id of assessment used in the mTm relationship of questions.
                obj.save()
                # Get number of requested questions
                requested_number_of_question = int(
                    request.POST.get("_requested_number_of_questions")
                )
                # Look at CLO's for this course
                clo_ids = CourseLevelOutcome.objects.filter(
                    course_id=obj.for_course_id
                ).values("id")
                # Get a list of questions
                questions = Question.objects.filter(clo__in=clo_ids)
                # Validate we have it.
                number_of_possible_questions = questions.count()
                if requested_number_of_question > number_of_possible_questions:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "The CLO's associated with this class only have a "
                        "total of {0} questions".format(number_of_possible_questions),
                    )
                    raise ValidationError(
                        "Number of questions possible for assessment {0} is less than the requested amount {1}".format(
                            number_of_possible_questions, requested_number_of_question
                        )
                    )

                else:
                    # If validation passed, set the questions to the assessment.
                    question_set = questions.random(requested_number_of_question)
                    obj.questions.set(question_set)
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        "You have {0} questions ready for assessment {1} worth {2} points".format(
                            number_of_possible_questions,
                            obj.name,
                            obj.total_possible_points(),
                        ),
                    )
                    obj.save()  # Save the object for real.

        else:
            if obj.state == AssessmentIssuedState.ISSUED:
                raise ValidationError(
                    "Cannot edit an assessment once it has been issued to students."
                )
            else:
                obj.save()

    def get_exclude(self, request, obj=None):
        """
        Determine what fields to hide during a change or an add.
        """
        if obj:  # Change view
            return [
                "total_possible_points",
                "total_number_of_questions",
                "term",
            ]
        else:  # Add view
            return ["questions", "issuer", "state"]

    def get_readonly_fields(self, request, obj=None):
        """
        Determines what fields you can edit
        note: I believe this doesn't prevent curl/wget third party to change things. Just compliant web browser.
        """
        if obj:  # Change view
            return [
                "issuer",
                "for_course",
                "total_possible_points",
                "total_number_of_questions",
            ]
        else:  # Add view
            return ["number_of_questions"]

    # TODO: render_change_form to limit what sort of questions are seen in the questions dropdown based on course.
    # This should ONLY trigger if we already have the course selected (e.g. change)
    # def render_change_form(self, request, context, *args, **kwargs):
    #    return super(AssessmentAdmin, self).render_change_form(request, context, *args, **kwargs)


class ProgramOutcomeInline(admin.TabularInline):
    model = ProgramOutcome
    extra = 1


class ProgramAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "courses")
    list_display_links = list_display
    inlines = [
        ProgramOutcomeInline,
    ]

    def courses(self, obj):
        """
        Method to display the courses under the program
        TODO: How to display them as separate clickable CLO's
        """
        pass


class CourseLevelOutcomeInline(admin.TabularInline):
    model = CourseLevelOutcome
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    inlines = [
        CourseLevelOutcomeInline,
    ]


class QuestionDetailInline(admin.TabularInline):
    model = QuestionDetail
    extra = 4  # Number of things to show


class PossibleAnswerInline(admin.TabularInline):
    model = PossibleAnswer
    extra = 4  # Number of things to show


class QuestionAdmin(admin.ModelAdmin):
    """
    Allows us to create 1 page to Add a Question and Answer.
    """

    inlines = [QuestionDetailInline, PossibleAnswerInline]


class UserAdmin(admin.ModelAdmin):
    fields = (
        "email",
        "first_name",
        "last_name",
        "groups",
        "is_active",
        "is_staff",
    )


# Instead of using a decorator just register everything here.
this.register(Program, ProgramAdmin)
this.register(Course, CourseAdmin)
this.register(Question, QuestionAdmin)
this.register(Assessment, AssessmentAdmin)
this.register(User, UserAdmin)
# TODO: Remove me, this was used for testing.
this.register(AssessmentResponse)
this.register(AssessmentAttempt)
