from itertools import groupby

from django.db import models
from django.utils.encoding import smart_str
from django.conf import settings
from djmoney.money import Money

from sendhut.lunch.models import Option


class ItemSet(object):
    """
    Represents a set of products like an order or a basket
    """
    def __iter__(self):
        raise NotImplementedError()

    def get_total(self, **kwargs):
        return sum([item.get_total(**kwargs) for item in self])

    def count(self):
        """Return the total quantity in cart."""
        lines = self.lines.all()
        return lines.aggregate(total_quantity=models.Sum('quantity'))


class ItemList(list, ItemSet):

    def __repr__(self):
        return 'ItemList(%s)' % (super(ItemList, self).__repr__(),)


class ItemLine:
    "Represents a single item in a cart or basket"

    @property
    def store(self):
        return self.item.menu.store

    def get_quantity(self):
        return self.quantity

    def get_total(self):
        """Return the total price of this line."""
        # return total.amount.quantize(CENTS)
        return self.get_price_per_item() * self.quantity

    def get_price_per_item(self):
        """Return the unit price of the line."""
        return self.item.get_price_per_item() + self.get_options_total()

    def _get_extras(self):
        extras = self.data.get('extras', [])
        _extras = []
        if extras:
            extras = list(map(int, extras))
            for option in Option.objects.filter(id__in=extras):
                _extras.append({
                    'id': int(option.id),
                    'uuid': str(option.uuid),
                    'name': option.name,
                    'price': option.price.amount if option.price else 0,
                    'parent': option.group.name
                })

        return _extras

    def get_options_total(self):
        options = self._get_extras()
        return Money(sum([x['price'] for x in options]), settings.DEFAULT_CURRENCY)

    def __str__(self):
        return smart_str(self.item)

    def __eq__(self, other):
        if not isinstance(other, ItemLine):
            return NotImplemented

        return (
            self.item == other.item and
            self.quantity == other.quantity and
            self.data == other.data)

    def __ne__(self, other):
        return not self == other  # pragma: no cover

    def __getstate__(self):
        return self.item, self.quantity, self.data

    def __setstate__(self, data):
        self.item, self.quantity, self.data = data


class Partitioner(ItemSet):
    """
    Represents an ItemSet partitioned for purposes such as delivery
    Override the __iter__() method to provide custom partitioning.
    """
    def __init__(self, subject):
        self.subject = subject

    def __iter__(self):
        'Override this method to provide custom partitioning'
        yield ItemList(self.subject)

    def __nonzero__(self):
        return bool(self.subject)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.subject)

    def classify(self, item):
        raise NotImplementedError()

    def get_partition(self, classifier, items):
        return ItemList(items)


class GroupingPartitioner(Partitioner):

    def __init__(self, subject, keyfunc, partition_class):
        self.keyfunc = keyfunc
        self.partition_class = partition_class
        super(GroupingPartitioner, self).__init__(subject)

    def __iter__(self):
        subject = sorted(self.subject, key=self.classify)
        for classifier, items in groupby(subject, key=self.classify):
            yield (classifier, self.get_partition(classifier, items))

    def classify(self, item):
        return self.keyfunc(item)

    def get_partition(self, classifier, items):
        return self.partition_class(items)


def partition(subject, keyfunc, partition_class=list):
    return GroupingPartitioner(subject, keyfunc, partition_class)
