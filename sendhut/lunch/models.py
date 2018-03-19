from datetime import datetime
from uuid import uuid4
import six

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.conf import settings
from taggit.managers import TaggableManager
from djmoney.models.fields import MoneyField
from sorl.thumbnail import ImageField
from jsonfield import JSONField

from sendhut.utils import (
    sane_repr, image_upload_path,
    generate_token, unslugify, json_encode
)
from sendhut.db import BaseModel
from sendhut.accounts.models import User


class FOOD_TAGS:
    tags = {
        'local-gems': ['local', 'nigeria', 'africa'],
        'halal': ['halal'],
        'pizza': ['pizza'],
        'vegetarian': ['veggie', 'vegetarian', 'vegetable'],
        'desserts': ['desserts', 'sweets', 'cake'],
        'guilty-pleasures': [
            'pizza',
            'cake',
            'desserts',
            'sweets',
            'burger',
            'sandwich',
            'french',
            'italian'
        ],
        'chinese': ['chinese', 'asia'],
        'fresh-drinks': ['veggie', 'vegetarian', 'vegetable', 'fresh'],
        'healthy-food': ['veggie', 'vegetarian', 'vegetable', 'health']
    }

    @classmethod
    def labels(cls, human=False):
        labels = cls.tags.keys()
        return [unslugify(x) for x in labels] if human else labels

    @classmethod
    def tags_for(cls, label):
        return cls.tags.get(label, [])


class Partner(BaseModel):
    "Partner is the parent org/merchant that owns the stores"
    name = models.CharField(max_length=100)
    business_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, null=True, blank=True, unique=True)
    email = models.EmailField(max_length=70, null=True, blank=True, unique=True)
    has_fleets = models.BooleanField(default=False)


class StoreManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(display=True)


class Store(BaseModel):
    "Food store"
    # TODO(yao): rename store to Store
    # TODO(yao): add allergy information
    # TODO(yao): add restaurant notes
    name = models.CharField(max_length=100)
    manager_name = models.CharField(max_length=100, null=True, blank=True)
    partner = models.ForeignKey('Partner', related_name='store', blank=True, null=True)
    # TODO(yao): replace address with branches
    address = models.CharField(max_length=200, null=True, blank=True)
    # TODO(yao): add multiple store phones
    phone = models.CharField(max_length=30, null=True, blank=True, unique=True)
    # TODO(yao): Add Branch (address, geo, phones)
    email = models.EmailField(max_length=70, null=True, blank=True, unique=True)
    slug = models.CharField(max_length=200)
    logo = models.ForeignKey('Image', related_name='store', blank=True, null=True)
    # image displayed on restaurant's page
    banner = models.ForeignKey('Image', related_name='for_store', blank=True, null=True)
    tags = TaggableManager()
    verified = models.BooleanField(default=False)
    # TODO(yao): add is partner field
    # store is opened or closed for some reason
    available = models.BooleanField(default=True)
    # display this store on site?
    display = models.BooleanField(default=True)

    featured = StoreManager()

    def tags_tx(self):
        tags = self.tags.all()
        return ', '.join([unslugify(x.name) for x in tags[:3]])

    def get_absolute_url(self):
        return reverse('lunch:store_detail', args=(self.self.slug, ))

    class Meta:
        db_table = "store"

    def __str__(self):
        return self.name

    __repr__ = sane_repr('name', 'address')


class Menu(BaseModel):
    """
    For food stores that offer different sets of menus either for lunch
    or on special occassions, menu labels can be used to group these menus.
    """
    # TODO(yao): Add related menus that'll show as options, e.g, soup, meat, fish
    name = models.CharField(max_length=40, null=True, blank=True)
    store = models.ForeignKey(Store, related_name='menus')
    tags = TaggableManager()
    info = models.CharField(max_length=360, null=True, blank=True)

    class Meta:
        db_table = "menu"

    __repr__ = sane_repr('name', 'store')

    def __str__(self):
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

    # TODO(yao): Use http://github.com/jazzband/django-model-utils
    categories = ArrayField(
        models.IntegerField(
            choices=FOOD_CATEGORIES
        ),
        default=list,
        blank=True
    )
    menu = models.ForeignKey(Menu, related_name='items')
    name = models.CharField(max_length=240)
    slug = models.CharField(max_length=240)
    description = models.TextField(null=True, blank=True)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    dietary_labels = ArrayField(
        models.IntegerField(
            choices=DIETARY_RESTRICTIONS
        ),
        default=list,
        blank=True
    )
    image = models.ForeignKey('Image', related_name='items', blank=True, null=True)
    available = models.BooleanField(default=True)

    @classmethod
    def dietary_label_text(cls, label_id):
        labels = {k: v for k, v in cls.DIETARY_RESTRICTIONS}
        return labels[label_id]

    class Meta:
        db_table = "item"

    def __str__(self):
        return self.name


