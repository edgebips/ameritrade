#!/usr/bin/env python3
"""Download transactions from Ameritrade and render them to Beancount format.

This script may contain some quirks related to how I represent transactions in
my accounts.

Tips:

- Links to transaction ids are inserted as ^td-XX. To automatically detect and
  remove previously imported transactions from a ledger, specify its filename
  with --ledger.

- If you trade options, it will be useful to group transactions by underlying
  type as they are all related. Use the --group-by-underlying option for this.

- You can disable auto-booking with --no-booking.

- Unhandled transactions will automatically raise an error. To debug when
  problems occur, you can use "-j <transaction-id>" in order to isolate
  processing to a single transaction, or "-J" to save the original JSON
  downloaded from TD.

"""
__author__ = 'Martin Blais <blais@furius.ca>'

from decimal import Decimal
from pprint import pformat
from pprint import pprint
from typing import Any, Dict, List, Optional, Tuple
import argparse
import collections
import datetime
import inspect
import logging
import re
import sys
import uuid
import pprint

from dateutil import parser

import ameritrade
from ameritrade import options
from ameritrade import utils

from beancount.core import data
from beancount.core import inventory
from beancount.core.inventory import MatchResult
from beancount.core import flags
from beancount.core.amount import Amount
from beancount.core.number import D
from beancount.core.number import ZERO
from beancount.core.number import MISSING
from beancount.core.position import Cost
from beancount.core.position import CostSpec
from beancount.parser import printer
from beancount.parser import booking
from beancount.parser.options import OPTIONS_DEFAULTS
from beancount import loader


ADD_EXTRA_METADATA = False


JSON = Any  # TODO(blais): Add proper type.p
BalanceDict = Dict[str, inventory.Inventory]


# US dollar currency.
USD = "USD"


# Standard options contract size.
CSIZE = 100


# Configuration file.
# TODO(blais): Turn this configuration into an input.
config = {
    'FILE'               : 'Assets:US:Ameritrade:Main',
    'cash_currency'      : 'USD',
    'asset_cash'         : 'Assets:US:Ameritrade:Main:Cash',
    'asset_money_market' : 'Assets:US:Ameritrade:Main:MMDA1',
    'asset_position'     : 'Assets:US:Ameritrade:Main:{symbol}',
    'option_position'    : 'Assets:US:Ameritrade:Main:Options',
    'asset_forex'        : 'Assets:US:Ameritrade:Forex',
    'fees'               : 'Expenses:Financial:Fees',
    'commission'         : 'Expenses:Financial:Commissions',
    'htb_fees'           : 'Expenses:Financial:Fees:HardToBorrow',
    'interest'           : 'Income:US:Ameritrade:Main:Interest',
    'dividend_nontax'    : 'Income:US:Ameritrade:Main:{symbol}:Dividend',
    'dividend'           : 'Income:US:Ameritrade:Main:{symbol}:Dividend',
    'adjustment'         : 'Income:US:Ameritrade:Main:Misc',
    'pnl'                : 'Income:US:Ameritrade:Main:PnL',
    'transfer'           : 'Assets:US:TD:Checking',
    'third_party'        : 'Assets:US:MSSB:Cash',
    'opening'            : 'Equity:Opening-Balances',
}


# Defaults for common quantization levels.
Q = D('0.01')
QO = D('0')
QP = D('0.0001')


# pylint: disable=invalid-name
def DF(floatnum: float, q: Decimal = Q) -> Decimal:
    """Convert a floating-point number to a quantized Decimal."""
    return D(floatnum).quantize(q)


# Dispatch table for handlers.
_DISPATCH = {}


def dispatch(txntype, description):
    """Decorator to register a handler for dispatch."""
    def deco(func):
        key = (txntype, description)
        assert key not in _DISPATCH, key
        _DISPATCH[key] = func
        return func
    return deco


