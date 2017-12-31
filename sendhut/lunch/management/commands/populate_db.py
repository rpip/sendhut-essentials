from random import choice, shuffle
from django.core.management.base import BaseCommand, CommandError

from sendhut.lunch.models import Basket, Item
from sendhut.dashboard.models import Allowance
from ._factory import (
    UserFactory, ItemFactory,
    MenuFactory, OptionGroupFactory,
    OptionFactory, ImageFactory, PartnerFactory,
    CompanyFactory, AllowanceFactory, EmployeeFactory,
    InviteFactory
)


def get_random_food_categories():
    n = choice(range(1, 4))
    categories = [k for k, _ in Basket.FOOD_CATEGORIES]
    shuffle(categories)
    return categories[:n]


class Command(BaseCommand):
    help = 'Populates the database with dummy Sendhut data'

    def _setup_partner(self, partner, menus_nbr=6):
        self.stdout.write(self.style.SUCCESS('Creating menus'))
        menus = MenuFactory.create_batch(menus_nbr, partner=partner)
        for menu in menus:
            self._setup_partner_menu(menu)

        self.stdout.write(self.style.SUCCESS('Setup done for partner'))

    def _setup_partner_menu(self, menu):
        self.stdout.write(self.style.SUCCESS('Creating menu items'))
        items = ItemFactory.create_batch(choice(range(3, 8)), menu=menu)

        images = ImageFactory.create_batch(50)
        image_ids = [image.id for image in images]
        for index, item in enumerate(items):
            # create item images
            self._create_item_images(item.id, image_ids)
            item.categories = get_random_food_categories()
            item.save()
            if choice([True, False]):
                self.stdout.write(self.style.SUCCESS('Creating side menus'))
                opt_group1 = OptionGroupFactory.create(item=item, multi_select=True)
                opt_group2 = OptionGroupFactory.create(item=item, multi_select=False)
                opt_groups = [opt_group1, opt_group2]
                # populate side menus
                for opt_group in opt_groups:
                    OptionFactory.create_batch(choice([3, 7]), group=opt_group)

        self.stdout.write(self.style.SUCCESS('Creating side menu items'))

    def _create_item_images(self, item_id, image_ids):
        shuffle(image_ids)
        _images = image_ids[:choice(range(2, 5))]
        item_to_images = []
        for _id in _images:
            item_image = Item.images.through(item_id=item_id, image_id=_id)
            item_to_images.append(item_image)

        Item.images.through.objects.bulk_create(item_to_images, batch_size=10)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating ADMIN user'))

        # raise CommandError()
        self.stdout.write(self.style.SUCCESS('Creating Partners'))
        # TODO(yao): Add orders
        users = UserFactory.create_batch(10)

        self.stdout.write(self.style.SUCCESS('Creating partners'))
        partners = PartnerFactory.create_batch(10)
        for partner in partners:
            self._setup_partner(partner, choice(range(4, 6)))

        # TODO(yao): create sample orders for users
        # create business account users
        self.stdout.write(self.style.SUCCESS('Creating dashboard data'))
        business_users = users[:2]
        for user in business_users:
            self._setup_business_user(user)

        # create admin user
        self.stdout.write(self.style.SUCCESS('Setting up admin user'))
        admin = UserFactory.create(email='admin@sendhut.com', username='admin')
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password('sendhut2017')
        admin.save()
        self._setup_business_user(admin)

        self.stdout.write(self.style.SUCCESS('DONE'))

    def _setup_business_user(self, user):
        company = CompanyFactory.create(user=user)
        employees = EmployeeFactory.create_batch(choice(range(5, 15)), company=company)
        allowances = AllowanceFactory.create_batch(choice(range(2, 4)), created_by=user, company=company)
        allowance_groups = []
        for e in employees:
            allowance = choice(allowances)
            e.allowance = allowance
            e.save()

        #InviteFactory.create_batch(choice(range(4, 9)), allowance=choice(allowances), company=company)
        self.stdout.write(self.style.SUCCESS('DONE: Dashboard setup'))
        # TODO(yao): generate employee orders


# IDEA(yao):
# create_fixture(partner, menu_config)
# menu_config = {menu_1: [category, n_items], menu_2: [category, n_items]}
