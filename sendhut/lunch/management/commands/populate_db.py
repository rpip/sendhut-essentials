from random import choice, shuffle
from django.core.management.base import BaseCommand, CommandError

from sendhut.lunch.models import Basket, Item
from ._factory import (
    UserFactory, ItemFactory,
    MenuFactory, SideMenuFactory,
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

        images = ImageFactory.create_batch(50)
        image_ids = [image.id for image in images]
        for index, item in enumerate(items):
            # create item images
            self._create_item_images(item.id, image_ids)
            item.categories = get_random_food_categories()
            item.save()
            if choice([True, False]):
                self.stdout.write(self.style.SUCCESS("Creating side menus"))
                side_menu1 = SideMenuFactory.create(item=item, multi_select=True)
                side_menu2 = SideMenuFactory.create(item=item, multi_select=False)
                side_menus = [side_menu1, side_menu2]
                # populate side menus
                for side_menu in side_menus:
                    SideItemFactory.create_batch(choice([3, 7]), menu=side_menu)

        self.stdout.write(self.style.SUCCESS("Creating side menu items"))

    def _create_item_images(self, item_id, image_ids):
        shuffle(image_ids)
        _images = image_ids[:choice(range(2, 5))]
        item_to_images = []
        for _id in _images:
            item_image = Item.images.through(item_id=item_id, image_id=_id)
            item_to_images.append(item_image)

        Item.images.through.objects.bulk_create(item_to_images, batch_size=10)

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
