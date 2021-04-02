import datetime
import uuid

from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from AAS.settings.base import AUTH_USER_MODEL
from . import Question_Options, PossibleAnswer
from .course import Course
from .question import Question


class AssessmentIssuedState(models.IntegerChoices):
    CREATED = 1  # Just created in the UI.
    ISSUED = 2  # Issued to students via email.


class Assessment(models.Model):
    """
    Assessment is what the teacher creates to test students.
    """

    class Meta:
        default_permissions = ("add", "change", "delete", "view")

    name = models.CharField(max_length=100, help_text="Name of the assessment")
    questions = models.ManyToManyField(Question)
    for_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        help_text="The course associated with this Assessment.",
    )
    term = models.DateField(
        default=datetime.date.today, help_text="The date of the assessment"
    )
    issuer = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assessor"
    )
    taker = models.ManyToManyField(AUTH_USER_MODEL, related_name="taker")
    state = models.IntegerField(
        choices=AssessmentIssuedState.choices,
        default=AssessmentIssuedState.CREATED,
        help_text="The assessment state",
    )

    def __str__(self):
        return self.name

    def state_transition_to_issued(self):
        self.state = AssessmentIssuedState.ISSUED
        self.save()

    def total_number_of_questions(self):
        """
        total_number_of_questions returns the number of questions in assessment.
        """
        return self.questions.count()

    def total_possible_points(self):
        """
        total_possible_points returns the total points possible in the assessment.
        """
        sum_points = 0
        for question in self.questions.all():
            sum_points += question.points
        return sum_points

    def average_score(self):
        """
        Example of analytic. This is O(n^2) at least.
        """
        user_count = 0
        total_score = 0
        for user in self.taker.all():
            user_count += 1  # add for each user (a count() call to the db is one extra call we don't need to make)
            for attempt in AssessmentAttempt.objects.filter(
                Q(user=user) & Q(state=AssessmentAttemptState.GRADED)
            ):
                total_score += attempt.total_score
        return total_score / float(user_count)


class AssessmentAttemptState(models.IntegerChoices):
    NOT_STARTED = 1  # Student hasn't started.
    IN_PROGRESS = 2  # Student signed in and started it.
    USER_DONE = 3  # Student clicked done.
    GRADED = 4  # Question has been graded.


class AssessmentAttempt(models.Model):
    """
    Assessment is what the teacher will issue to create AssessmentAttempt's.
    AssessmentAttempt is the "students view" into their test.
    AssessmentResponse contains their answers for AssessmentAttempt's questions.
    """

    class Meta:
        default_permissions = ("add", "change", "delete", "view")
        unique_together = (
            "slug",
            "assessment",
            "user",
        )

    slug = models.SlugField(max_length=36)  # UUIDv4 length as a string is 36.
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="test_taker"
    )
    state = models.IntegerField(
        choices=AssessmentAttemptState.choices,
        default=AssessmentAttemptState.NOT_STARTED,
        help_text="The assessment attempt state",
    )
    issue_time = models.DateTimeField(
        default=timezone.now, verbose_name="Creation time of Assessment attempt"
    )
    start_time = models.DateTimeField(
        null=True, blank=True, verbose_name="Time at which user started"
    )
    done_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Time at which the user completed the assessment",
    )
    graded_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Time at which the system graded the assessment",
    )
    total_score = models.FloatField(
        null=True,  # creation of object will need this to be null.
        verbose_name="The sum of all points earned for the assessment attempt",
    )

    def state_transition_to_in_progress(self):
        """
        Executed when the student starts the test in the UI.
        """
        self.state = AssessmentAttemptState.IN_PROGRESS
        self.start_time = timezone.now()
        self.save()

    def state_transition_to_user_done(self):
        """
        Executed when the student hits submit in the UI.
        """
        self.state = AssessmentAttemptState.USER_DONE
        self.done_time = timezone.now()
        self.save()

    def is_done(self):
        if self.state == AssessmentAttemptState.USER_DONE:
            return True

    def state_transition_to_graded(self, points_earned):
        """
        Executed when the system graded the test.
        """
        self.state = AssessmentAttemptState.GRADED
        self.graded_time = timezone.now()
        self.total_score = points_earned
        self.save()

    def is_graded(self):
        if self.state == AssessmentAttemptState.GRADED:
            return True

    def get_absolute_url(self):
        """
        URL is provided to user in email, slug as a UUIDv4 will provide enough randomness.
        """
        return reverse("assessment-attempt", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().__str__()  # UUIDv4 is "random enough"
        return super().save(*args, **kwargs)

    @classmethod
    def create(cls, assessmentid, userid):
        """
        provides a way to generate a new AssessmentAttempt
        """
        ass_attempt = cls(
            slug=uuid.uuid4().__str__(),
            assessment_id=assessmentid,
            user_id=userid,
            state=AssessmentAttemptState.NOT_STARTED,
        )
        ass_attempt.save()
        return ass_attempt

    def get_questions(self):
        """
        get_questions provides the questions associated with the issued Assessment.
        TODO: Test that assessment.questions.filter() returns correct values.
        """
        assessment = Assessment.objects.get(id=self.assessment_id)
        return assessment.questions.order_by("id")

    def __str__(self):
        return f"{self.slug}"

    def get_assessment_response(self):
        ar = AssessmentResponse.objects.filter(attempt=self.id)
        return ar


class AssessmentResponse(models.Model):
    """
    AssessmentResponse contain the responses to a AssessmentAttempt.
    """

    class Meta:
        default_permissions = ("add", "change", "delete", "view")
        unique_together = ("attempt", "question", "selection")

    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selection = models.CharField(
        max_length=1,
        choices=Question_Options,
        blank=True,
        help_text="The selection value, such as A,B,C..",
    )

    def grade_question_selection(self):
        asked_question = self.question.id
        point_worth = self.question.points  # Fraction of points the selection is worth.
        try:
            # Get question
            possible_answer = PossibleAnswer.objects.get(
                # Q function to do AND'ing.
                Q(pk=asked_question)
                & Q(selection=self.selection)
            )
            # Take questions point_worth and multiply it by the weight.
            return point_worth * possible_answer.weight
            # If somehow we get here, ignore it (user select D on a T/F question).
        except PossibleAnswer.DoesNotExist:
            return 0.0
        except PossibleAnswer.MultipleObjectsReturned:
            # TODO: Log this as an issue, we should never have this happen.
            return 0.0

    def __str__(self):
        return f"{self.attempt}:{self.attempt.user}:{self.question}:{self.selection}"
