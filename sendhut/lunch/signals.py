from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Item, Store
from .views import GroupOrder
from sendhut.cart import Cart, cart_updated


@receiver(post_save, sender=Item)
@receiver(post_save, sender=Store)
def add_item_slug(sender, instance, created, **kwargs):
    if created:
        slug = '{}-{}'.format(slugify(instance.name), instance.id)
        instance.slug = slug
        instance.save()


@receiver(cart_updated, sender=Cart)
def update_group_order(sender, **kwargs):
    group_session = kwargs['group_session']
    cart = kwargs['cart']
    GroupOrder.update_member_cart(group_session, cart)