class ItemVariant(BaseModel):
    name = models.CharField(max_length=100, blank=True)
    price_override = MoneyField(
        default_currency=settings.DEFAULT_CURRENCY,
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True)
    item = models.ForeignKey(
        Item, related_name='variants', on_delete=models.CASCADE)
    image = models.ForeignKey(
        'Image', related_name='variants',
        null=True, blank=True)

    class Meta:
        db_table = "variant"

    def __str__(self):
        return self.name


class Image(BaseModel):

    ONE_DAY = 60 * 60 * 24

    image = ImageField(upload_to=image_upload_path)
    thumbnail_path = models.CharField(max_length=200)

    class Meta:
        db_table = "image"

    def generate_unique_path(cls, timestamp):
        pieces = [six.text_type(x) for x in divmod(int(timestamp.strftime('%s')), ONE_DAY)]
        pieces.append(uuid4().hex)
        return u'/'.join(pieces)

    def __str__(self):
        return str(self.id)


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
    item = models.ForeignKey(
        Item,
        related_name='option_groups',
        null=True, blank=True)
    variant = models.ForeignKey(
        ItemVariant,
        related_name='option_groups',
        null=True, blank=True)
    is_required = models.BooleanField(default=False)
    multi_select = models.BooleanField(default=True)
    menus = models.ManyToManyField(Menu, related_name='options', through='MenuOption')

    class Meta:
        db_table = 'option_group'


class Option(BaseModel):

    name = models.CharField(max_length=60)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency=settings.DEFAULT_CURRENCY)
    group = models.ForeignKey(OptionGroup, related_name='options')

    class Meta:
        db_table = 'option'

    __repr__ = sane_repr('name', 'price')

    def __str__(self):
        return "%s" % self.name


class MenuOption(BaseModel):

    menu = models.ForeignKey(Menu)
    option_group = models.ForeignKey(OptionGroup)

    class Meta:
        db_table = 'menu_options'
        unique_together = (('menu', 'option_group'), )

    __repr__ = sane_repr('menu', 'option_group')


class Order(BaseModel):

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
    delivery_fee = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency=settings.DEFAULT_CURRENCY
    )
    notes = models.CharField(max_length=300, null=True, blank=True)
    total_cost = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency=settings.DEFAULT_CURRENCY
    )
    payment = models.IntegerField(
        choices=PAYMENT_STATUS,
        default=PENDING
    )
    payment_source = models.IntegerField(
        choices=PAYMENT_SOURCE,
        default=CASH
    )
    group_cart = models.OneToOneField('GroupCart', related_name='order', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.created:
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

    @classmethod
    def create_from_cart(cls, cart, **kwargs):
        order = cls.objects.create(**kwargs)
        for line in cart:
            OrderLine.objects.create(
                item_id=line.id,
                quantity=line.quantity,
                price=line.data['total'],
                order=order,
                special_instructions=line.data['note'],
                metadata=json_encode(line.data)
            )
        return order

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


class GroupCart(BaseModel):
    """
    Model for holding group orders.
    """
    OPEN = 1
    LOCKED = 2

    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (LOCKED, 'Locked')
    ]

    class Meta:
        db_table = "group_cart"

    token = models.CharField(max_length=10)
    owner = models.ForeignKey(User, related_name='group_carts')
    store = models.ForeignKey(Store, related_name='group_carts')
    monetary_limit = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='NGN',
        null=True,
        blank=True
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=OPEN)

    @staticmethod
    def get_user_open_carts(user):
        return GroupCart.objects.filter(
            members__user=user,
            status=GroupCart.OPEN
        )

    def save(self, *args, **kwargs):
        # TODO(yao): generate Heroku-style names for the group order
        if not self.created:
            self.token = generate_token(6)
        super().save(*args, **kwargs)
        return self

    def lock(self):
        self.update(status=self.LOCKED)

    def unlock(self):
        self.update(status=self.OPEN)

    def is_open(self):
        return self.status == self.OPEN

    def cancel(self):
        self.delete()

    def get_absolute_url(self):
        return reverse('lunch:cart_join', args=(self.token, ))

    def __str__(self):
        return self.token


class GroupCartMember(BaseModel):

    class Meta:
        db_table = "group_cart_member"

    user = models.ForeignKey(User, related_name='joined_group_carts',
                             null=True, blank=True)
    group_cart = models.ForeignKey(GroupCart, related_name='members')
    name = models.CharField(max_length=40)
    # holds user's cart for current group order session
    cart = JSONField(null=True, blank=True, default=[])
