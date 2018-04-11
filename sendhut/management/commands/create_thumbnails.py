from itertools import chain

from django.core.management.base import BaseCommand
from sorl.thumbnail import get_thumbnail
from django_rq import enqueue

from sendhut.lunch.models import Store


class Command(BaseCommand):
    help = 'Generate thumbanails for all store and item images'

    def handle(self, *args, **options):
        self.generate_thumbnails()

    def generate_thumbnails(self):
        self.stdout.write('Thumbanails generation:')
        stores = Store.featured.all()
        for store in stores:
            self.stdout.write('Generating store thumbnails: {}'.format(store.name))
            img = store.banner.image
            self.get_thumbnail(img, "350x187")  # home page
            self.get_thumbnail(img, "370x160")  # store page
            self.get_thumbnail(img, "576x288")  # checkout

            items = chain(*[menu.items.all() for menu in store.menus.all()])
            for item in items:
                if item.image:
                    self.stdout.write('Generating item thumbnails: {}'.format(item.name))
                    img = item.image.image
                    self.get_thumbnail(img, "350x160")  # item on store page, mobile
                    self.get_thumbnail(img, "128x128")  # item on store page
                    self.get_thumbnail(img, "585x312")  # item detail

        self.stdout.write('DONE: thumbanails generation:')

    def get_thumbnail(self, img, size):
        enqueue(get_thumbnail, img, size, crop="center")
