# TODO(yao): adjust delivery time slots to be dynamic
from datetime import datetime, timedelta


def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta


def build_time_slots(start=None, end=None):
    start = start or (datetime.now().replace(hour=11, minute=30))
    end = end or (start + timedelta(hours=7))
    slots = list(datetime_range(start, end, timedelta(minutes=30)))
    return zip(slots[:6], slots[1:])


def get_delivery_schedule(start_date=None):
    # TODO(yao): remove time slots that are within 30 minutes from time
    # order was placed, for Today orders
    now = datetime.now()
    dates = {
        'Today': now.date(),
        'Tomorrow': now + timedelta(days=1)
    }
    time_slots = [
        (t_start.strftime('%-I:%M %p'), t_end.strftime('%-I:%M %p'))
        for t_start, t_end in build_time_slots()
    ]
    return {'dates': dates, 'time_slots': time_slots}


def get_eta():
    pass


def calculate_delivery_cost():
    pass
