"""Some utility functions built on top of the API.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"


from typing import Any, Dict, Optional, Union

import ameritrade as td


JSON = Dict[str, Union[str, float, int, 'JSON']]


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


def GetPositions(api: td.AmeritradeAPI, account_id: str) -> Any:
    """Fetch the account if of the main account. Return JSON."""
    account = api.GetAccount(accountId=account_id, fields='positions')
    acc = next(iter(account.items()))[1]
    return acc['positions']


ACTIVE_STATUS = frozenset({
    'AWAITING_PARENT_ORDER',
    'AWAITING_CONDITION',
    'AWAITING_MANUAL_REVIEW',
    'ACCEPTED',
    'PENDING_ACTIVATION',
    'QUEUED',
    'WORKING'})


def IsOrderActive(order: JSON) -> bool:
    """Predicate for when an order is active."""
    if 'status' in order:
        if order['status'] in ACTIVE_STATUS:
            return True
    if 'childOrderStrategies' in order:
        if any(child['status'] in ACTIVE_STATUS
               for child in order['childOrderStrategies']):
            return True
    return False
