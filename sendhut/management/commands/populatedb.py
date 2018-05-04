from random import choice, shuffle
from django.core.management.base import BaseCommand, CommandError

from sendhut.stores.models import Item, Store
from sendhut.factory import (
    ImageFactory, UserFactory, OptionGroupFactory,
    CartFactory, GroupOrderFactory, OptionFactory,
    OrderFactory, create_orderlines,
)
from .load_menus import create_lagos_stores


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
        self.stdout.write(self.style.SUCCESS('Creating admin user'))
        admin = UserFactory.create(email='hello@sendhut.com', username='admin')
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(ADMIN_PASSWORD)
        admin.save()

        self.stdout.write(self.style.SUCCESS('Creating admin cart'))
        # TODO(yao): add cart items from specific stores
        cart = CartFactory.create(user=admin, stores=Store.objects.all()[:2])
        self.stdout.write(self.style.SUCCESS('Creating Orders'))
        orders = OrderFactory.create_batch(2, user=admin)
        for x in orders:
            create_orderlines(x, [x.item for x in cart])

        self.stdout.write(self.style.SUCCESS('DONE'))


# IDEA(yao):
# create_fixture(store, menu_config)
# menu_config = {menu_1: [category, n_items], menu_2: [category, n_items]}
