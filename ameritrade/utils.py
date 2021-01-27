"""Some utility functions built on top of the API.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"


from typing import Optional

import ameritrade as td


import pprint

def GetMainAccount(api: td.AmeritradeAPI, acctype: Optional[str]=None) -> str:
    """Returns the largest account of a particular type."""
    matching_accounts = []
    for acc in api.GetAccounts():
        for accname, accvalue in acc.items():
            if acctype and accvalue['type'] != acctype:
                continue
            liq_value = accvalue['currentBalances']['liquidationValue']
            matching_accounts.append((liq_value, accvalue['accountId']))
    if not matching_accounts:
        raise ValueError("No matching accounts.")
    return next(iter(sorted(matching_accounts, reverse=True)))[1]


ACTIVE_STATUS = frozenset({
    'AWAITING_PARENT_ORDER',
    'AWAITING_CONDITION',
    'AWAITING_MANUAL_REVIEW',
    'ACCEPTED',
    'PENDING_ACTIVATION',
    'QUEUED',
    'WORKING'})
