#!/usr/bin/env python3
"""Cancel all orders.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import argparse
import collections
import datetime
import logging
import math
import itertools
import pprint
import re
import time
from typing import Any, Optional, Tuple

import ameritrade as td
from ameritrade import utils


def CancelAllOrders(api, account_id, statuses=None):
  if statuses is None:
    statuses = utils.ACTIVE_STATUS
  orders = api.GetOrdersByPath(accountId=account_id)
  for order in orders:
    if order['status'] not in statuses:
        continue
    logging.info("Canceling: %s", order['orderId'])
    resp = api.CancelOrder(accountId=account_id, orderId=order['orderId'])
    if resp:
        raise ValueError(resp)


def main():
    """Compute various vol estimates."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    td.add_args(parser)
    args = parser.parse_args()
    config = td.config_from_args(args)
    config = config._replace(readonly=False)
    api = td.open(config)

    CancelAllOrders(api, utils.GetMainAccount(api))


if __name__ == '__main__':
    main()
