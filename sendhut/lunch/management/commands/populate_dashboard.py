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

        self.stdout.write(self.style.SUCCESS('DONE'))

    def _setup_business_user(self, user):
        company = CompanyFactory.create(user=user)
        employees = EmployeeFactory.create_batch(choice(range(5, 15)), company=company)
        allowances = AllowanceFactory.create_batch(2, created_by=user, company=company)
        allowance_groups = []
        for x in employees:
            allowance = choice(allowances)
            _allowance = Allowance.members.through(
                employee_id=x.id,
                allowance_id=allowance.id
            )
            allowance_groups.append(_allowance)

        AllowanceGroup.objects.bulk_create(allowance_groups, batch_size=100)
        self.stdout.write(self.style.SUCCESS('DONE: Dashboard setup'))
        # TODO(yao): generate employee orders