def RunDispatch(txn, balances={}, commodities={}, raise_error=False, check_not_empty=False):
    """Dispatch a transaction to its handler."""
    key = (txn['type'], txn['description'])
    try:
        handler = _DISPATCH[key]
    except KeyError:
        if raise_error:
            pprint.pprint(txn)
            raise ValueError("Unknown message: {}".format(repr(key)))
        logging.error("Ignoring message for: %s", repr(key))
    else:
        # Call the handler method.
        signature = inspect.signature(handler)
        kwargs = dict()
        if 'balances' in signature.parameters:
            kwargs['balances'] = balances
        if 'commodities' in signature.parameters:
            kwargs['commodities'] = commodities
        result = handler(txn, **kwargs)

        if result and not isinstance(result, list):
            result = [result]
        if check_not_empty:
            empty_txn = PruneEmptyValues(txn)
            assert not empty_txn, pformat(empty_txn)
        return result


def PruneEmptyValues(txn):
    """Remove empty values, recursively."""
    clean_map = {}
    for key, value in txn.items():
        if isinstance(value, dict):
            value = PruneEmptyValues(value)
        if value:
            clean_map[key] = value
    return clean_map


def ParseDate(datestr: str) -> datetime.date:
    """Parse a date string."""
    return parser.parse(datestr).date()


def Posting(account, units=None, cost=None, price=None):
    """Create a posting."""
    return data.Posting(account, units, cost, price, None, None)


def GetOptionName(inst, yeartxn=None):
    """Get the encoded name of an option."""
    if 'symbol' in inst:
        return inst['symbol']
    opt = options.ParseOptionCusip(inst['cusip'], yeartxn=yeartxn)
    return options.MakeOptionSymbol(opt)


def Date(txn) -> datetime.date:
    """Fetch the date from a transaction."""
    return ParseDate(txn['transactionDate'])


def GetNetAmount(txn) -> Amount:
    """Return the net amount of a transaction."""
    return Amount(DF(txn['netAmount']), config['cash_currency'])


def GetLink(txn) -> Amount:
    """Return the net amount of a transaction."""
    return "td-{}".format(txn['transactionId'])


# Short three-letter codes for types of transactions.
_CODES = {
    'RECEIVE_AND_DELIVER'  : 'RAD',
    'TRADE'                : 'TRD',
    'WIRE_IN'              : 'WIN',
    'DIVIDEND_OR_INTEREST' : 'DOI',
    'ELECTRONIC_FUND'      : 'EFN',
    'JOURNAL'              : 'JRN',
}
def Type(txn):
    """Map a long transaction type name to a three-letter type name."""
    return _CODES[txn['type']]


def CreateCusipMap(txns):
    """Create a mapping of CUSIP to symbol."""
    cusmap = {}
    for txn in txns:
        try:
            inst = txn['transactionItem']['instrument']
            cusip = inst['cusip']
            symbol = inst['symbol']
            cusmap.setdefault(cusip, symbol)
        except KeyError:
            continue
    return cusmap


def CreateTransaction(txn, allow_fees=False) -> data.Transaction:
    """Create a transaction."""
    fileloc = data.new_metadata('<ameritrade>', 0)
    date = Date(txn)
    # TODO(blais): Fetch the settlement date.
    # if 'settlementDate' in txn:
    #     fileloc['settlementDate'] = ParseDate(txn['settlementDate'])
    narration = '({}) {}'.format(Type(txn), txn['description'])
    links = {GetLink(txn)}
    if not allow_fees:
        for _, value in txn['fees'].items():
            assert not value
    return data.Transaction(fileloc,
                            date, flags.FLAG_OKAY, None, narration,
                            data.EMPTY_SET, links, [])


# TODO(blais): Review fees aggregation here. I think we want them to separate
# accounts. You can click in TOS to view the breakdown.
def CreateFeesPostings(txn) -> List[data.Posting]:
    """Get postings for fees."""
    postings = []
    fees = txn['fees']
    commission = fees.pop('commission')
    if commission:
        postings.append(Posting(config['commission'], Amount(DF(commission), USD)))
    fees.pop('optRegFee', None)
    fees.pop('secFee', None)
    for unused_name, number in sorted(fees.items()):
        if not number:
            continue
        postings.append(Posting(config['fees'], Amount(DF(number), USD)))
    return postings


