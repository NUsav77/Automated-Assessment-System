from django.db import models
from .abstract import BaseModel


class Program(BaseModel):
    pass


class ProgramOutcome(BaseModel):
    """
    A Program can have 1 to many PLO's.
    """

    program = models.ForeignKey(Program, on_delete=models.CASCADE)
