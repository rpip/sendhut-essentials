from random import choice, shuffle, sample
from django.core.management.base import BaseCommand
from django.conf import settings

from sendhut.stores.models import Item, Store
from sendhut.factory import (
    ImageFactory, UserFactory, OptionGroupFactory,
    CartFactory, OptionFactory, OrderFactory, create_orderlines,
    GiveAwayFactory, CouponFactory, AddressFactory, GiveAwayStoreFactory,
    GiveAwayDropoffFactory
)
from .load_menus import create_lagos_stores


ADMIN_PASSWORD = USER_PASSWORD = 'h3ll02018!'


GTBANK_PASSWORD = 'hell0gt'


def get_random_food_categories():
    n = choice(range(1, 4))
    categories = [k for k, _ in Item.FOOD_CATEGORIES]
    shuffle(categories)
    return categories[:n]


class Command(BaseCommand):
    # TODO(yao): group order factory
    help = 'Populates the database with dummy Sendhut data'

    def add_arguments(self, parser):
        parser.add_argument('--with-giveaways', type=bool, default=False)

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
        admin = UserFactory.create(email=settings.SUPPORT_EMAIL, username='admin')
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(ADMIN_PASSWORD)
        admin.save()
        AddressFactory.create_batch(3, user=admin)

        self.stdout.write(self.style.SUCCESS('Creating admin cart'))
        # TODO(yao): add cart items from specific stores
        stores = Store.objects.all()
        cart = CartFactory.create(user=admin, stores=sample(list(stores), 2))
        self.stdout.write(self.style.SUCCESS('Creating Orders'))
        orders = OrderFactory.create_batch(2, user=admin)
        for x in orders:
            create_orderlines(x, [x.item for x in cart])

        self._create_giveaways(
            admin, sample(list(stores), 3), num_coupons=10)
        self._create_giveaways(
            users[0], sample(list(stores), 2), num_coupons=5)

        # GT Bank
        gtbank_user = UserFactory.create(
            email='platform@gtbank.com',
            username='gtplatform')
        gtbank_user.is_staff = True
        admin.is_superuser = True
        gtbank_user.set_password(GTBANK_PASSWORD)
        # set permissions on only giveaways
        gtbank_user.user_permissions.add()
        gtbank_user.save()

        self._create_giveaways(
            gtbank_user, sample(list(stores), 3), num_coupons=10)
        self._create_giveaways(
            gtbank_user, sample(list(stores), 3), num_coupons=10)

        self.stdout.write(self.style.SUCCESS('DONE'))

    def _create_giveaways(self, user, stores, num_coupons=10):
        self.stdout.write(self.style.SUCCESS('CREATING GIVEAWAYS'))
        giveaway = GiveAwayFactory(created_by=user)
        CouponFactory.create_batch(num_coupons, giveaway=giveaway)
        for store in stores:
            GiveAwayStoreFactory.create(giveaway=giveaway, store=store)

        GiveAwayDropoffFactory.create_batch(6, giveaway=giveaway)
        CouponFactory.create_batch(num_coupons, giveaway=giveaway)

    def _create_addresses(self, users):
        self.stdout.write(self.style.SUCCESS('Creating Addresses'))
        for u in users:
            AddressFactory.create_batch(3, user=u)
