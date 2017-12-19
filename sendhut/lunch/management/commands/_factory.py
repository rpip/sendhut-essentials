from random import choice, shuffle
import glob

from django.core.files import File
from faker import Faker
from factory import (
    DjangoModelFactory, SubFactory,
    LazyFunction, lazy_attribute, Sequence,
)

from sendhut.accounts.models import User, Address
from sendhut.lunch.models import (
    Partner, Menu, Item, OptionGroup, Option,
    Image, ItemImage, OrderItem, Order
)
from sendhut.dashboard.models import Company, Employee, Allowance


fake = Faker()


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
    ''
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


class PartnerFactory(DjangoModelFactory):

    class Meta:
        model = Partner

    name = lazy_attribute(lambda o: fake.company())
    address = lazy_attribute(lambda o: fake.address())
    location = choice(FOOD_LOCATIONS)
    phone = choice(PHONE_NUMBERS)


class MenuFactory(DjangoModelFactory):

    class Meta:
        model = Menu

    name = choice(MENU_NAMES)
    partner = SubFactory(Partner)


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

    image = SubFactory(Image)
    item = SubFactory(Item)


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


class CompanyFactory(DjangoModelFactory):

    class Meta:
        model = Company

    user = SubFactory(UserFactory)
    name = lazy_attribute(lambda o: fake.catch_phrase())
    address = SubFactory(AddressFactory)


class AllowanceFactory(DjangoModelFactory):

    class Meta:
        model = Allowance

    created_by = SubFactory(UserFactory)
    frequency = lazy_attribute(lambda o: choice(list(dict(Allowance.FREQUENCY).keys())))
    limit = lazy_attribute(lambda x: choice([0, 10000, 6000, 20000]))
    company = SubFactory(CompanyFactory)


class EmployeeFactory(DjangoModelFactory):

    class Meta:
        model = Employee

    user = SubFactory(UserFactory)
    role = lazy_attribute(lambda o: choice(list(dict(Employee.ROLES).keys())))
    company = SubFactory(CompanyFactory)
    allowance = SubFactory(AllowanceFactory)


class OrderFactory(DjangoModelFactory):

    class Meta:
        model = Order


class OrderItemFactory(DjangoModelFactory):

    class Meta:
        model = OrderItem
