import json
from pathlib import Path
from random import shuffle, choice

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from sendhut.lunch.models import Store, Menu, Item, Image, ItemVariant
from ._factory import ImageFactory

STORES_LIMIT = 15


class Command(BaseCommand):
    help = 'Loads restaurants from JSON file into DB'
    # TODO(yao): Load Options

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=STORES_LIMIT)
        parser.add_argument('--with-images', type=bool, default=False)

    def handle(self, *args, **options):
        limit = options['limit']
        with_images = options['with_images']
        self.stdout.write(self.style.SUCCESS('Loading JSON data'))
        if with_images:
            ImageFactory.create_batch(12)

        create_lagos_stores(limit, with_images=with_images)

        self.stdout.write(self.style.SUCCESS('DONE'))


def create_lagos_stores(n=STORES_LIMIT, with_images=False):
    lagos_stores_file = Path('etc/lagos-stores.json')
    with open(lagos_stores_file) as f:
        restaurants = json.load(f)
        shuffle(restaurants)
        for store in restaurants[:n]:
            add_store(store, with_images=with_images)


def create_item_images(item_id, image_ids):
    shuffle(image_ids)
    _images = image_ids[:choice(range(1, 3))]
    item_to_images = []
    for _id in _images:
        item_image = Item.images.through(item_id=item_id, image_id=_id)
        item_to_images.append(item_image)

    Item.images.through.objects.bulk_create(item_to_images, batch_size=10)


def add_store(data, with_images=False):

    images = Image.objects.all()

    name = data.pop('name')
    address = data.pop('address')
    menus = data.pop('menus')
    cuisines = data.pop('cuisines', [])
    store = Store.objects.create(
        name=name,
        address=address,
        banner=choice(images) if with_images else None,
        metadata=data
    )
    store.tags.add(*[slugify(x) for x in cuisines])
    # menus -> Item -> OptionGroup -> Options
    for m in menus:
        menu = Menu.objects.create(
            name=m['name'],
            store=store,
            info=m['description']
        )
        for x in m['items']:
            variants = x.pop('variants', [])
            item = Item.objects.create(
                name=x.pop('title'),
                price=x.pop('amount'),
                description=x.pop('description'),
                menu=menu,
                image=choice(images) if with_images else None,
                metadata=x
            )
            for v in variants:
                ItemVariant.objects.create(
                    name=v.pop('title'),
                    price_override=v.pop('price'),
                    image=choice(images) if with_images else None,
                    item=item
                )
