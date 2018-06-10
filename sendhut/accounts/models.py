from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models

from sendhut.utils import sane_repr
from sendhut.db import BaseModel


class User(AbstractUser, BaseModel):

    ID_PREFIX = 'usr'

    phone = models.CharField(max_length=20, unique=True)
    last_login = models.DateTimeField(null=True, blank=True)
    identity_verified = models.BooleanField(default=False)

    __repr__ = sane_repr('id')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    class Meta:
        db_table = 'user'


class Address(BaseModel):

    ID_PREFIX = 'adr'

    # name and phone number default to user name and tel
    user = models.ForeignKey(User, related_name='addresses')
    # contact name
    name = models.CharField(max_length=120, null=True, blank=True)
    # actual address
    address = models.CharField(max_length=120)
    # flat number or company name
    building_name = models.CharField(max_length=42, null=True, blank=True)
    # geo co-ordinates: lat,lon
    location = models.PointField(null=True, spatial_index=True, geography=True)
    notes = models.CharField(max_length=252, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    # TODO(yao): add address alias: home, office etc
    is_default = models.BooleanField(blank=True, default=False)

    class Meta:
        db_table = 'address'

    __repr__ = sane_repr('county', 'city', 'postcode')

    def __str__(self):
        return self.address
