from random import choice, shuffle
from django.core.management.base import BaseCommand, CommandError

from sendhut.lunch.models import Item, OrderLine, Store
from .load_menus import create_lagos_stores
from ._factory import (
    ImageFactory, UserFactory, OptionGroupFactory,
    OptionFactory, OrderFactory, fake
)


ADMIN_PASSWORD = USER_PASSWORD = 'h3ll02018!'


def get_random_food_categories():
    n = choice(range(1, 4))
    categories = [k for k, _ in Item.FOOD_CATEGORIES]
    shuffle(categories)
    return categories[:n]


class Command(BaseCommand):
    help = 'Populates the database with dummy Sendhut data'

    def _setup_store(self, store):
        self.stdout.write(self.style.SUCCESS('Creating menus'))
        store.save()
        for menu in store.menus.all():
            self._setup_store_menu(menu)

        self.stdout.write(self.style.SUCCESS('Setup done for store'))

    def _setup_store_menu(self, menu):
        self.stdout.write(self.style.SUCCESS('Creating menu items'))
        items = menu.items.all()
        for item in items:
            if choice([True, False]):
                self.stdout.write(self.style.SUCCESS('Creating side menus'))
                opt_group1 = OptionGroupFactory.create(item=item, multi_select=True)
                opt_group2 = OptionGroupFactory.create(item=item, multi_select=False)
                opt_groups = [opt_group1, opt_group2]
                # populate side menus
                for opt_group in opt_groups:
                    OptionFactory.create_batch(choice([1, 3]), group=opt_group)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating ADMIN user'))

        # raise CommandError()
        self.stdout.write(self.style.SUCCESS('Creating users'))
        UserFactory.create_batch(3, password=USER_PASSWORD)

        self.stdout.write(self.style.SUCCESS('Creating stores'))
        ImageFactory.create_batch(12)
        create_lagos_stores(with_images=True)
        for store in Store.objects.all():
            self._setup_store(store)

        # create admin user
        self.stdout.write(self.style.SUCCESS('Setting up admin user'))
        admin = UserFactory.create(email='hello@sendhut.com', username='admin')
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(ADMIN_PASSWORD)
        admin.save()

        self.stdout.write(self.style.SUCCESS('Creating Orders'))
        orders = OrderFactory.create_batch(2, user=admin)
        for x in orders:
            self.create_orderlines(x)

        self.stdout.write(self.style.SUCCESS('DONE'))

    def create_orderlines(self, order):
        for x in range(1, choice([2, 5])):
            items = Item.objects.all()
            OrderLine.objects.create(
                quantity=choice(range(1, 6)),
                price=choice([1200, 900, 3500, 800, 400, 1400, 1650, 850]),
                special_instructions=fake.sentence(),
                order=order,
                item=choice(items)
            )


# IDEA(yao):
# create_fixture(store, menu_config)
# menu_config = {menu_1: [category, n_items], menu_2: [category, n_items]}