def CreateBalance(api, accountId) -> data.Balance:
    """Create a Balance directive for the account."""
    acc = api.GetAccount(accountId=accountId)
    balances = acc['securitiesAccount']['currentBalances']
    mmfund = balances['moneyMarketFund']
    shorts = balances['shortBalance']
    amt = mmfund + shorts
    fileloc = data.new_metadata('<ameritrade>', 0)
    date = datetime.date.today()
    return data.Balance(fileloc, date,
                        config['asset_cash'],
                        Amount(D(amt).quantize(Q), USD), None, None)


def CreateNote(txn, account, comment) -> data.Note:
    """Create a Note directive."""
    fileloc = data.new_metadata('<ameritrade>', 0)
    date = Date(txn)
    return data.Note(fileloc, date, account, comment)


#-------------------------------------------------------------------------------
# Dispatchers.


@dispatch('JOURNAL', 'CASH ALTERNATIVES REDEMPTION')
@dispatch('JOURNAL', 'CASH ALTERNATIVES PURCHASE')
@dispatch('RECEIVE_AND_DELIVER', 'CASH ALTERNATIVES REDEMPTION')
@dispatch('RECEIVE_AND_DELIVER', 'CASH ALTERNATIVES PURCHASE')
def DoMoneyMarketRedemptions(_):
    """Process money market transactions. These are journal entries and tranfers
    relating to the money market account and can be ignored as we treat the cash
    account and the money market account as a single account.
    """
    # Ignore.


@dispatch('RECEIVE_AND_DELIVER', 'CASH ALTERNATIVES INTEREST')
def DoMoneyMarketInterest(txn):
    """Process money market transactions. These are journal entries and tranfers
    relating to the money market account and can be ignored as we treat the cash
    account and the money market account as a single account.
    """
    entry = CreateTransaction(txn)
    amount = DF(txn['transactionItem']['amount'])
    units = Amount(amount, config['cash_currency'])
    return entry._replace(postings=[
        Posting(config['interest'], -units),
        Posting(config['asset_cash'], units),
    ])


@dispatch('WIRE_IN', 'THIRD PARTY')
@dispatch('WIRE_IN', 'WIRE INCOMING')
def DoThirdParty(txn):
    entry = CreateTransaction(txn)
    units = GetNetAmount(txn)
    return entry._replace(postings=[
        Posting(config['third_party'], -units),
        Posting(config['asset_cash'], units),
    ])


@dispatch('DIVIDEND_OR_INTEREST', 'FREE BALANCE INTEREST ADJUSTMENT')
def DoBalanceInterestAdjustment(txn):
    entry = CreateTransaction(txn)
    units = GetNetAmount(txn)
    return entry._replace(postings=[
        Posting(config['adjustment'], -units),
        Posting(config['asset_cash'], units),
    ])


@dispatch('DIVIDEND_OR_INTEREST', 'ORDINARY DIVIDEND')
@dispatch('DIVIDEND_OR_INTEREST', 'NON-TAXABLE DIVIDENDS')
@dispatch('DIVIDEND_OR_INTEREST', 'LONG TERM GAIN DISTRIBUTION')
def DoDividends(txn):
    entry = CreateTransaction(txn)
    units = GetNetAmount(txn)
    symbol = txn['transactionItem']['instrument']['symbol']
    keymap = {
        'ORDINARY DIVIDEND': 'dividend',
        'NON-TAXABLE DIVIDENDS': 'dividend_nontax',
        'LONG TERM GAIN DISTRIBUTION': 'dividend',
    }
    key = keymap[txn['description']]
    dividend_account = config[key].format(symbol=symbol)
    return entry._replace(postings=[
        Posting(dividend_account, -units),
        Posting(config['asset_cash'], units),
    ])


@dispatch('ELECTRONIC_FUND', 'CLIENT REQUESTED ELECTRONIC FUNDING RECEIPT (FUNDS NOW)')
@dispatch('ELECTRONIC_FUND', 'CLIENT REQUESTED ELECTRONIC FUNDING DISBURSEMENT (FUNDS NOW)')
def DoElectronicFunding(txn):
    entry = CreateTransaction(txn)
    units = GetNetAmount(txn)
    postings = [
        Posting(config['transfer'], -units),
        Posting(config['asset_cash'], units),
    ]
    if postings[0].units.number > 0:
        postings = list(reversed(postings))
    return entry._replace(postings=postings)


