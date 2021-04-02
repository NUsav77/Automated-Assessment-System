from django.db import models

from .const import Question_Options
from .question import Question


class PossibleAnswer(models.Model):
    """
    Tells us how right an answer is.
    Say if they select "A" and only A
    By default it is zero points (wrong).
    However a faculty user can say if they select A, then it is worth .25,1.0 or whatever number they wish.
    This leaves us with 4 records per question (or 2 if using True/False) to account for all possible outcomes.
    """

    class Meta:
        default_permissions = ("add", "change", "delete", "view")
        unique_together = (
            ("selection", "question"),
        )  # Tells us selection+question makes a row unique.

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        help_text="The question which these answers are for.",
    )
    # Note: removed correctness as score of zero is implied wrong.
    selection = models.CharField(
        max_length=1,
        choices=Question_Options,
        help_text="The selection value, such as A,B,C..",
    )
    weight = models.FloatField(
        default=0.0, help_text="The float value that if this is selected is worth."
    )

    def __str__(self):
        return f"{self.question}:{self.selection}"
