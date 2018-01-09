from datetime import datetime
from random import choice, shuffle
from uuid import uuid4
import six

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify
from django.conf import settings
from taggit.managers import TaggableManager
from djmoney.models.fields import MoneyField
from sorl.thumbnail import ImageField
from jsonfield import JSONField

from sendhut.utils import sane_repr, image_upload_path, generate_token
from sendhut.db import BaseModel


FOOD_TAGS = [
    'local gems', 'halal', 'pizza', 'vegetarian', 'deserts',
    'guilty', 'pleasures', 'chinese', 'fresh drinks', 'healthy', 'food'
]


class Partner(BaseModel):
    "Food vendor"
    # TODO(yao): rename model to Vendor
    # TODO(yao): add allergy information
    # TODO(yao): add restaurant notes
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    location = models.CharField(max_length=30, null=True, blank=True)
    logo = ImageField(upload_to=image_upload_path, null=True, blank=True)
    # banner is image displayed on restaurant's page
    slug = models.CharField(max_length=64)
    banner = ImageField(upload_to=image_upload_path, null=True, blank=True)
    tags = TaggableManager()

    def tags_tx(self):
        shuffle(FOOD_TAGS)
        return ', '.join(FOOD_TAGS[:3])

    class Meta:
        db_table = "partner"

    __repr__ = sane_repr('name', 'address')


class Menu(BaseModel):
    """
    For food vendors that offer different sets of menus either for lunch
    or on special occassions, menu labels can be used to group these menus.
    """
    # menu labels
    MAIN_MENU = 0
    BREAKFAST = 1
    LUNCH = 2
    DINNER = 3
    WEEKEND_SPECIAL = 4

    MENU_LABELS = (
        (MAIN_MENU, "Menu"),
        (BREAKFAST, "Breakfast"),
        (LUNCH, "Lunch"),
        (DINNER, "Dinner"),
        (WEEKEND_SPECIAL, "Weekend Special")
    )

    name = models.CharField(max_length=80, null=True, blank=True)
    partner = models.ForeignKey(Partner, related_name='menus')
    label = models.IntegerField(
        choices=MENU_LABELS,
        default=MAIN_MENU
    )

    class Meta:
        db_table = "menu"

    __repr__ = sane_repr('name', 'partner')

    def __unicode__(self):
        return "%s" % self.name


class Item(BaseModel):

    # TODO(yao): Generate thumbnails on save

    # dietary restrictions
    GLUTEN_FREE = 0
    DAIRY_FREE = 1
    VEGAN = 2
    VEGETARIAN = 3
    HALAL = 4

    DIETARY_RESTRICTIONS = [
        (GLUTEN_FREE, "Gluten Free"),
        (DAIRY_FREE, "Dairy Free"),
        (VEGAN, "Vegan"),
        (VEGETARIAN, "Vegetarian"),
        (HALAL, "Halal")
    ]

    # Food categories
    LOCAL_GEMS = 1
    HALAL = 2
    VEGETARIAN = 3
    DESSERTS_SWEET_TREATS = 4
    GUILTY_PLEASURES = 5
    BAKERY = 6
    FRESH_JUICE = 7
    HEALTHY_FOOD = 8

    FOOD_CATEGORIES = (
        (LOCAL_GEMS, 'Local gems'),
        (HALAL, 'Halal'),
        (VEGETARIAN, 'Vegetarian'),
        (DESSERTS_SWEET_TREATS, 'Desserts'),
        (DESSERTS_SWEET_TREATS, 'Sweet treats'),
        (GUILTY_PLEASURES, 'guilty pleasures'),
        (BAKERY, 'Bakery'),
        (FRESH_JUICE, 'Fresh Juice'),
        (HEALTHY_FOOD, 'Healthy Food')
    )

    categories = ArrayField(
        models.IntegerField(
            choices=FOOD_CATEGORIES
        ),
        default=list,
        blank=True
    )
    menu = models.ForeignKey(Menu, related_name='items')
    name = models.CharField(max_length=60)
    slug = models.CharField(max_length=64)
    description = models.TextField()
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    dietary_labels = ArrayField(
        models.IntegerField(
            choices=DIETARY_RESTRICTIONS
        ),
        default=list,
        blank=True
    )
    tags = TaggableManager()
    images = models.ManyToManyField('Image', related_name='items', through='ItemImage')
    available = models.BooleanField(default=True)

    @classmethod
    def dietary_label_text(cls, label_id):
        labels = {k: v for k, v in cls.DIETARY_RESTRICTIONS}
        return labels[label_id]

    @property
    def primary_image(self):
        # TODO(yao): Generate fixtures with primary image
        im = choice(self.images.all())
        return im.image

    class Meta:
        db_table = "item"


class Image(BaseModel):

    ONE_DAY = 60 * 60 * 24

    image = ImageField(upload_to=image_upload_path)
    thumbnail_path = models.CharField(max_length=200)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "image"

    def generate_unique_path(cls, timestamp):
        pieces = [six.text_type(x) for x in divmod(int(timestamp.strftime('%s')), ONE_DAY)]
        pieces.append(uuid4().hex)
        return u'/'.join(pieces)


class ItemImage(BaseModel):

    item = models.ForeignKey(Item)
    image = models.ForeignKey(Image)

    class Meta:
        db_table = 'item_image'
        unique_together = (('item', 'image'), )

    __repr__ = sane_repr('item', 'image')


class OptionGroup(BaseModel):
    """
    Menu of complimentary dishes (sides/options) for the selected food item.

    Exampples:
    - Choice of Dressing (for Grilled Chicken salad)
    - Choice of Flavor
    - Choice of size
    - Add ons
    - Appetizers
    - Choice of Protein (required)
    - Pizza sizes
    - Soups
    """
    name = models.CharField(max_length=60)
    item = models.ForeignKey(Item, related_name='option_groups', null=True, blank=True)
    is_required = models.BooleanField(default=False)
    multi_select = models.BooleanField(default=True)

    class Meta:
        db_table = 'option_group'


class Option(BaseModel):

    name = models.CharField(max_length=60)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    group = models.ForeignKey(OptionGroup, related_name='options')

    class Meta:
        db_table = 'option'

    __repr__ = sane_repr('name', 'price')

    def __unicode__(self):
        return "%s" % self.name


class Order(BaseModel):

    from datetime import datetime

    DELIVERY_TIMES = (
        '11:30',
        '12:00',
        '12:30',
        '1:00',
        '1:30',
        '2:00',
        '2:30'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    reference = models.CharField(max_length=8, unique=True)
    # TODO(yao): add helpers for calculating orders
    delivery_time = models.DateTimeField(default=datetime.now)
    delivery_address = models.CharField(max_length=120)
    delivery_fee = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    notes = models.CharField(max_length=300, null=True, blank=True)
    total_cost = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.reference = generate_token(8)
        super().save(*args, **kwargs)
        return self

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    @classmethod
    def get_today_delivery_schedules(cls):
        schedule = []
        for time in cls.DELIVERY_TIMES:
            hour, minute = time.split(':')
            schedule.append(datetime.today().replace(hour=int(hour), minute=int(minute)))
        return schedule

    class Meta:
        db_table = "order"


class OrderLine(BaseModel):

    item = models.ForeignKey(Item)
    quantity = models.IntegerField()
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    special_instructions = models.TextField(null=True, blank=True)
    order = models.ForeignKey(Order, related_name='order_lines')
    metadata = JSONField(null=True, blank=True)

    class Meta:
        db_table = "order_line"