@dispatch('TRADE', 'BUY TRADE')
@dispatch('TRADE', 'SELL TRADE')
@dispatch('TRADE', 'SHORT SALE')
@dispatch('TRADE', 'CLOSE SHORT POSITION')
@dispatch('TRADE', 'TRADE CORRECTION')
@dispatch('TRADE', 'OPTION ASSIGNMENT')
@dispatch('TRADE', 'OPTION EXERCISE')
def DoTrade(txn, commodities):
    entry = CreateTransaction(txn, allow_fees=True)
    new_entries = [entry]

    # Add the common order id as metadata, to make together multi-leg options
    # orders.
    if 'orderId' in txn:
        match = re.match(r"([A-Z0-9]+)\.\d+", txn['orderId'])
        if match:
            order_id = match.group(1)
        else:
            order_id = txn['orderId']
        entry.links.add('order-{}'.format(order_id))

    # Figure out if this is a sale / clkosing transaction.
    item = txn['transactionItem']
    inst = item['instrument']
    assetType = inst.get('assetType', None)

    # It's a sale if the instruction says so. Pretty straightforward.
    is_sale = item.get('instruction', None) == 'SELL'

    # Add commodity leg.
    amount = DF(item['amount'], QO)
    if assetType in ('EQUITY', None):
        # Short sales will never have the 'CLOSING' flag but they will have a
        # 'SHORT SALE' description, which allows us to disambiguate them from
        # closing sales. Buys to close short sales will have a description of
        # 'CLOSE SHORT POSITION'.
        is_closing = txn['description'] in {'CLOSE SHORT POSITION', 'SELL TRADE'}

        symbol = inst['symbol']
        account = config['asset_position'].format(symbol=symbol)
        # TODO(blais): Re-enable this in v3 when booking code has been reviewed.
        # This triggers and error in booking, but that's how it should rendered.
        # is_closing = True

    elif assetType == 'OPTION':
        # Unfortunately, the 'CLOSING' flag isn't set consistently on the result
        # of the API (this would be very helpful if it were). It's only used
        # with options, and we only use it then.
        is_closing = item.get('positionEffect', None) == 'CLOSING'

        symbol = GetOptionName(inst, entry.date.year)
        account = config['asset_position'].format(symbol='Options')
        # Note: The contract size isn't present. If we find varying contract
        # size we could consider calling the API again to find out what it is.
        amount *= CSIZE

        # Open a new Commodity directive for that one option product.
        if not is_closing and symbol not in commodities:
            meta = data.new_metadata('<ameritrade>', 0)
            meta['name'] = inst['description']
            if ADD_EXTRA_METADATA:
                meta['assetcls'] = 'Options'     # Optional
                meta['strategy'] = 'RiskIncome'  # Optional
                if 'cusip' in inst:
                    meta['cusip'] = inst['cusip']
            commodity = data.Commodity(meta, entry.date, symbol)
            commodities[symbol] = commodity
            new_entries.insert(0, commodity)

    else:
        assert False, "Invalid asset type: {}".format(inst)

    # Create number of unitsp and price.
    units = Amount(amount, symbol)
    price = DF(item['price'], QP) if 'price' in item else None
    if is_sale:
        units = -units

    if is_closing:
        # If this is a closing trade, the price is the sales price and it needs
        # to be booked against a position. Set the price as price annotation,
        # not cost.
        cost = CostSpec(None, None, None, None, None, False)
        entry.postings.append(Posting(account, units, cost, Amount(price, USD)))
    else:
        # This is an opening transaction, so the price is the cost basis.
        cost = CostSpec(price, None, USD, entry.date, None, False)
        entry.postings.append(Posting(account, units, cost))

    # Add fees postings.
    entry.postings.extend(CreateFeesPostings(txn))

    # Cash leg.
    units = GetNetAmount(txn)
    entry.postings.append(Posting(config['asset_cash'], units))

    # Add a P/L leg if we're closing.
    if is_closing:
        entry.postings.append(Posting(config['pnl']))

    return new_entries


