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


class IssueResolutions:
    "Enum of possible ways of resolving issues"

    STORE_RECOMMENDATION = 'store'
    LEAVE_ITEM = 'leave'
    CANCEL_ORDER = 'cancel'
    CONTACT_ME = 'contact me'

    CHOICES = [
        (STORE_RECOMMENDATION, "Go with the store's recommendation"),
        (LEAVE_ITEM, "Leave out the selected item"),
        (CANCEL_ORDER, "Cancel the entire order"),
        (CONTACT_ME, "Contact me")
    ]
