from django.contrib.auth.models import AbstractUser
from django.db import models

from sendhut.utils import sane_repr
from sendhut.db import BaseModel


class User(AbstractUser, BaseModel):

    phone = models.CharField(max_length=20, unique=True)
    last_login = models.DateTimeField(null=True, blank=True)
    identity_verified = models.BooleanField(default=False)

    __repr__ = sane_repr('id')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    class Meta:
        db_table = 'user'


class Address(BaseModel):
    # name and phone number default to user name and tel
    user = models.ForeignKey(User, related_name='addresses')
    # apt number or company name
    apt_number = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=120)
    # eg: Delivery Instructions. Ex. Call me when you’re outside!
    instructions = models.TextField(null=True, blank=True)
    # geo co-ordinates: lat,lon
    # from django.contrib.gis.geos import GEOSGeometry
    # GEOSGeometry('POINT(%s %s), 27700' % (lng, lat))
    # location = gis_models.PointField(max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'address'

    __repr__ = sane_repr('county', 'city', 'postcode')

    def __str__(self):
        return self.address_1