@dispatch('RECEIVE_AND_DELIVER', 'STOCK SPLIT')
def DoStockSplit(txn):
    entry = CreateTransaction(txn, allow_fees=True)

    item = txn['transactionItem']
    inst = item['instrument']
    assert inst['assetType'] == 'EQUITY'
    symbol = inst['symbol']
    amt = DF(item['amount'], QO)
    account = config['asset_position'].format(symbol=symbol)
    cost = CostSpec(None, None, None, None, None, False)
    entry.postings.extend([
        Posting(account, Amount(-amt, symbol), cost, None),
        Posting(account, Amount(amt * D('2'), symbol), cost, None),
        ])

    return entry


@dispatch('RECEIVE_AND_DELIVER', 'REMOVAL OF OPTION DUE TO ASSIGNMENT')
@dispatch('RECEIVE_AND_DELIVER', 'REMOVAL OF OPTION DUE TO EXERCISE')
@dispatch('RECEIVE_AND_DELIVER', 'REMOVAL OF OPTION DUE TO EXPIRATION')
def DoRemovalOfOption(txn, balances):
    entry = CreateTransaction(txn, allow_fees=True)

    item = txn['transactionItem']
    inst = item['instrument']
    assert inst['assetType'] == 'OPTION'
    symbol = GetOptionName(inst, entry.date.year)
    account = config['asset_position'].format(symbol='Options')

    # Note: The contract size isn't present. If we find varying contract
    # size we could consider calling the API again to find out what it is.
    amt = DF(item['amount'], QO)
    amt *= CSIZE

    # Find the current amount in the given account to figure out the side of the
    # position and the appropriate side to remove. {492fa5292636}
    balance = balances[account]
    try:
        pos = balance[(symbol, None)]
        sign = -1 if pos.units.number > 0 else 1
    except KeyError:
        # Could not find the position. Go short.
        sign = -1

    cost = CostSpec(None, None, None, None, None, False)
    entry.postings.extend([
        Posting(account, Amount(sign * amt, symbol), cost, Amount(ZERO, USD)),
        Posting(config['pnl']),
        ])

    return entry


@dispatch('RECEIVE_AND_DELIVER', 'INTERNAL TRANSFER BETWEEN ACCOUNTS OR ACCOUNT TYPES')
def DoInternalTransfer(txn):
    if txn['netAmount'] != 0.0:
        raise ValueError(txn)


@dispatch('RECEIVE_AND_DELIVER', 'MANDATORY - NAME CHANGE')
def DoNameChange(txn):
    entry = CreateTransaction(txn, allow_fees=True)
    return entry


@dispatch('JOURNAL', 'MANDATORY - NAME CHANGE')
def DoNameChangeJournal(txn):
    entry = CreateTransaction(txn, allow_fees=True)
    return entry


@dispatch('JOURNAL', 'MARK TO THE MARKET')
def DoMarkToTheMarket(_):
    pass


@dispatch('DIVIDEND_OR_INTEREST', 'SHORT TERM CAPITAL GAINS')
def DoCapitalGains(txn):
    entry = CreateTransaction(txn)
    inst = txn['transactionItem']['instrument']['symbol']
    entry = entry._replace(narration="{} - {}".format(entry.narration, inst))
    units = GetNetAmount(txn)
    return entry._replace(postings=[
        Posting(config['asset_cash'], units),
        Posting(config['pnl'], -units),
    ])


@dispatch('JOURNAL', 'INTRA-ACCOUNT TRANSFER')
def DoIntraAccountTransfer(txn):
    # if 'settlementDate' in txn:
    #     fileloc['settlementDate'] = ParseDate(txn['settlementDate'])
    comment = 'Intra-Account Transfer (subAccount: {}; link: ^{}; netAmount: {})'.format(
        txn['subAccount'], GetLink(txn), txn['netAmount'])
    return CreateNote(txn, config['asset_cash'], comment)


