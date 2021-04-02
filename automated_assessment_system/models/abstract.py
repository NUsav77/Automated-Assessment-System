from django.db import models


class BaseModel(models.Model):
    """
    Provides boilerplate to all the model instances created.
    """

    class Meta:
        default_permissions = ("add", "change", "delete", "view")
        abstract = True

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
