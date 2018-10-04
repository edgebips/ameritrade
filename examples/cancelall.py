#!/usr/bin/env python3
"""Cancel all working orders.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import argparse

import ameritrade


def order_str(order):
    price = order['price']
    legstrs = []
    for leg in order['orderLegCollection']:
        instruction = leg['instruction']
        quantity = leg['quantity']
        symbol = leg['instrument']['symbol']
        legstrs.append(' '.join(map(str, [instruction, quantity, symbol])))
    return '{}: {} @ {}'.format(order['orderId'], '; '.join(legstrs), price)


def keep(mapping, keepkeys):
    filtmap = {key: value
               for key, value in mapping.items()
               if key in keepkeys}
    assert set(keepkeys) == set(filtmap.keys())
    return filtmap


def main():
    """Cancel all orders."""
    parser = argparse.ArgumentParser(description=__doc__.strip())
    ameritrade.add_script_args(parser)
    args = parser.parse_args()
    config = ameritrade.config_from_args(args, readonly=False)
    api = ameritrade.open(config)

    orders = api.GetOrdersByQuery()
    cancel_orders = []
    for order in orders:
        if order['status'] != 'QUEUED':
            continue
        cancel_orders.append(order)
        print(order_str(order))
    print("Cancel all orders [y/n]?")
    response = input()
    if response != 'y':
        print("Exiting without canceling.")
        return
    for order in cancel_orders:
        print("Canceling order {}".format(order['orderId']))
        status = api.CancelOrder(**keep(order, {'accountId', 'orderId'}))
        pprint.pprint(status)


if __name__ == '__main__':
    main()
