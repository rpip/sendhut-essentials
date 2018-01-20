from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Item, Vendor
from .views import GroupOrder
from sendhut.cart import Cart, cart_updated


@receiver(post_save, sender=Item)
@receiver(post_save, sender=Vendor)
def add_item_slug(sender, instance, created, **kwargs):
    if created:
        slug = '{}-{}'.format(slugify(instance.name), instance.id)
        instance.slug = slug
        instance.save()


def payment_notification(sender, **kwargs):
    # mark order as paid
    pass


@receiver(cart_updated, sender=Cart)
def update_group_order(sender, **kwargs):
    group_cart = kwargs['group_cart']
    cart = kwargs['cart']
    member = kwargs['member']
    if group_cart:
        GroupOrder.update_member_cart(group_cart, cart, member)