@dispatch('JOURNAL', 'MISCELLANEOUS JOURNAL ENTRY')
def DoIntraAccountTransfer(txn):
    comment = 'Miscellaneous Journal Entry (transactionId: ^{}; netAmount: {})'.format(
        GetLink(txn), txn['netAmount'])
    return CreateNote(txn, config['asset_cash'], comment)


@dispatch('JOURNAL', 'HARD TO BORROW FEE')
def DoHardToBorrow(txn):
    entry = CreateTransaction(txn)
    units = GetNetAmount(txn)
    return entry._replace(postings=[
        Posting(config['htb_fees'], units),
        Posting(config['asset_cash'], -units),
    ])


def DoNotImplemented(txn):
    logging.warning("Not implemented: %s", pformat(txn))


def MatchTrades(entries: List[data.Directive]) -> Tuple[data.Entries, BalanceDict]:
    # NOTE(blais): Eventually we ought to use the real functionality provided by
    # Beancount. Note that we could add extra data in the inventory in order to
    # keep track of the augmenting entries, and return it properly. This would
    # work and is doable in the pure Python code today.
    balances = collections.defaultdict(inventory.Inventory)
    positions = {}

    # Create new link sets in order to avoid mutating the inputs.
    entries = [
        (entry._replace(links=entry.links.copy())
         if isinstance(entry, data.Transaction)
         else entry)
        for entry in entries]

    # Process all transactions, adding links in-place.
    for entry in data.filter_txns(entries):
        for posting in entry.postings:
            if posting.cost is None:
                continue
            pos, booking = balances[posting.account].add_position(posting)
            pos_key = (posting.account, posting.units.currency)
            if booking in {MatchResult.CREATED, MatchResult.AUGMENTED}:
                positions[pos_key] = entry
            elif booking == MatchResult.REDUCED:
                opening_entry = positions[pos_key]
                link = 'trade-{}'.format(uuid.uuid4().hex[-12:])
                opening_entry.links.add(link)
                entry.links.add(link)

    return entries, balances


def GetExpiredOptionsPrices(positions: JSON,
                            balances: BalanceDict) -> List[data.Price]:
    """Produce zero prices for expired options, on the following day."""

    # Create an options positions map.
    position_map = {pos['instrument']['symbol']: pos
                    for pos in positions
                    if pos['instrument']['assetType'] == 'OPTION'}

    price_entries = []
    for currency, balance in balances.items():
        for position in balance:
            currency = position.units.currency
            if options.IsOptionSymbol(currency):
                opt = options.ParseOptionSymbol(currency)
                fileloc = data.new_metadata('<ameritrade>', 0)

                # Record for the next day (we typically run this script at night).
                date = datetime.date.today() + datetime.timedelta(days=1)

                # If the position is still currently held, find the appropriate
                # price point from the list of positions.
                try:
                    pos = position_map[currency]
                except KeyError:
                    price = ZERO
                else:
                    quantity = Decimal(pos['longQuantity'] - pos['shortQuantity'])
                    price = Decimal(pos['marketValue']) / (quantity * CSIZE)

                price_entries.append(
                    data.Price(fileloc, date, currency, Amount(price, USD)))

    return price_entries


def SortCommodityFirst(entries: List[data.Directive]) -> List[data.Directive]:
    """Keep the entries in the same order and put Commodity entries ahead of txns."""
    aug_entries = []
    for index, entry in enumerate(entries):
        if isinstance(entry, data.Transaction):
            if re.search(r"EXPIRATION", entry.narration):
                priority = 0
            else:
                priority = 2
        elif isinstance(entry, data.Commodity):
            priority = 1
        else:
            priority = 3
        aug_entries.append(((entry.date, priority, index), entry))
    aug_entries.sort()
    return [etuple[1] for etuple in aug_entries]


