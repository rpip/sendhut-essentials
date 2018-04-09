from django.dispatch import Signal


cart_updated = Signal(providing_args=['group_order', 'cart'])


class CartStatus:
    """Enum of possible cart statuses."""

    OPEN = 'open'
    CANCELED = 'canceled'
    LOCKED = 'locked'

    CHOICES = [
        (OPEN,  'Open - currently active'),
        (CANCELED, 'Canceled - canceled by user'),
        (LOCKED, 'Locked - locked by user checkout')
    ]
