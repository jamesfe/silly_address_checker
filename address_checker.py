# -*- coding: utf-8 -*-

import requests
from datetime import datetime
import re
import time

output_prefix = '10k_addresses_'


def slow_get(url):
    time.sleep(0.2)
    return requests.get(url)


def get_address_info(setup):
    """
    url = 'https://bitaps.com/api/address/{}'.format(address.decode('utf-8'))
    address_info = slow_get(url)
    if api_call.status_code != 200:
        print('bad status code: {}'.format(api_call.status_code))
    """

    address = setup[0]
    trans_url = 'https://bitaps.com/api/address/transactions/{}'.format(address)
    trans_call = slow_get(trans_url)
    if trans_call.status_code != 200:
        print('bad status code: {}'.format(trans_call.status_code))

    transactions = trans_call.json()

    trans_dates = sorted([_[0] for _ in transactions])
    most_recent_date = datetime.fromtimestamp(trans_dates[-1])
    with open('./output/{}_address_info.csv'.format(output_prefix), 'a') as outfile:
        message = '{},{},"{}"\n'.format(len(trans_dates), most_recent_date, setup[1])
        outfile.write(message)
        print(message, end='')


def read_active_addresses(fname):
    addresses = []
    with open(fname, 'r') as infile:
        for line in infile:
            match = re.match("Address: (.*) with private key (.*) has .*", line)
            if match is not None:
                addresses.append(match.groups())
    return addresses


addresses = read_active_addresses('./output/10k_passwords_active.txt')
for address in addresses:
    get_address_info(address)
