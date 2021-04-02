from django.db import models
from .program import Program, ProgramOutcome
from .abstract import BaseModel


class Course(BaseModel):
    """
    A Course can have m to n many programs.
    """

    program = models.ManyToManyField(Program)

    def __str__(self):
        return f"{self.name}"


class CourseLevelOutcome(BaseModel):
    """
    A Course can have 1 to many CLO's.
    Each PLO can map to n PLO's
    """

    plo = models.ManyToManyField(ProgramOutcome)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
