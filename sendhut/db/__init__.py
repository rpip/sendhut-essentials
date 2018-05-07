from uuid import uuid4

from django.db import models
from jsonfield import JSONField
from django.urls import reverse

from safedelete.models import SafeDeleteModel
from safedelete.models import HARD_DELETE
from safedelete.admin import SafeDeleteAdmin, highlight_deleted
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
    _safedelete_policy = SOFT_DELETE_CASCADE

    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    deleted = models.DateTimeField(null=True, blank=True)
    metadata = JSONField(blank=True, null=True, max_length=360)
    uuid = models.UUIDField(
        default=uuid4, blank=True,
        editable=False, unique=True
    )

    def get_admin_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name),
                       args=[self.id])

    class Meta:
        abstract = True  # Set this model as Abstract

    def hard_delete(self):
        self.delete(force_policy=HARD_DELETE)


class BaseModelAdmin(SafeDeleteAdmin):

    exclude = ('metadata',)
    _list_display = (highlight_deleted,) + SafeDeleteAdmin.list_display
    _list_filter = SafeDeleteAdmin.list_filter
    actions = ('hard_delete',) + SafeDeleteAdmin.actions

    def hard_delete(self, request, queryset):
        self.message_user(request, "{} successfully deleted".format(queryset.count()))
        return queryset.delete(force_policy=HARD_DELETE)

    hard_delete.short_description = "HARD Delete selected items"

    def get_list_display(self, request):
        return tuple(self.list_display) + self._list_display

    def get_list_filter(self, request):
        return tuple(self.list_filter) + self._list_filter
