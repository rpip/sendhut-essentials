from uuid import uuid4

from django.db import models


class BaseModel(models.Model):
    """
    An abstract base class model that provides
    self-updating ``created`` and ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    uuid = models.UUIDField(
        default=uuid4, blank=True,
        editable=False, unique=True
    )

    class Meta:
        abstract = True  # Set this model as Abstract
