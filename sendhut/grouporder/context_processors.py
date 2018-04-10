"""Group order related context processors."""
from .utils import get_group_member_from_request


def group_order(request):
    """Inject group order info into context"""
    member = get_group_member_from_request(request)
    if member:
        return {
            'group_order': member.group_order,
            'member': member,
            'cart': member.cart
        }

    return {}
