default_app_config = 'sendhut.grouporder.apps.GrouporderConfig'


class MemberStatus:
    """Enum of possible member modes/states"""
    IN = 'in'
    OUT = 'out'

    CHOICES = [
        (IN,  'IN - currently active'),
        (OUT, 'OUT - exited by user')
    ]
