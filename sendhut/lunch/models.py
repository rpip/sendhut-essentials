from uuid import uuid4
from random import choice
import six

from django.db import models
from django.contrib.postgres.fields import ArrayField
from taggit.managers import TaggableManager
from djmoney.models.fields import MoneyField
from sorl.thumbnail import ImageField

from sendhut.utils import sane_repr, image_upload_path
from sendhut.db import BaseModel


class Partner(BaseModel):
    "Food vendors"

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    location = models.CharField(max_length=30, null=True, blank=True)

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

    # dietary restrictions
    GLUTEN_FREE = 0
    DAIRY_FREE = 1
    VEGAN = 2
    PALEO = 3

    DIETARY_RESTRICTIONS = [
        (GLUTEN_FREE, "Gluten Free"),
        (DAIRY_FREE, "Dairy Free"),
        (VEGAN, "Vegan"),
        (PALEO, "Paleo")
    ]

    # Food categories
    LOCAL_GEMS = 1
    CONTINENTAL = 2
    OUR_PICKS = 3
    TODAY_SPECIAL = 4
    TOMORROW_SPECIAL = 5
    FRUITS_AND_DRINKS = 6

    FOOD_CATEGORIES = (
        (LOCAL_GEMS, 'Local Gems'),
        (CONTINENTAL, 'Continental'),
        (OUR_PICKS, 'Our Picks'),
        (TODAY_SPECIAL, 'Today\'s Special'),
        (TOMORROW_SPECIAL, 'Tomorrow\'s Special'),
        (FRUITS_AND_DRINKS, 'Fruits and Drinks')
    )
    category = models.IntegerField(
        choices=FOOD_CATEGORIES,
        null=True,
        blank=True
    )
    menu = models.ForeignKey(Menu, related_name='items')
    name = models.CharField(max_length=60)
    description = models.TextField()
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    dietary_labels = ArrayField(
        models.IntegerField(
            choices=DIETARY_RESTRICTIONS,
            null=True,
            blank=True
        ))
    tags = TaggableManager()
    images = models.ManyToManyField('Image', related_name='items', through='ItemImage')

    @classmethod
    def get_random_food_category(cls):
        _ids = [_id for (name, _id) in cls.FOOD_CATEGORIES]
        return choice(_ids)

    class Meta:
        db_table = "item"


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


class ItemImage(BaseModel):

    item = models.ForeignKey(Item)
    image = models.ForeignKey(Image)

    class Meta:
        db_table = 'item_image'
        unique_together = (('item', 'image'), )

    __repr__ = sane_repr('item', 'image')


class SideMenu(BaseModel):
    """
    Menu of complimentary dishes or options of the selected food item.

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
    item = models.ForeignKey(Item, related_name='side_menus')
    is_required = models.BooleanField(default=False)

    class Meta:
        db_table = 'side_menu'


class SideItem(BaseModel):

    name = models.CharField(max_length=60)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='NGN')
    menu = models.ForeignKey(SideMenu, related_name='items')

    class Meta:
        db_table = 'side_item'

    __repr__ = sane_repr('name', 'price')

    def __unicode__(self):
        return "%s" % self.name
