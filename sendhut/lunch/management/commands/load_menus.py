import json
from pathlib import Path
from random import shuffle, choice

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from sendhut.lunch.models import Vendor, Menu, Item, Image
from ._factory import ImageFactory

VENDORS_LIMIT = 15


class Command(BaseCommand):
    help = 'Loads restaurants from JSON file into DB'
    # TODO(yao): Load Options

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=VENDORS_LIMIT)
        parser.add_argument('--with-images', type=bool, default=False)

    def handle(self, *args, **options):
        limit = options['limit']
        with_images = options['with_images']
        self.stdout.write(self.style.SUCCESS('Loading JSON data'))
        if with_images:
            ImageFactory.create_batch(12)

        create_lagos_vendors(limit, with_images=with_images)

        self.stdout.write(self.style.SUCCESS('DONE'))


def create_lagos_vendors(n=VENDORS_LIMIT, with_images=False):
    lagos_vendors_file = Path('etc/lagos-vendors.json')
    with open(lagos_vendors_file) as f:
        restaurants = json.load(f)
        shuffle(restaurants)
        for vendor in restaurants[:n]:
            add_vendor(vendor, with_images=with_images)


def create_item_images(item_id, image_ids):
    shuffle(image_ids)
    _images = image_ids[:choice(range(1, 3))]
    item_to_images = []
    for _id in _images:
        item_image = Item.images.through(item_id=item_id, image_id=_id)
        item_to_images.append(item_image)

    Item.images.through.objects.bulk_create(item_to_images, batch_size=10)


def setup_item_images(items, images):
    image_ids = [image.id for image in Image.objects.all()]
    shuffle(image_ids)
    for index, item in enumerate(items):
        # create item images
        create_item_images(item.id, image_ids)
        item.save()


def add_vendor(data, with_images=False):
    name = data.pop('name')
    address = data.pop('address')
    menus = data.pop('menus')
    cuisines = data.pop('cuisines', [])
    vendor = Vendor.objects.create(
        name=name,
        address=address,
        banner=ImageFactory._random_image(),
        metadata=data
    )
    vendor.tags.add(*[slugify(x) for x in cuisines])
    # menus -> Item -> OptionGroup -> Options
    for m in menus:
        menu = Menu.objects.create(
            name=m['name'],
            vendor=vendor,
            info=m['description']
        )
        for x in m['items']:
            Item.objects.create(
                name=x.pop('title'),
                price=x.pop('amount'),
                description=x.pop('description'),
                menu=menu,
                metadata=x
            )

    if with_images:
        images = Image.objects.all()
        setup_item_images(menu.items.all(), images)
