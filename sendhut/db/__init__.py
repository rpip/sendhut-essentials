from uuid import uuid4

from django.db import models
from jsonfield import JSONField

# from .soft_delete import SoftDeletionModel
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE, HARD_DELETE


class UpdateMixin(object):
    def update(self, **kwargs):
        if self._state.adding:
            raise self.DoesNotExist
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save(update_fields=kwargs.keys())


class BaseModel(SafeDeleteModel, UpdateMixin):
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
    metadata = JSONField(blank=True, null=True, max_length=360)
    uuid = models.UUIDField(
        default=uuid4, blank=True,
        editable=False, unique=True
    )

    def hard_delete(self):
        self.delete(force_policy=HARD_DELETE)

    class Meta:
        abstract = True  # Set this model as Abstract
