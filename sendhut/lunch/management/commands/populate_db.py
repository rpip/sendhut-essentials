from random import choice, shuffle
from django.core.management.base import BaseCommand, CommandError

from sendhut.lunch.models import Basket
from ._factory import (
    UserFactory, ItemFactory,
    MenuFactory, ItemImageFactory, SideMenuFactory,
    SideItemFactory, ImageFactory, PartnerFactory
)


def get_random_food_categories():
    n = choice(range(1, 4))
    categories = [k for k, _ in Basket.FOOD_CATEGORIES]
    shuffle(categories)
    return categories[:n]


class Command(BaseCommand):
    help = 'Populates the database with dummy Sendhut data'

    def _setup_partner(self, partner, menus_nbr=2):
        self.stdout.write(self.style.SUCCESS("Creating menus"))
        menus = MenuFactory.create_batch(menus_nbr, partner=partner)
        for menu in menus:
            self._setup_partner_menu(menu)

        self.stdout.write(self.style.SUCCESS("Setup done for partner"))

    def _setup_partner_menu(self, menu):
        self.stdout.write(self.style.SUCCESS("Creating menu items"))
        items = ItemFactory.create_batch(choice(range(8, 20)), menu=menu)

        self.stdout.write(self.style.SUCCESS("Creating side menus"))
        images = ImageFactory.create_batch(50)
        for index, item in enumerate(items):
            side_menus = SideMenuFactory.create_batch(2, item=item)
            ItemImageFactory.create(item=item, image=choice(images))
            item.categories = get_random_food_categories()
            item.save()
            if choice([True, False]):
                side_menus_nbr = len(side_menus)
                index = side_menus_nbr-1 if index >= side_menus_nbr else index
                SideItemFactory.create_batch(
                    choice([3, 5]), menu=side_menus[index])

        self.stdout.write(self.style.SUCCESS("Creating side menu items"))

    def handle(self, *args, **options):
        # raise CommandError()
        self.stdout.write(self.style.SUCCESS("Creating Partners"))
        # TODO(yao): Add orders
        UserFactory.create_batch(10)

        self.stdout.write(self.style.SUCCESS("Creating partners"))
        partners = PartnerFactory.create_batch(10)
        for partner in partners:
            self._setup_partner(partner)

        self.stdout.write(self.style.SUCCESS("DONE"))



# create_fixture(partner, menu_config)
# menu_config = {menu_1: [category, n_items], menu_2: [category, n_items]}
