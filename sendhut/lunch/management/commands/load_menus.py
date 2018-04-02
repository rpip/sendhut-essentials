import json
from pathlib import Path
from random import shuffle, choice

import yaml
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from sendhut.lunch.models import (
    Store, Menu, Item, Image, ItemVariant,
    Option, OptionGroup
)
from sendhut.factory import ImageFactory

STORES_LIMIT = 15


class Command(BaseCommand):
    help = 'Loads restaurants from JSON file into DB'
    # TODO(yao): Load Options

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=STORES_LIMIT)
        parser.add_argument('--with-images', type=bool, default=False)
        parser.add_argument('-f', '--file', type=str, action='append')

    def handle(self, *args, **options):
        limit = options['limit']
        with_images = options['with_images']
        menu_files = options['file']
        if menu_files:
            return self.load_from_menus(menu_files, with_images)

        self.stdout.write(self.style.SUCCESS('Loading JSON data'))
        if with_images:
            ImageFactory.create_batch(12)

        create_lagos_stores(limit, with_images=with_images)

        self.stdout.write(self.style.SUCCESS('DONE'))

    def load_from_menus(self, menu_files, with_images=False):
        for f in menu_files:
            with open(f) as _f:
                data = yaml.load(_f)
                # add 'name' key for menu to match scrapped data format
                data['menus'] = [dict({'name': k}, **v) for k, v in data['menus'].items()]
                self.stdout.write(self.style.SUCCESS('CREATING {}'.format(data['name'])))
                add_store(data, with_images=with_images)


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
    locations = data.pop('locations', None)
    if locations:
        # TODO(yao): create branches for each location
        address = locations[0]['address']
    else:
        address = data.pop('address')
    menus = data.pop('menus')
    cuisines = data.pop('cuisines', data.pop('tags', []))
    store, _ = Store.objects.get_or_create(
        name=name,
        address=address,
        banner=choice(images) if with_images else None,
        metadata=data
    )
    store.tags.add(*[slugify(x) for x in cuisines])
    # menus -> Item -> OptionGroup -> Options
    for m in menus:
        menu, _ = Menu.objects.get_or_create(
            name=m['name'],
            store=store,
            info=m.get('description')
        )
        variant_key = m.get('variant_key')
        for x in m['items']:
            variants = x.pop('variants', [])
            options = x.pop('options', [])
            item = Item.objects.create(
                name=x.pop('title', x.get('name')),
                price=x.pop('amount', x.get('price', None)),
                description=x.pop('description', ''),
                menu=menu,
                image=choice(images) if with_images else None,
                metadata=x
            )
            # HACK(yao):
            if isinstance(options, list):
                for opt in options:
                    opt_group = OptionGroup.objects.create(
                        name=opt['title'],
                        multi_select=opt.get('multi', True),
                        is_required=opt.get('required', False),
                        item=item
                    )
                    for x in opt['items']:
                        Option.objects.create(
                            name=x['name'],
                            price=x.get('price'),
                            group=opt_group
                        )

            if isinstance(variants, list):
                for v in variants:
                    ItemVariant.objects.create(
                        name=v.pop('title', v.get(variant_key)),
                        price_override=v.pop('price'),
                        image=choice(images) if with_images else None,
                        item=item
                    )
