from faker import Faker
from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField

from sendhut import utils
from sendhut.db import BaseModel
from sendhut.accounts.models import Address
# TODO(yao): add employee, upload csv


class Company(BaseModel):
    # TODO(yao): billing info
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address)

    class Meta:
        db_table = 'company'


class Employee(BaseModel):

    MEMBER = 0
    ADMIN = 1

    ROLES = [
        (MEMBER, 'Member'),
        (ADMIN, 'Admin')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    role = models.IntegerField(
        choices=ROLES,
        default=MEMBER,
        blank=True,
        null=True
    )
    company = models.ForeignKey(Company, related_name='employees')

    class Meta:
        db_table = 'employee'


class Allowance(BaseModel):

    DAILY = 0
    WEEKLY = 1

    FREQUENCY = [
        (DAILY, 'daily'),
        (WEEKLY, 'weekly')
    ]

    def _generate_random_name():
        fake = Faker()
        token = utils.generate_token()
        word = '{}-{}-{}'.format(token, fake.color_name(), fake.street_name())
        return word.replace(' ', '-')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=_generate_random_name()
    )
    frequency = models.IntegerField(
        choices=FREQUENCY,
        default=WEEKLY,
        blank=True,
        null=True
    )
    limit = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    company = models.ForeignKey(Company, related_name='allowances')
    members = models.ManyToManyField(
        Employee,
        related_name='allowances',
        through='AllowanceGroup'
    )

    class Meta:
        db_table = 'allowance'


class AllowanceGroup(BaseModel):
    employee = models.ForeignKey(Employee)
    allowance = models.ForeignKey(Allowance)

    class Meta:
        db_table = 'allowance_group'


class Invite(BaseModel):
    invite_token = models.CharField(max_length=32)
    date_joined = models.DateTimeField(blank=True)
    company = models.ForeignKey(Company, related_name='invited_employees')

    @staticmethod
    def mark_joined(token):
        pass
