from random import choice, shuffle
import glob

from django.conf import settings
from django.core.files import File
from django.utils.text import slugify
from faker import Faker
from factory import (
    DjangoModelFactory, SubFactory,
    LazyFunction, lazy_attribute, Sequence,
    post_generation, SelfAttribute
)

from sendhut.accounts.models import User, Address
from sendhut.cart.models import Cart, CartLine
from sendhut.stores.models import (
    Store, Menu, Item, OptionGroup, Option, Image, FOOD_TAGS
)
from sendhut.checkout.models import Order, OrderLine
from sendhut.grouporder.models import GroupOrder, Member


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


def create_orderlines(order, items=Item.objects.all()):
    for x in range(1, choice([2, 5])):
        OrderLine.objects.create(
            quantity=choice(range(1, 6)),
            unit_price=choice([1200, 900, 3500, 800, 400, 1400, 1650, 850]),
            special_instructions=fake.sentence(),
            order=order,
            item=choice(items)
        )


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
    # apt number or company name
    apt_number = 'Q9'
    name = lazy_attribute(lambda x: choice([None, 'Yao Adzaku']))
    phone = lazy_attribute(lambda x: choice([None, '08169567693']))
    # TODO(yao): build list of valid Lagos addresses
    address = lazy_attribute(lambda x: fake.address())
    instructions = lazy_attribute(lambda x: choice([None, fake.sentence()]))


class ImageFactory(DjangoModelFactory):

    class Meta:
        model = Image

    def _random_image():
        images = glob.glob('./static/images/fixtures/*/*')
        return File(open(choice(images), 'rb'))

    image = LazyFunction(_random_image)


class StoreFactory(DjangoModelFactory):
    class Meta:
        model = Store

    name = lazy_attribute(lambda o: fake.company())
    address = lazy_attribute(lambda o: fake.address())
    phone = choice(PHONE_NUMBERS)
    logo = SubFactory(ImageFactory)
    banner = SubFactory(ImageFactory)

    # TODO(yao): Add menu and items to store generation

    @post_generation
    def post(obj, create, extracted, **kwargs):
        obj.location = (choice(FOOD_LOCATIONS))
        obj.tags.add(*[slugify(x) for x in get_food_tags()])
        obj.save()


class MenuFactory(DjangoModelFactory):

    class Meta:
        model = Menu

    name = lazy_attribute(lambda o: choice(MENU_NAMES))
    store = SubFactory(Store)

    @post_generation
    def post(obj, create, extracted, **kwargs):
        obj.tags.add(*[slugify(x) for x in get_food_tags()])


class ItemFactory(DjangoModelFactory):

    # TODO(yao): Add variants generator

    class Meta:
        model = Item

    menu = SubFactory(MenuFactory)
    name = lazy_attribute(lambda o: fake.catch_phrase())
    description = lazy_attribute(lambda o: fake.text(max_nb_chars=100))
    price = choice([1200, 900, 3500, 800, 400, 1400, 1650, 850])
    dietary_labels = lazy_attribute(lambda o: random_diet_labels())
    image = SubFactory(ImageFactory)


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
    address = 'Lekki phase 1'
    notes = lazy_attribute(lambda o: fake.sentence())
    delivery_fee = settings.BASE_DELIVERY_FEE
    total_gross = choice([2300, 1200, 8000, 12000])


class OrderLineFactory(DjangoModelFactory):

    class Meta:
        model = OrderLine

    quantity = lazy_attribute(lambda o: choice(range(1, 6)))
    unit_price = lazy_attribute(lambda o: choice([1200, 3500, 400, 1400, 850]))
    special_instructions = lazy_attribute(lambda o: fake.sentence())
    order = SubFactory(OrderFactory)
    item = SubFactory(ItemFactory)


class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart

    user = SubFactory(UserFactory)

    class Params:
        stores = None

    @classmethod
    def create(cls, **kwargs):
        stores = kwargs.get('stores')
        cart = super().create(**kwargs)
        if stores:
            cls._add_cartlines_from_stores(cart, stores)

        return cart

    @classmethod
    def _add_cartlines_from_stores(cls, cart, stores):
        for store in stores:
            menus = [x for x in store.menus.all()]
            items = [m.items.all() for m in menus]
            items = [item for sublist in items for item in sublist]
            for _ in range(2, choice(range(3, 5))):
                CartLineFactory.create(cart=cart, item=choice(items))


class CartLineFactory(DjangoModelFactory):

    class Meta:
        model = CartLine

    cart = SubFactory(CartFactory)
    item = SubFactory(ItemFactory)
    quantity = lazy_attribute(lambda o: choice(range(1, 6)))
    # TODO(yao): Add options and note to data field
    # data


class GroupOrderFactory(DjangoModelFactory):

    class Meta:
        model = GroupOrder

    user = SubFactory(UserFactory)
    store = SubFactory(Store)
    monetary_limit = lazy_attribute(lambda o: choice([1000, 2000, 3000, None]))


class MemberFactory(DjangoModelFactory):

    class Meta:
        model = Member

    user = SubFactory(UserFactory)
    group_order = SubFactory(GroupOrderFactory)
    name = lazy_attribute(lambda o: choice([fake.name(), fake.email()]))
    cart = SubFactory(CartFactory)
