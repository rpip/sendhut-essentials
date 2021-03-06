from random import choice, shuffle, sample
from django.core.management.base import BaseCommand
from django.conf import settings

from sendhut.stores.models import Item, Store
from sendhut.factory import (
    ImageFactory, UserFactory, OptionGroupFactory,
    CartFactory, OptionFactory, OrderFactory, create_orderlines,
    AddressFactory
)
from .load_menus import create_lagos_stores


ADMIN_PASSWORD = USER_PASSWORD = 'h3ll02018!'


def get_random_food_categories():
    n = choice(range(1, 4))
    categories = [k for k, _ in Item.FOOD_CATEGORIES]
    shuffle(categories)
    return categories[:n]


class Command(BaseCommand):
    # TODO(yao): group order factory
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
        users = UserFactory.create_batch(3, password=USER_PASSWORD)
        self._create_addresses(users)

        self.stdout.write(self.style.SUCCESS('Creating stores'))
        ImageFactory.create_batch(12)
        create_lagos_stores(with_images=True)
        for store in Store.objects.all():
            self._setup_store(store)

        # create admin user
        self.stdout.write(self.style.SUCCESS('Creating admin user'))
        admin = UserFactory.create(
            email=settings.SUPPORT_EMAIL,
            username='admin'
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(ADMIN_PASSWORD)
        admin.save()
        AddressFactory.create_batch(3, user=admin)

        self.stdout.write(self.style.SUCCESS('Creating admin cart'))
        # TODO(yao): add cart items from specific stores
        # cart = CartFactory.create(user=admin, stores=sample(list(stores), 2))
        # self.stdout.write(self.style.SUCCESS('Creating Orders'))
        # orders = OrderFactory.create_batch(2, user=admin)
        # for x in orders:
        #     create_orderlines(x, [x.item for x in cart])
        self.stdout.write(self.style.SUCCESS('DONE'))

    def _create_addresses(self, users):
        self.stdout.write(self.style.SUCCESS('Creating Addresses'))
        for u in users:
            AddressFactory.create_batch(3, user=u)
