from datetime import datetime
from random import choice
from uuid import uuid4
import six

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from taggit.managers import TaggableManager
from djmoney.models.fields import MoneyField
from sorl.thumbnail import ImageField
from jsonfield import JSONField

from sendhut.utils import sane_repr, image_upload_path, generate_token, unslugify
from sendhut.db import BaseModel
from sendhut.accounts.models import User


FOOD_TAGS = [
    'local gems', 'halal', 'pizza', 'vegetarian', 'desserts',
    'guilty pleasures', 'chinese', 'fresh drinks', 'healthy food'
]


class Vendor(BaseModel):
    "Food vendor"
    # TODO(yao): add allergy information
    # TODO(yao): add restaurant notes
    # TODO(yao): Add boolean field showing if restaurant is open today
    name = models.CharField(max_length=100)
    # TODO(yao): delete address
    address = models.CharField(max_length=200, null=True, blank=True)
    # TODO(yao): add multiple vendor phones
    phone = models.CharField(max_length=30, null=True, blank=True)
    # TODO(yao): Add locations for multipe vendor locations
    # VendorLocation: address, geo, phones
    # location = models.CharField(max_length=30, null=True, blank=True)
    logo = ImageField(upload_to=image_upload_path, null=True, blank=True)
    # banner is image displayed on restaurant's page
    slug = models.CharField(max_length=200)
    banner = ImageField(upload_to=image_upload_path, null=True, blank=True)
    tags = TaggableManager()

    def tags_tx(self):
        tags = self.tags.all()
        return ', '.join([unslugify(x.name) for x in tags[:3]])

    class Meta:
        db_table = "vendor"

    __repr__ = sane_repr('name', 'address')


class Menu(BaseModel):
    """
    For food vendors that offer different sets of menus either for lunch
    or on special occassions, menu labels can be used to group these menus.
    """
    # TODO(yao): Add related menus that'll show as options, e.g, soup, meat, fish
    name = models.CharField(max_length=40, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, related_name='menus')
    tags = TaggableManager()
    info = models.CharField(max_length=360, null=True, blank=True)

    class Meta:
        db_table = "menu"

    __repr__ = sane_repr('name', 'vendor')

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
    name = models.CharField(max_length=120)
    slug = models.CharField(max_length=240)
    description = models.TextField()
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    dietary_labels = ArrayField(
        models.IntegerField(
            choices=DIETARY_RESTRICTIONS
        ),
        default=list,
        blank=True
    )
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
    name = models.CharField(max_length=120)
    item = models.ForeignKey(Item, related_name='option_groups', null=True, blank=True)
    is_required = models.BooleanField(default=False)
    multi_select = models.BooleanField(default=True)
    menus = models.ManyToManyField(Menu, related_name='options', through='MenuOption')

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


class MenuOption(BaseModel):

    menu = models.ForeignKey(Menu)
    option_group = models.ForeignKey(OptionGroup)

    class Meta:
        db_table = 'menu_options'
        unique_together = (('menu', 'option_group'), )

    __repr__ = sane_repr('menu', 'option_group')


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
    payment = models.ForeignKey('Payment', null=True, blank=True)

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

    class Meta:
        db_table = "order_line"


class Payment(BaseModel):

    class Meta:
        db_table = 'payment'

    PENDING = 1
    CONFIRMED = 2
    FAILED = 3

    CASH = 1
    ONLINE = 2

    PAYMENT_STATUS = (
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (FAILED, 'Failed')
    )

    PAYMENT_SOURCE = (
        (CASH, 'Cash'),
        (ONLINE, 'Online')
    )
    reference = models.CharField(max_length=19)
    status = models.IntegerField(
        choices=PAYMENT_STATUS,
        default=PENDING
    )
    source = models.IntegerField(
        choices=PAYMENT_SOURCE,
        default=CASH
    )


class GroupCart(BaseModel):

    class Meta:
        db_table = "group_cart"

    name = models.CharField(max_length=20)
    owner = models.ForeignKey(User, related_name='owned_group_cart')
    vendor = models.ForeignKey(Vendor, related_name='group_carts')
    monetary_limit = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='NGN',
        null=True,
        blank=True
    )
    order = models.ForeignKey(Order, related_name='group_order', null=True, blank=True)
    payment = models.ForeignKey(Payment, null=True, blank=True)

    def save(self, *args, **kwargs):
        # TODO(yao): generate Heroku-style names for the group order
        self.name = generate_token(8)
        super().save(*args, **kwargs)
        return self


class GroupCartMember(BaseModel):

    class Meta:
        db_table = "group_cart_member"

    user = models.ForeignKey(User, related_name='group_carts', null=True, blank=True)
    group_cart = models.ForeignKey(GroupCart, related_name='members')
    # TODO(yao): make name non nullable
    name = models.CharField(max_length=40, null=True, blank=True)
    cart = JSONField(null=True, blank=True)
