from django.db import models
from django.db.models.query import QuerySet
from datetime import datetime

# http://django-safedelete.readthedocs.io/en/latest/models.html#module-safedelete.models
# admin hard delete, user delete is hard delete


class SoftDeletionQuerySet(QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(
            deleted=datetime.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted=None)

    def dead(self):
        return self.exclude(deleted=None)


class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SoftDeletionModel(models.Model):

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, force_policy=None, **kwargs):
        self.deleted = datetime.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()
