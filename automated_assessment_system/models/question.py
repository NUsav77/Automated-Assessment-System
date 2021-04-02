from django.db import models
from .course import CourseLevelOutcome
from .const import Question_Options
from django_random_queryset import RandomManager


class Question(models.Model):
    """ The question itself """

    class Meta:
        default_permissions = ("add", "change", "delete", "view")

    objects = RandomManager()

    text = models.TextField(help_text="The question to be asked")
    note = models.TextField(
        help_text="A non-student facing note regarding the question", blank=True
    )
    clo = models.ForeignKey(CourseLevelOutcome, on_delete=models.CASCADE)
    points = models.IntegerField(
        default=1,
        blank=False,
        null=False,
        help_text="Number of points this question is worth. Points are earned by looking at "
        "answers and if select multiplying the values",
    )

    def __str__(self):
        return self.text

    def get_question_details(self):
        return [
            (answer.tag, answer.text)
            for answer in QuestionDetail.objects.filter(question__id=self.id)
        ]

    def question_type(self):
        """
        Determines what form widget to use.
        TODO: Validate input for save() call.
        """
        question_has_true_false_tag = QuestionDetail.objects.filter(
            question__id=self.id, tag__in=["T", "F"]
        ).count()
        if question_has_true_false_tag == 2:
            return "TF"
        else:
            return "MC"


class QuestionDetail(models.Model):
    class Meta:
        default_permissions = ("add", "change", "delete", "view")
        unique_together = (
            ("tag", "question"),
        )  # Tells us tag+question makes a row unique.

    tag = models.CharField(
        max_length=1,
        choices=Question_Options,
        blank=False,
        null=False,
        help_text="The Option name such as D or False",
    )
    text = models.TextField(
        blank=False,
        null=False,
        help_text="The Option text, such as ERD stands for Entity Relationship Diagram",
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
