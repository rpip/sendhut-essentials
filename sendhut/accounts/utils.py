from .models import Address


def make_default_address(id):
    addr = Address.objects.get(id=id)
    addr.user.addresses.update(is_default=False)
    addr.is_default = True
    addr.save(update_fields=['is_default'])
