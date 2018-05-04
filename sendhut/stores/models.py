from uuid import uuid4
import six

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.conf import settings
from taggit.managers import TaggableManager
from djmoney.models.fields import MoneyField
from sorl.thumbnail import ImageField
from sorl.thumbnail import get_thumbnail

from sendhut.utils import sane_repr, image_upload_path, unslugify
from sendhut.db import BaseModel
from . import FoodCategories, DietaryRestrictions


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
    class Meta:
        db_table = "partner"

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
    # TODO(yao): display 'Pre-order.' for Restaurants allowing orders ahead of opening
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
    # TODO(yao): Use choices to display availability: 'Closed',​'Unavailable'
    # store is opened or closed for some reason
    available = models.BooleanField(default=True)
    # display this store on site?
    # TODO(yao): rename to is_featured
    display = models.BooleanField(default=True)

    featured = StoreManager()

    def tags_tx(self):
        tags = self.tags.all()
        return ', '.join([unslugify(x.name) for x in tags[:3]])

    def get_absolute_url(self):
        return reverse('stores:store_detail', args=(self.self.slug, ))

    class Meta:
        db_table = "store"

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return self.id < other.id

    __repr__ = sane_repr('name', 'address')


class Menu(BaseModel):
    """
    For food stores that offer different sets of menus either for lunch
    or on special occassions, menu labels can be used to group these menus.
    """
    # TODO(yao): Add related menus that'll show as options, e.g, soup, meat, fish
    name = models.CharField(max_length=40, null=True, blank=True)
    store = models.ForeignKey(Store, related_name='menus')
    tags = TaggableManager(blank=True)
    info = models.CharField(max_length=360, null=True, blank=True)
    # does vendor charge for items in this menu?
    bowl_charge = MoneyField(
        max_digits=10, decimal_places=2,
        default_currency='NGN',
        null=True, blank=True)

    class Meta:
        db_table = "menu"

    __repr__ = sane_repr('name', 'store')

    def __str__(self):
        return "%s" % self.name


class Item(BaseModel):

    # TODO(yao): Generate thumbnails on save

    # TODO(yao): Use http://github.com/jazzband/django-model-utils
    categories = ArrayField(
        models.IntegerField(
            choices=FoodCategories.CHOICES
        ),
        default=list,
        blank=True
    )
    menu = models.ForeignKey(Menu, related_name='items')
    name = models.CharField(max_length=240)
    slug = models.CharField(max_length=240)
    description = models.TextField(null=True, blank=True)
    price = MoneyField(
        max_digits=10, decimal_places=2,
        default_currency='NGN', null=True, blank=True)
    dietary_labels = ArrayField(
        models.IntegerField(
            choices=DietaryRestrictions.CHOICES
        ),
        default=list,
        blank=True
    )
    image = models.ForeignKey('Image', related_name='items', blank=True, null=True)
    available = models.BooleanField(default=True)

    def get_price_per_item(self):
        return self.price if self.price else 0

    @property
    def bowl_charge(self):
        return self.menu.bowl_charge if self.menu.bowl_charge else 0

    @property
    def store(self):
        return self.menu.store

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

    # TODO(yao): delete from cache and index
    # from sorl.thumbnail import delete: delete(my_file)

    class Meta:
        db_table = "image"

    def generate_unique_path(cls, timestamp):
        pieces = [six.text_type(x) for x in divmod(int(timestamp.strftime('%s')), ONE_DAY)]
        pieces.append(uuid4().hex)
        return u'/'.join(pieces)

    def thumb_sm(self):
        return get_thumbnail(self.image, '128x128', crop='center')

    def thumb_lg(self):
        return get_thumbnail(self.image, '585x312', crop='center')

    def __str__(self):
        return str(self.id)


class OptionGroup(BaseModel):
    """
    Menu of complimentary sides/options for the selected food item.

    Exampples:
    - Choice of Dressing (for Grilled Chicken salad)
    - Choice of Flavor
    - Choice of size
    - Add ons (Choose between $min and $max)
    - Appetizers
    - Choice of Protein (required)
    - Pizza sizes
    - Soups
    - What sides would you like?
    - Would you like an extra piece of chicken
    When only one option/side?
    - Would you like to add XYZ? [x] Add XYZ
    """
    # TODO(yao): better error: You have selected too few options for "Choose Your Size"
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
    price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency=settings.DEFAULT_CURRENCY,
        null=True, blank=True
    )
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
