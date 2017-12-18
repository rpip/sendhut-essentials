from random import choice
from django.core.management.base import BaseCommand, CommandError

from sendhut.dashboard.models import Allowance, AllowanceGroup
from ._factory import (
    UserFactory, CompanyFactory,
    AllowanceFactory, EmployeeFactory
)


class Command(BaseCommand):
    help = 'Generates fake data for the business accounts'

    def handle(self, *args, **options):
        # TODO(yao): create sample orders for users
        # create business account users
        self.stdout.write(self.style.SUCCESS('Creating dashboard data'))
        business_users = UserFactory.create_batch(2)
        for user in business_users:
            self._setup_business_user(user)

        self.stdout.write(self.style.SUCCESS('Stting up admin-biz'))
        admin = UserFactory.create(email='admin-biz@sendhut.com', username='admin-biz')
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password('h4ppy!h4ppy!')
        admin.save()
        self._setup_business_user(admin)

        self.stdout.write(self.style.SUCCESS('DONE'))

    def _setup_business_user(self, user):
        company = CompanyFactory.create(user=user)
        employees = EmployeeFactory.create_batch(choice(range(5, 15)), company=company)
        self.stdout.write(self.style.SUCCESS('DONE: Dashboard setup'))
        # TODO(yao): generate employee orders
