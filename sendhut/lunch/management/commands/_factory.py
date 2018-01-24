from random import choice, shuffle
import glob

from django.conf import settings
from django.core.files import File
from django.utils.text import slugify
from faker import Faker
from factory import (
    DjangoModelFactory, SubFactory,
    LazyFunction, lazy_attribute, Sequence,
    post_generation
)

from sendhut.accounts.models import User, Address
from sendhut.lunch.models import (
    Vendor, Menu, Item, OptionGroup, Option,
    Image, ItemImage, OrderLine, Order, FOOD_TAGS
)


fake = Faker()


def get_food_tags():
    labels = FOOD_TAGS.labels()
    shuffle(labels)
    n = choice(range(0, len(labels)))
    label = labels[n]
    return FOOD_TAGS.tags_for(label)


def random_diet_labels():
    items = [x[0] for x in Item.DIETARY_RESTRICTIONS]
    shuffle(items)
    _len = choice(range(1, len(items)))
    return items[0:_len]


PHONE_NUMBERS = ('08096699966', '08169567693')

MENU_NAMES = (
    'Drinks / Beverages',
    'Salads',
    'Continental',
    'Soup',
    'Starters',
    'Pastries',
    'Butchers Plates',
    'Burger and Sandwiches',
    'Main Dish',
    'Desserts',
    'Meditanian Dishes - Salads',
)

SIDE_MENUS = (
    'Choice of Dressing (for Grilled Chicken salad)',
    'Choice of Flavor',
    'Choice of size',
    'Add ons',
    'Appetizers',
    'Choice of Protein',
    'Pizza sizes',
    'Soups'
)

FOOD_LOCATIONS = (
    '6.446448,3.472094',
    '6.450741, 3.457324',
    '6.448694, 3.466079',
    '6.445197, 3.468740',
    '6.442212, 3.455436',
    '6.441871, 3.437841',
    '6.436498, 3.443334',
    '6.430698, 3.437068',
    '6.428395, 3.440845',
    '6.431465, 3.424537',
    '6.438352, 3.420309',
    '6.433784, 3.419200',
    '6.431264, 3.414761',
    '6.464497, 3.471666',
    '6.438824, 3.442659'
)


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User
        django_get_or_create = ('username',)

    first_name = lazy_attribute(lambda o: fake.first_name())
    last_name = lazy_attribute(lambda o: fake.last_name())
    username = Sequence(lambda n: '{}_{}'.format(fake.user_name(), n))
    email = lazy_attribute(lambda o: o.username + "@example.com")
    phone = choice(PHONE_NUMBERS)
    identity_verified = choice([True, False])


class AddressFactory(DjangoModelFactory):

    class Meta:
        model = Address

    user = SubFactory(UserFactory)
    city = 'Lagos'
    county = 'Lekki phase 1'
    location = '6.446448, 3.472094'
    address_1 = 'Rukayyah, Atinuke Alaka Close Lekki Lagos 23401'


class VendorFactory(DjangoModelFactory):
    class Meta:
        model = Vendor

    def _logo_img():
        images = glob.glob('./static/images/restaurant-logos/*')
        return File(open(choice(images), 'rb'))

    def _banner_img():
        images = glob.glob('./static/images/fixtures/*/*')
        return File(open(choice(images), 'rb'))

    name = lazy_attribute(lambda o: fake.company())
    address = lazy_attribute(lambda o: fake.address())
    phone = choice(PHONE_NUMBERS)
    logo = LazyFunction(_logo_img)
    banner = LazyFunction(_banner_img)

    @post_generation
    def post(obj, create, extracted, **kwargs):
        obj.location = (choice(FOOD_LOCATIONS))
        obj.tags.add(*[slugify(x) for x in get_food_tags()])
        obj.save()


class MenuFactory(DjangoModelFactory):

    class Meta:
        model = Menu

    name = lazy_attribute(lambda o: choice(MENU_NAMES))
    vendor = SubFactory(Vendor)

    @post_generation
    def post(obj, create, extracted, **kwargs):
        obj.tags.add(*[slugify(x) for x in get_food_tags()])


class ItemFactory(DjangoModelFactory):

    class Meta:
        model = Item

    menu = SubFactory(MenuFactory)
    name = lazy_attribute(lambda o: fake.catch_phrase())
    description = lazy_attribute(lambda o: fake.text(max_nb_chars=100))
    price = choice([1200, 900, 3500, 800, 400, 1400, 1650, 850])
    dietary_labels = lazy_attribute(lambda o: random_diet_labels())


class ImageFactory(DjangoModelFactory):

    class Meta:
        model = Image

    def _random_image():
        images = glob.glob('./static/images/fixtures/*/*')
        return File(open(choice(images), 'rb'))

    image = LazyFunction(_random_image)


class ItemImageFactory(DjangoModelFactory):

    class Meta:
        model = ItemImage

    image = SubFactory(ImageFactory)
    item = SubFactory(ItemFactory)


class OptionGroupFactory(DjangoModelFactory):

    class Meta:
        model = OptionGroup

    name = choice(SIDE_MENUS)
    item = SubFactory(ItemFactory)
    is_required = choice([True, False])
    multi_select = choice([True, False])


class OptionFactory(DjangoModelFactory):

    class Meta:
        model = Option

    name = lazy_attribute(lambda o: fake.catch_phrase())
    price = choice([1200, 900, 3500, 800, 400, 1400, 1650, 850])
    group = SubFactory(OptionGroupFactory)


class OrderFactory(DjangoModelFactory):

    class Meta:
        model = Order

    user = SubFactory(UserFactory)
    delivery_time = lazy_attribute(lambda o: choice(Order.get_today_delivery_schedules()))
    delivery_address = 'Lekki phase 1'
    notes = lazy_attribute(lambda o: fake.sentence())
    delivery_fee = settings.LUNCH_DELIVERY_FEE
    total_cost = choice([2300, 1200, 8000, 12000])


class OrderLineFactory(DjangoModelFactory):

    class Meta:
        model = OrderLine

    quantity = lazy_attribute(lambda o: choice(range(1, 6)))
    price = lazy_attribute(lambda o: choice([1200, 900, 3500, 800, 400, 1400, 1650, 850]))
    special_instructions = lazy_attribute(lambda o: fake.sentence())
    order = SubFactory(OrderFactory)
    item = SubFactory(ItemFactory)
