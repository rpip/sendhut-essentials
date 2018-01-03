from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField

from sendhut.utils import sane_repr
from sendhut.db import BaseModel
from sendhut.accounts.models import Address


class Company(BaseModel):
    # TODO(yao): billing info
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Employee.objects.create(
            user=self.user,
            company=self,
            role=Employee.ADMIN
        )

    class Meta:
        db_table = 'company'


class Employee(BaseModel):

    MEMBER = 0
    ADMIN = 1

    ROLES = [
        (MEMBER, 'Member'),
        (ADMIN, 'Admin')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    role = models.IntegerField(
        choices=ROLES,
        default=MEMBER,
        blank=True,
        null=True
    )
    company = models.ForeignKey(Company, related_name='employees')
    allowance = models.ForeignKey('Allowance', related_name='members', null=True, blank=True)

    def role_text(self):
        return dict(self.ROLES)[self.role]

    class Meta:
        db_table = 'employee'


class Allowance(BaseModel):

    DAILY = 0
    WEEKLY = 1

    FREQUENCY = [
        (DAILY, 'daily'),
        (WEEKLY, 'weekly')
    ]

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    frequency = models.IntegerField(
        choices=FREQUENCY,
        default=WEEKLY,
        blank=True,
        null=True
    )
    limit = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    company = models.ForeignKey(Company, related_name='allowances')

    def frequency_text(self):
        return dict(self.FREQUENCY)[self.frequency].capitalize()

    def __str__(self):
        return "%s" % self.limit

    class Meta:
        db_table = 'allowance'


class Invite(BaseModel):
    # TODO: resend invitation
    email = models.CharField(max_length=32)
    token = models.CharField(max_length=32)
    date_joined = models.DateTimeField(blank=True, null=True)
    company = models.ForeignKey(Company, related_name='invited_employees')
    allowance = models.ForeignKey('Allowance', null=True, blank=True)
    role = models.IntegerField(
        choices=Employee.ROLES,
        default=Employee.MEMBER,
        blank=True,
        null=True
    )

    def role_text(self):
        return dict(Employee.ROLES)[self.role]

    class Meta:
        db_table = 'invite'
