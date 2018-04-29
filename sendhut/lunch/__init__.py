default_app_config = 'sendhut.lunch.apps.LunchConfig'


class DietaryRestrictions:
    # dietary restrictions
    GLUTEN_FREE = 'gluten-free'
    DAIRY_FREE = 'dairy-free'
    VEGAN = 'vegan'
    VEGETARIAN = 'vegetarian'
    HALAL = 'halal'

    CHOICES = [
        (GLUTEN_FREE, "Gluten Free"),
        (DAIRY_FREE, "Dairy Free"),
        (VEGAN, "Vegan"),
        (VEGETARIAN, "Vegetarian"),
        (HALAL, "Halal")
    ]


class FoodCategories():
    # Food categories
    LOCAL_GEMS = 'local-gems'
    HALAL = 'halal'
    VEGETARIAN = 'vegetarian'
    DESSERTS_SWEET_TREATS = 'dessert-sweets'
    GUILTY_PLEASURES = 'guilty-pleasures'
    BAKERY = 'bakery'
    FRESH_JUICE = 'fresh-juice'
    HEALTHY_FOOD = 'healthy-food'

    CHOICES = (
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