def GroupByUnderlying(entries: data.Entries) -> Dict[Tuple[bool, data.Currency],
                                                     data.Entries]:
    """Group entries by underlying."""

    # Group entries by underlying.
    groups = collections.defaultdict(list)
    for entry in entries:
        has_option = False
        if isinstance(entry, data.Transaction):
            # Keep just the legs with options symbols on them.
            postings_by_under = collections.defaultdict(list)
            for posting in entry.postings:
                if posting.cost is None:
                    continue
                currency = posting.units.currency
                p_symbol, is_option = options.GetUnderlying(posting.units.currency)
                has_option |= is_option
                postings_by_under[p_symbol].append(posting)

            if len(postings_by_under) >= 2:
                # Not handling transfers in this script.
                continue
            elif postings_by_under:
                symbol = next(iter(postings_by_under.keys()))
            else:
                symbol = None

        elif isinstance(entry, data.Price):
            symbol, is_option = options.GetUnderlying(entry.currency)
            has_option |= is_option

        elif isinstance(entry, data.Commodity):
            symbol, is_option = options.GetUnderlying(entry.currency)
            has_option |= is_option

        elif isinstance(entry, data.Note):
            symbol = None

        elif isinstance(entry, (data.Open, data.Balance)):
            continue

        else:
            raise NotImplementedError("Not supported: {}".format(entry))

        # Insert into relevant group.
        groups[(has_option, symbol or "")].append(entry)

    return dict(groups.items())


def RemoveDateReductions(entries: data.Entries) -> data.Entries:
    """When booking explicitly without the full previous state of the ledger,
    reductions will have their date automatically inserted by the booking code.
    In this context, where we will be processing a subset of the input (we're
    not providing the state of the ledger prior), do not do this (remove these).

    This results in transactions like this:

      2021-01-28 * "(TRD) SELL TRADE"
        Assets:US:Ameritrade:Main:FB        -15 FB {2021-01-28} @ 282.6100 USD
        Expenses:Financial:Fees            0.09 USD
        Assets:US:Ameritrade:Main:Cash  4239.06 USD

    In the future, what we'll want to do is make the booking code accept the
    prior state to book against, and we will (a) compute the state/balances from
    processing the ledger, provide that to the booking code as en entry point.

    In the meantime, we fixup the unnecessary dates, which would cause problems
    when inserted in the full ledger.
    """
    new_entries = []
    for entry in entries:
        if isinstance(entry, data.Transaction):
            new_postings = []
            fixed = False
            for posting in entry.postings:
                if (posting.cost and
                    posting.cost.number in {None, MISSING} and
                    posting.cost.date is not None):
                    posting = posting._replace(cost=posting.cost._replace(date=None))
                    fixed = True
                new_postings.append(posting)
            if fixed:
                entry = entry._replace(postings=new_postings)
        new_entries.append(entry)
    return new_entries


