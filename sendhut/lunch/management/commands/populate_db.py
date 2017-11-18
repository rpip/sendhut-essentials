from random import choice
from django.core.management.base import BaseCommand, CommandError

from sendhut.lunch.models import ItemImage
from ._factory import (
    UserFactory, AddressFactory, ItemFactory,
    MenuFactory, ItemImageFactory, SideMenuFactory,
    SideItemFactory, ImageFactory, PartnerFactory
)


class Command(BaseCommand):
    help = 'Populates the database with dummy Sendhut data'

    def handle(self, *args, **options):
        # raise CommandError()
        self.stdout.write(self.style.SUCCESS("Creating Partners"))
        users = UserFactory.create_batch(10)

        self.stdout.write(self.style.SUCCESS("Creating partners"))
        partners = PartnerFactory.create_batch(3)

        self.stdout.write(self.style.SUCCESS("Creating menus"))
        menu1 = MenuFactory.create_batch(2, partner=choice(partners))
        menu2 = MenuFactory.create_batch(4, partner=choice(partners))
        menu3 = MenuFactory.create_batch(2, partner=choice(partners))
        menu4 = MenuFactory.create_batch(3, partner=choice(partners))
        menu5 = MenuFactory.create_batch(2, partner=choice(partners))

        self.stdout.write(self.style.SUCCESS("Creating menu items"))
        items = ItemFactory.create_batch(choice(range(8, 20)), menu=choice(menu1))
        items += ItemFactory.create_batch(choice(range(3, 6)), menu=choice(menu1))

        items += ItemFactory.create_batch(choice(range(12, 16)), menu=choice(menu2))
        items += ItemFactory.create_batch(choice(range(2, 7)), menu=choice(menu2))

        items += ItemFactory.create_batch(choice(range(5, 8)), menu=choice(menu3))
        items += ItemFactory.create_batch(choice(range(4, 6)), menu=choice(menu3))

        items += ItemFactory.create_batch(choice(range(8, 15)), menu=choice(menu4))
        items += ItemFactory.create_batch(choice(range(5, 9)), menu=choice(menu4))

        items += ItemFactory.create_batch(choice(range(9, 12)), menu=choice(menu5))
        items += ItemFactory.create_batch(choice(range(5, 8)), menu=choice(menu5))

        self.stdout.write(self.style.SUCCESS("Creating side menus"))
        side_menus = []
        for x in range(0, 10):
            side_menus += SideMenuFactory.create_batch(2, item=items[x])

        self.stdout.write(self.style.SUCCESS("Creating side menu items"))
        side_menu_items = []
        for x in range(0, 10):
            toss = choice([True, False])
            if toss:
                side_menu_items += SideItemFactory.create_batch(choice([3, 5]),
                                                                menu=side_menus[x])

        images = ImageFactory.create_batch(40)
        for x in range(0, 30):
            ItemImageFactory.create(item=items[x], image=images[x])

        self.stdout.write(self.style.SUCCESS("Created {} users".format(len(users))))

        self.stdout.write(self.style.SUCCESS("Created {} items".format(len(items))))
