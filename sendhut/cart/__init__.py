from django.dispatch import Signal



cart_updated = Signal(providing_args=['group_order', 'cart'])