def main():
    argparser = argparse.ArgumentParser()
    ameritrade.add_args(argparser)

    argparser.add_argument(
        '-i', '--ignore-errors', dest='raise_error', action='store_false',
        default=True,
        help="Raise an error on unhandled messages")
    argparser.add_argument(
        '-J', '--debug-file', '--json', action='store',
        help="Debug filename where to strore al the raw JSON")
    argparser.add_argument(
        '-j', '--debug-transaction', action='store', type=int,
        help="Process a single transaction and print debugging data about it.")

    argparser.add_argument('-e', '--end-date', action='store',
                           help="Period of end date minus one year.")

    argparser.add_argument('-B', '--no-booking', dest='booking',
                           action='store_false', default=True,
                           help="Do booking to resolve lots.")

    argparser.add_argument('-l', '--ledger', action='store',
                           help=("Beancount ledger to remove already imported "
                                 "transactions (optional)."))

    argparser.add_argument('-g', '--group-by-underlying', action='store_true',
                           help=("Group the transaction output by corresponding "
                                 "underlying. This is great for options."))

    args = argparser.parse_args()

    # Open a connection and figure out the main account.
    api = ameritrade.open(ameritrade.config_from_args(args))
    accountId = utils.GetMainAccount(api)
    positions = utils.GetPositions(api, accountId)

    # Fetch transactions.
    # Note that the following arguments are also honored:
    #   endDate=datetime.date.today().isoformat())
    #   startDate='2014-01-01',
    #   endDate='2015-01-01')
    if args.end_date:
        end_date = parser.parse(args.end_date).date()
        start_date = end_date - datetime.timedelta(days=364)
        start = start_date.isoformat()
        end = end_date.isoformat()
    else:
        start = end = None
    txns = api.GetTransactions(accountId=accountId,
                               startDate=start, endDate=end)
    if isinstance(txns, dict):
        pprint(txns, sys.stderr)
        return
    txns.reverse()

    # Optionally write out the raw original content downloaded to a file.
    if args.debug_file:
        with open(args.debug, 'w') as ofile:
            ofile.write(pformat(txns))

    # Process each of the transactions.
    entries = []
    balances = collections.defaultdict(inventory.Inventory)
    commodities = {}
    for txn in txns:
        if args.debug_transaction:
            if txn['transactionId'] != args.debug_transaction:
                continue
            else:
                pprint.pprint(txn)

        # print('{:30} {}'.format(txn['type'], txn['description'])); continue
        dispatch_entries = RunDispatch(txn, balances, commodities, args.raise_error)
        if dispatch_entries:
            entries.extend(dispatch_entries)

            # Update a balance account of just the units.
            #
            # This is only here so that the options removal can figure out which
            # side is the reduction side and what sign to use on the position
            # change. Ideally the API would provide a side indication and we
            # wouldn't have to maintain any state at alll. {492fa5292636}
            for entry in data.filter_txns(dispatch_entries):
                for posting in entry.postings:
                    balance = balances[posting.account]
                    if posting.units is not None:
                        balance.add_amount(posting.units)

    # Add a final balance entry.
    balance_entry = CreateBalance(api, accountId)
    if balance_entry:
        entries.append(balance_entry)

    if args.booking:
        # Book the entries.
        entries, balance_errors = booking.book(entries, OPTIONS_DEFAULTS.copy())
        if balance_errors:
            printer.print_errors(balance_errors)

        # Remove dates on reductions when they have no prices. This is an
        # artifact of not being able to pass in prior balance state to the
        # booking code, which we will fix in v3.
        entries = RemoveDateReductions(entries)

        # Match up the trades we can in this subset of the history and pair them up
        # with a common random id.
        entries, balances = MatchTrades(entries)

        # Add zero prices for expired options for which we still have non-zero
        # positions.
        entries.extend(GetExpiredOptionsPrices(positions, balances))


    # If a Beancount ledger has been specified, open it, read it in, and remove
    # all the transactions up to the latest one with the transaction id (as a
    # link) that's present in the ledger.
    if args.ledger:
        ledger_entries, _, __ = loader.load_file(args.ledger)

        # Find the date of the last transaction in the ledger with a TD
        # transaction id, and the full set of links to remove.
        links = set()
        last_date = None
        for entry in data.filter_txns(ledger_entries):
            for link in (entry.links or {}):
                if re.match(r"td-\d{9,}", link):
                    links.add(link)
                    last_date = entry.date

        # Remove all the transactions already present in the ledger.
        #
        # Also remove all the non-transactions with a date before that of the
        # last linked one that was found. This allows us to remove Price and
        # Commodity directives. (In v3, when links are available on every
        # directive, we can just use the links.)
        entries = [entry
                   for entry in entries
                   if ((isinstance(entry, data.Transaction) and
                        not entry.links & links)
                       or
                       (not isinstance(entry, data.Transaction) and
                        entry.date >= last_date))]

    if args.group_by_underlying:
        # Group the transactions by their underlying, with org-mode separators.
        groups = GroupByUnderlying(entries)
        for (has_option, currency), group_entries in sorted(groups.items()):
            header = currency or "General"
            if has_option:
                header = "Options: {}".format(header)
            print("** {}".format(header))
            print()
            printer.print_entries(data.sorted(group_entries), file=sys.stdout)
            print()
            print()
    else:
        # Render all the entries chronologically (the default).
        sentries = SortCommodityFirst(entries)
        printer.print_entries(sentries, file=sys.stdout)


if __name__ == '__main__':
    main()
