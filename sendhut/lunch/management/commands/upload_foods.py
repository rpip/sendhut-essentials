import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from sendhut.lunch.models import Vendor, Menu, Item


class Command(BaseCommand):
    help = 'Loads restaurants from JSON file into DB'
    # TODO(yao): Load Options

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading JSON data'))
        create_lagos_vendors()

        self.stdout.write(self.style.SUCCESS('DONE'))


def create_lagos_vendors(n=20):
    lagos_vendors_file = Path('etc/lagos-vendors.json')
    with open(lagos_vendors_file) as f:
        restaurants = json.load(f)
        for vendor in restaurants[n]:
            add_vendor(vendor)


def add_vendor(data):
    name = data.pop('name')
    address = data.pop('address')
    menus = data.pop('menus')
    cuisines = data.pop('cuisines')
    vendor = Vendor.objects.create(name=name, address=address, metadata=data)
    vendor.tags.add(*[slugify(x) for x in cuisines])
    # menus -> Item -> OptionGroup -> Options
    for m in menus:
        menu = Menu.objects.create(
            name=m['name'],
            vendor=vendor,
            info=m['description']
        )
        for x in m['items']:
            item = Item.objects.create(
                name=x['title'],
                price=x['amount'],
                description=x['description'],
                menu=menu
            )
