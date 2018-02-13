from django.db import models

from sendhut.utils import sane_repr
from sendhut.db import BaseModel


class Merchant(BaseModel):

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=30)
    business_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=70)

    class Meta:
        db_table = 'merchant'

    __repr__ = sane_repr('name', 'phone_number', 'business_name', 'email')

    def __unicode__(self):
        return self.business_name
