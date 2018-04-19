#!/usr/bin/env python

import requests
import json
import yaml
import re

# http://order.chicken-republic.com/media/js/ce56032fdeda6b3e028fd0246d477014.js


HEADERS = {'X-Requested-With': 'XMLHttpRequest'}

BASE_URL = 'http://order.chicken-republic.com/'

OPTIONS_REGEX = r'Product.Config\((.*?)\)\;'


def get_options(item_id):
    url = '{}/quickview/product/view?id={}'.format(BASE_URL, item_id)
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return {}

    data = r.json()
    opts = re.findall(r'Product.Config\((.*?)\)\;', data['content'])
    opts = json.loads(opts[0]) if opts else []
    opts = opts['attributes'].values()
    _opts = []
    for x in opts:
        opt = {
            'title': x['label'],
            'multi': False,
            'items': [
                {'name': _x['label'], 'price': float(_x['price'])} for _x in x['options']
            ]
        }
        _opts.append(opt)

    return _opts


def load_menus(data):
    results = {}
    for x in data:
        items = []
        for item in x['items']:
            del item['priceHtmlBlock']
            if item['type'] == 'configurable':
                item['options'] = get_options(item['id'])

            items.append(item)

        results[x['name']] = {'items': items}
    return results


def run():
    print("Loading menus...")
    with open('./etc/chicken-republic.json', 'r') as f:
        menus = load_menus(json.loads(f.read()))
        _data = {
            'name': 'Chicken Republic',
            'locations': [
                {'address': 'No 10 Admiralty Way, Lekki Phase 1'},
                {'address': '190 Awolowo road, Falomo, Ikoyi'},
                {'address': '271A Ajose Adeogun street'}
            ],
            'menus': menus
        }
        with open('./etc/chicken-republic.yaml', 'w') as ff:
            yaml.dump(_data, ff, allow_unicode=True, default_flow_style=False)


if __name__ == '__main__':
    run()
