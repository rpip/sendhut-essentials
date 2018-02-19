from uuid import uuid4

from django.db import models
from jsonfield import JSONField

# from .soft_delete import SoftDeletionModel
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE


class BaseModel(SafeDeleteModel):
    """
    An abstract base class model that provides
    self-updating ``created`` and ``modified`` fields.
    """
    # TODO(yao): implement soft-delete. mark as deleted
    # and excluded objects delete from queries
    _safedelete_policy = SOFT_DELETE_CASCADE

    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    metadata = JSONField(blank=True, null=True)
    uuid = models.UUIDField(
        default=uuid4, blank=True,
        editable=False, unique=True
    )

    class Meta:
        abstract = True  # Set this model as Abstract
