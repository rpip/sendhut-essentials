#!/usr/bin/env python
import json
from urlparse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://food.jumia.com.ng/"


def get_restaurants():
    # TODO(tade): support sort and user_search query params
    results = []
    print("Getting restaurants in Lagos \n")
    for page_no in range(1, 6):
        url = urljoin(BASE_URL, "restaurants/city/lagos?page={}".format(page_no))
        page = fetch(url)
        # Create a BeautifulSoup object
        soup = BeautifulSoup(page, 'html.parser')
        vendor_selectors = soup.find_all('article', class_='vendor')
        for vendor_tag in vendor_selectors:
            cuisines = vendor_tag.find(
                class_="vendor__cuisines").getText(separator=u', ')
            cuisines = [x.strip() for x in cuisines.split(',') if x.strip()]
            name = vendor_tag.find(class_="vendor__name").get_text()
            vendor = {
                'name': name.strip(),
                'cuisines': cuisines,
                'url': urljoin(BASE_URL, vendor_tag.find('a').get('href'))
            }
            details = get_vendor_details(vendor['url'])
            vendor.update(details)
            results.append(vendor)

    print("DONE \n")
    return results


def get_vendor_details(url):
    "Returns vendor menu and other info"
    # TODO(tade): include info (delivery hours, delivery fee, tagline, address)
    print("Getting vendor: {}".format(url))
    page = fetch(url)
    soup = BeautifulSoup(page, 'html.parser')
    menu_selectors = soup.find_all(class_='menu__category')
    try:
        delivery_fee = soup.find(class_='vendor-info__overview__list').find_all('dd')[0].get_text()
    except:
        delivery_fee = None

    try:
        street_address = soup.find(class_='vendor-info__address__content').find(attrs={'itemprop': 'streetAddress'}).get_text()
    except:
        street_address = None
    try:
        geo_latitude = soup.find(class_='vendor-info__address__map').find(attrs={'itemprop': 'latitude'}).get('content')
        geo_longitude = soup.find(class_='vendor-info__address__map').find(attrs={'itemprop': 'latitude'}).get('content')
        geo_address = {'latitude': geo_latitude, 'longitude': geo_longitude}
    except:
        geo_address = {'latitude': None, 'longitude': None}

    delivery_hours = get_delivery_hours(soup)
    menus = get_menus(menu_selectors)

    return {
        'menus': menus,
        'delivery_fee': delivery_fee.strip() if delivery_fee else delivery_fee,
        'delivery_hours': delivery_hours,
        # 'tagline': tagline,
        'address': street_address,
        'geo_address': geo_address
    }


def get_delivery_hours(soup):
    schedules = soup.find_all(class_="schedules__item__time")
    delivery_hours = []
    for day in schedules:
        meta = day.find_all('meta')
        _day = dict([(x.get('itemprop'), x.get('content')) for x in meta])
        delivery_hours.append(_day)

    return [x for x in delivery_hours if x]


def get_menus(menu_selectors):
    menus = []
    for menu_tag in menu_selectors:
        name = menu_tag.find(class_="menu__category__title").get_text()
        items_selectors = menu_tag.find_all(class_="menu-item ")
        description = menu_tag.find(class_='menu__category__content')
        description = description.get_text().strip() if description else ""
        menu = {'name': name.strip(), 'description': description}
        items = []
        for item_tag in items_selectors:
            title = item_tag.find(class_="menu-item__title").get_text().strip()
            description = menu_tag.find(class_="menu-item__description")
            description = description.get_text().strip() if description else ""
            amount = get_amount(item_tag)
            item = {
                'title': title,
                'description': description,
                'amount': amount
            }
            items.append(item)
        menu['items'] = items
        menus.append(menu)

    return menus


def fetch(url):
    return requests.get(url, verify=False).content


def get_amount(item_tag):
    amount = item_tag.find(class_="menu-item__variation__price").get_text().strip()
    return float(''.join(amount[1:].split('.')[0].split(',')))


def test_get_restaurants():
    results = get_restaurants()
    assert(isinstance(results, list))
    assert(len(results) > 0)
    vendor = results[0]
    assert(isinstance(vendor, dict))
    assert(set(vendor) == set(['name', 'cuisines', 'url']))


def test_get_vendor_details(url):
    pass


if __name__ == '__main__':

    restaurants = get_restaurants()
    with open('lagos-vendors.json', 'w') as f:
        json.dump(restaurants, f)
