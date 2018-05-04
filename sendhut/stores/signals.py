from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Item, Store


@receiver(post_save, sender=Item)
@receiver(post_save, sender=Store)
def add_item_slug(sender, instance, created, **kwargs):
    if created:
        slug = '{}-{}'.format(slugify(instance.name), instance.id)
        instance.slug = slug
        instance.save()
