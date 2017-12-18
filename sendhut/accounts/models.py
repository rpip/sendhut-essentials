from django.contrib.auth.models import AbstractUser
from django.db import models

from sendhut.utils import sane_repr
from sendhut.db import BaseModel


class User(AbstractUser, BaseModel):

    phone = models.CharField(max_length=20)
    last_login = models.DateTimeField(null=True, blank=True)
    identity_verified = models.BooleanField(default=False)

    __repr__ = sane_repr('id')

    @property
    def is_business_account(self):
        pass

    class Meta:
        db_table = 'user'


class Address(BaseModel):
    user = models.ForeignKey(User, related_name='addresses')
    postcode = models.CharField(max_length=10, null=True, blank=True)
    county = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=64)
    # geo co-ordinates: lat,lon
    # from django.contrib.gis.geos import GEOSGeometry
    # GEOSGeometry('POINT(%s %s), 27700' % (lng, lat))
    # location = gis_models.PointField(max_length=64, null=True, blank=True)
    location = models.CharField(max_length=30, null=True, blank=True)
    address_1 = models.CharField(max_length=254)
    address_2 = models.CharField(max_length=254, null=True, blank=True)
    address_3 = models.CharField(max_length=254, null=True, blank=True)

    class Meta:
        db_table = 'address'

    __repr__ = sane_repr('county', 'city', 'postcode')

    def __unicode__(self):
        return self.address_1
