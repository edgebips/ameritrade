"""Unit tests for Ameritrade to Beancount converter."""
__author__ = 'Martin Blais <blais@furius.ca>'

# pylint: disable=invalid-name,missing-function-docstring,too-many-lines

import unittest

import transactions

from beancount.parser.cmptest import assertEqualEntries


def test_JOURNAL__CASH_ALTERNATIVES_REDEMPTION():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'CASH ALTERNATIVES REDEMPTION',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 20678.89,
           'settlementDate': '2017-08-31',
           'subAccount': '2',
           'transactionDate': '2017-08-31T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789, 'cost': 0.0},
           'transactionSubType': 'RM',
           'type': 'JOURNAL'}
    assert not transactions.RunDispatch(txn)


def test_JOURNAL__CASH_ALTERNATIVES_PURCHASE():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'CASH ALTERNATIVES PURCHASE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': -21085.71,
           'settlementDate': '2017-09-01',
           'subAccount': '2',
           'transactionDate': '2017-09-01T09:03:39+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789, 'cost': 0.0},
           'transactionSubType': 'PM',
           'type': 'JOURNAL'}
    assert not transactions.RunDispatch(txn)


def test_RECEIVE_AND_DELIVER__CASH_ALTERNATIVES_REDEMPTION():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'CASH ALTERNATIVES REDEMPTION',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.0,
           'settlementDate': '2017-08-31',
           'subAccount': '1',
           'transactionDate': '2017-08-31T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 20678.89,
                               'cost': 0.0,
                               'instrument': {'assetType': 'CASH_EQUIVALENT',
                                              'cusip': '9ZZZFD898',
                                              'symbol': 'MMDA10',
                                              'type': 'MONEY_MARKET'}},
           'transactionSubType': 'RM',
           'type': 'RECEIVE_AND_DELIVER'}
    assert not transactions.RunDispatch(txn)


def test_RECEIVE_AND_DELIVER__CASH_ALTERNATIVES_PURCHASE():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'CASH ALTERNATIVES PURCHASE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.0,
           'settlementDate': '2017-09-01',
           'subAccount': '1',
           'transactionDate': '2017-09-01T09:04:25+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 21085.71,
                               'cost': 0.0,
                               'instrument': {'assetType': 'CASH_EQUIVALENT',
                                              'cusip': '9ZZZFD898',
                                              'symbol': 'MMDA10',
                                              'type': 'MONEY_MARKET'}},
           'transactionSubType': 'PM',
           'type': 'RECEIVE_AND_DELIVER'}
    assert not transactions.RunDispatch(txn)


def test_WIRE_IN__THIRD_PARTY():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'THIRD PARTY',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 21085.7,
           'settlementDate': '2017-08-31',
           'subAccount': '2',
           'transactionDate': '2017-08-31T16:25:02+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789, 'cost': 0.0},
           'transactionSubType': 'TP',
           'type': 'WIRE_IN'}
    assertEqualEntries("""

      2017-08-31 * "(WIN) THIRD PARTY" ^99988877766
        Assets:US:MSSB:Cash             -21085.70 USD
        Assets:US:Ameritrade:Main:Cash   21085.70 USD

    """, transactions.RunDispatch(txn))


def test_WIRE_IN__WIRE_INCOMING():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'WIRE INCOMING',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 79980.0,
           'settlementDate': '2017-01-19',
           'subAccount': '2',
           'transactionDate': '2017-01-19T17:15:05+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'cost': 0.0},
           'transactionSubType': 'WI',
           'type': 'WIRE_IN'}
    assertEqualEntries("""

      2017-01-19 * "(WIN) WIRE INCOMING" ^99988877766
        Assets:US:MSSB:Cash             -79980.00 USD
        Assets:US:Ameritrade:Main:Cash   79980.00 USD

    """, transactions.RunDispatch(txn))


def test_RECEIVE_AND_DELIVER__CASH_ALTERNATIVES_INTEREST():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'CASH ALTERNATIVES INTEREST',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.0,
           'settlementDate': '2017-08-31',
           'subAccount': '1',
           'transactionDate': '2017-09-01T03:28:34+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 1.24,
                               'cost': 0.0,
                               'instrument': {'assetType': 'CASH_EQUIVALENT',
                                              'cusip': '9ZZZFD898',
                                              'symbol': 'MMDA10',
                                              'type': 'MONEY_MARKET'}},
           'transactionSubType': 'MI',
           'type': 'RECEIVE_AND_DELIVER'}
    assertEqualEntries("""

      2017-09-01 * "(RAD) CASH ALTERNATIVES INTEREST" ^99988877766
        Income:US:Ameritrade:Main:Interest  -1.24 USD
        Assets:US:Ameritrade:Main:Cash       1.24 USD

    """, transactions.RunDispatch(txn))


def test_DIVIDEND_OR_INTEREST__FREE_BALANCE_INTEREST_ADJUSTMENT():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'FREE BALANCE INTEREST ADJUSTMENT',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.01,
           'settlementDate': '2017-08-31',
           'subAccount': '2',
           'transactionDate': '2017-09-01T03:47:28+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789, 'cost': 0.0},
           'transactionSubType': 'CA',
           'type': 'DIVIDEND_OR_INTEREST'}
    assertEqualEntries("""

      2017-09-01 * "(DOI) FREE BALANCE INTEREST ADJUSTMENT" ^99988877766
        Income:US:Ameritrade:Main:Misc  -0.01 USD
        Assets:US:Ameritrade:Main:Cash   0.01 USD

    """, transactions.RunDispatch(txn))



def test_DIVIDEND_OR_INTEREST__ORDINARY_DIVIDEND():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'ORDINARY DIVIDEND',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 110.11,
           'settlementDate': '2017-09-08',
           'subAccount': '2',
           'transactionDate': '2017-09-08T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'cost': 0.0,
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '464288323',
                                              'symbol': 'NYF'}},
           'transactionSubType': 'OD',
           'type': 'DIVIDEND_OR_INTEREST'}
    assertEqualEntries("""

      2017-09-08 * "(DOI) ORDINARY DIVIDEND" ^99988877766
        Income:US:Ameritrade:Main:NYF:Dividend  -110.11 USD
        Assets:US:Ameritrade:Main:Cash           110.11 USD

    """, transactions.RunDispatch(txn))


def test_DIVIDEND_OR_INTEREST__NON_TAXABLE_DIVIDENDS():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'NON-TAXABLE DIVIDENDS',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 112.02,
           'settlementDate': '2017-10-06',
           'subAccount': '2',
           'transactionDate': '2017-10-06T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'cost': 0.0,
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '464288323',
                                              'symbol': 'NYF'}},
           'transactionSubType': 'DE',
           'type': 'DIVIDEND_OR_INTEREST'}
    assertEqualEntries("""

      2017-10-06 * "(DOI) NON-TAXABLE DIVIDENDS" ^99988877766
        Income:US:Ameritrade:Main:NYF:Dividend  -112.02 USD
        Assets:US:Ameritrade:Main:Cash           112.02 USD

    """, transactions.RunDispatch(txn))



def test_DIVIDEND_OR_INTEREST__LONG_TERM_GAIN_DISTRIBUTION():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'LONG TERM GAIN DISTRIBUTION',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 52.89,
           'settlementDate': '2017-12-28',
           'subAccount': '2',
           'transactionDate': '2017-12-28T06:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'cost': 0.0,
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '464288323',
                                              'symbol': 'NYF'}},
           'transactionSubType': 'DG',
           'type': 'DIVIDEND_OR_INTEREST'}
    assertEqualEntries("""

      2017-12-28 * "(DOI) LONG TERM GAIN DISTRIBUTION" ^99988877766
        Income:US:Ameritrade:Main:NYF:Dividend  -52.89 USD
        Assets:US:Ameritrade:Main:Cash           52.89 USD

    """, transactions.RunDispatch(txn))


def test_ELECTRONIC_FUND__CLIENT_REQUESTED_ELECTRONIC_FUNDING_RECEIPT_FUNDS_NOW():
    txn = {'achStatus': 'Approved',
           'cashBalanceEffectFlag': True,
           'clearingReferenceNumber': '70330047',
           'description': 'CLIENT REQUESTED ELECTRONIC FUNDING RECEIPT (FUNDS NOW)',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 20000.0,
           'settlementDate': '2017-10-11',
           'subAccount': '2',
           'transactionDate': '2017-10-10T23:39:41+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789, 'cost': 0.0},
           'transactionSubType': 'FI',
           'type': 'ELECTRONIC_FUND'}
    assertEqualEntries("""

      2017-10-10 * "(EFN) CLIENT REQUESTED ELECTRONIC FUNDING RECEIPT (FUNDS NOW)" ^99988877766
        Assets:US:TD:Checking           -20000.00 USD
        Assets:US:Ameritrade:Main:Cash   20000.00 USD

    """, transactions.RunDispatch(txn))


def test_ELECTRONIC_FUND__CLIENT_REQUESTED_ELECTRONIC_FUNDING_DISBURSEMENT_FUNDS_NOW():
    txn = {'achStatus': 'Approved',
           'cashBalanceEffectFlag': True,
           'clearingReferenceNumber': '79493016',
           'description': 'CLIENT REQUESTED ELECTRONIC FUNDING DISBURSEMENT (FUNDS NOW)',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': -4700.0,
           'settlementDate': '2018-07-24',
           'subAccount': '2',
           'transactionDate': '2018-07-23T09:07:13+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789, 'cost': 0.0},
           'transactionSubType': 'FO',
           'type': 'ELECTRONIC_FUND'}
    assertEqualEntries("""

      2018-07-23 * "(EFN) CLIENT REQUESTED ELECTRONIC FUNDING DISBURSEMENT (FUNDS NOW)" ^99988877766
        Assets:US:TD:Checking            4700.00 USD
        Assets:US:Ameritrade:Main:Cash  -4700.00 USD

    """, transactions.RunDispatch(txn))


def test_TRADE__BUY_TRADE__EQUITY():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'BUY TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 6.95,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': -5585.45,
           'orderDate': '2017-12-08T17:55:47+0000',
           'orderId': 'T1646318287',
           'settlementDate': '2017-12-12',
           'subAccount': '2',
           'transactionDate': '2017-12-08T17:55:47+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 100.0,
                               'cost': -5578.5,
                               'instruction': 'BUY',
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '464288323',
                                              'symbol': 'NYF'},
                               'price': 55.785},
           'transactionSubType': 'BY',
           'type': 'TRADE'}
    assertEqualEntries("""

      2017-12-08 * "(TRD) BUY TRADE" ^99988877766
        Assets:US:Ameritrade:Main:NYF        100 NYF {55.7850 USD}
        Expenses:Financial:Commissions      6.95 USD
        Assets:US:Ameritrade:Main:Cash  -5585.45 USD

    """, transactions.RunDispatch(txn))

    txn = {'cashBalanceEffectFlag': True,
           'description': 'BUY TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 4.95,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': -14619.75,
           'orderDate': '2018-08-30T14:50:25+0000',
           'orderId': 'T1893895604',
           'settlementDate': '2018-09-04',
           'subAccount': '2',
           'transactionDate': '2018-08-30T14:50:26+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 500.0,
                               'cost': -14614.8,
                               'instruction': 'BUY',
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '37954Y814',
                                              'symbol': 'FINX'},
                               'price': 29.2296},
           'transactionSubType': 'BY',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-08-30 * "(TRD) BUY TRADE" ^99988877766
        Assets:US:Ameritrade:Main:FINX        500 FINX {29.2296 USD, 2018-08-30}
        Expenses:Financial:Commissions       4.95 USD
        Assets:US:Ameritrade:Main:Cash  -14619.75 USD

    """, transactions.RunDispatch(txn))


def test_TRADE__SELL_TRADE__EQUITY():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'SELL TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 6.95,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.73,
                    'secFee': 0.73},
           'netAmount': 31696.17,
           'orderDate': '2017-07-05T17:23:22+0000',
           'orderId': 'T1527984822',
           'settlementDate': '2017-07-10',
           'subAccount': '2',
           'transactionDate': '2017-07-05T17:23:22+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 94.0,
                               'cost': 31703.85,
                               'instruction': 'SELL',
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '88160R101',
                                              'symbol': 'TSLA'},
                               'price': 337.275},
           'transactionSubType': 'SL',
           'type': 'TRADE'}
    assertEqualEntries("""

      2017-07-05 * "(TRD) SELL TRADE" ^99988877766
        Assets:US:Ameritrade:Main:TSLA       -94 TSLA {} @ 337.2750 USD
        Expenses:Financial:Commissions      6.95 USD
        Expenses:Financial:Fees             0.73 USD
        Assets:US:Ameritrade:Main:Cash  31696.17 USD
        Income:US:Ameritrade:Main:PnL

    """, transactions.RunDispatch(txn), allow_incomplete=True)

    txn = {'cashBalanceEffectFlag': True,
           'description': 'SELL TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.4,
                    'secFee': 0.4},
           'netAmount': 18179.6,
           'orderDate': '2016-12-28T20:08:56+0000',
           'orderId': 'T1392438833',
           'settlementDate': '2017-01-03',
           'subAccount': '2',
           'transactionDate': '2016-12-29T02:08:56+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 500.0,
                               'cost': 18180.0,
                               'instruction': 'SELL',
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '921943858',
                                              'symbol': 'VEA'},
                               'price': 36.36},
           'transactionSubType': 'SL',
           'type': 'TRADE'}
    assertEqualEntries("""

      2016-12-29 * "(TRD) SELL TRADE" ^99988877766
        Assets:US:Ameritrade:Main:VEA       -500 VEA {} @ 36.3600 USD
        Expenses:Financial:Fees             0.40 USD
        Assets:US:Ameritrade:Main:Cash  18179.60 USD
        Income:US:Ameritrade:Main:PnL

    """, transactions.RunDispatch(txn), allow_incomplete=True)


def test_TRADE__BUY_TRADE__OPTION__OPENING():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'BUY TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 7.95,
                    'optRegFee': 0.08,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.08,
                    'secFee': 0.0},
           'netAmount': -584.03,
           'orderDate': '2018-08-30T14:22:53+0000',
           'orderId': 'T1893801618',
           'settlementDate': '2018-08-31',
           'subAccount': '2',
           'transactionDate': '2018-08-30T14:33:55+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 6.0,
                               'cost': -576.0,
                               'instruction': 'BUY',
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0XSP..U780290000',
                                              'description': 'XSP Sep 7 2018 290.0 Put',
                                              'optionExpirationDate': '2018-09-07T05:00:00+0000',
                                              'putCall': 'PUT',
                                              'symbol': 'XSP_090718P290',
                                              'underlyingSymbol': 'XSP'},
                               'positionEffect': 'OPENING',
                               'price': 0.96},
           'transactionSubType': 'BY',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-08-30 * "(TRD) BUY TRADE" ^99988877766
        Assets:US:Ameritrade:Main:Options      600 XSP180907P290 {0.9600 USD}
        Expenses:Financial:Commissions        7.95 USD
        Expenses:Financial:Fees               0.08 USD
        Assets:US:Ameritrade:Main:Cash     -584.03 USD

    """, transactions.RunDispatch(txn))

    txn = {'cashBalanceEffectFlag': True,
           'description': 'BUY TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 9.95,
                    'optRegFee': 0.14,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.14,
                    'secFee': 0.0},
           'netAmount': -12470.09,
           'orderDate': '2018-08-28T19:20:04+0000',
           'orderId': 'T1891785119',
           'settlementDate': '2018-08-29',
           'subAccount': '2',
           'transactionDate': '2018-08-28T19:37:09+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 10.0,
                               'cost': -12460.0,
                               'instruction': 'BUY',
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0SPY..RJ00260000',
                                              'description': 'SPY Jun 19 2020 260.0 Put',
                                              'optionExpirationDate': '2020-06-19T05:00:00+0000',
                                              'putCall': 'PUT',
                                              'symbol': 'SPY_061920P260',
                                              'underlyingSymbol': 'SPY'},
                               'positionEffect': 'OPENING',
                               'price': 12.46},
           'transactionSubType': 'BY',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-08-28 * "(TRD) BUY TRADE" ^99988877766
        Assets:US:Ameritrade:Main:Options       1000 SPY200619P260 {12.4600 USD}
        Expenses:Financial:Commissions          9.95 USD
        Expenses:Financial:Fees                 0.14 USD
        Assets:US:Ameritrade:Main:Cash     -12470.09 USD

    """, transactions.RunDispatch(txn))


def test_TRADE__BUY_TRADE__OPTION__CLOSING():
    pass  # No example of this yet.


def test_TRADE__SELL_TRADE__OPTION__OPENING():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'SELL TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 9.95,
                    'optRegFee': 0.14,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.16,
                    'secFee': 0.0},
           'netAmount': 219.89,
           'orderDate': '2018-08-27T14:11:22+0000',
           'orderId': 'T1889893556',
           'settlementDate': '2018-08-28',
           'subAccount': '2',
           'transactionDate': '2018-08-27T14:11:22+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 10.0,
                               'cost': 230.0,
                               'instruction': 'SELL',
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0SPY..IL80299000',
                                              'description': (
                                                  'SPY Sep 21 2018 299.0 Call'),
                                              'optionExpirationDate': (
                                                  '2018-09-21T05:00:00+0000'),
                                              'putCall': 'CALL',
                                              'symbol': 'SPY_092118C299',
                                              'underlyingSymbol': 'SPY'},
                               'positionEffect': 'OPENING',
                               'price': 0.23},
           'transactionSubType': 'SL',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-08-27 * "(TRD) SELL TRADE" ^99988877766
        Expenses:Financial:Commissions       9.95 USD
        Expenses:Financial:Fees              0.16 USD
        Assets:US:Ameritrade:Main:Options   -1000 SPY180921C299 {0.2300 USD}
        Assets:US:Ameritrade:Main:Cash     219.89 USD

    """, transactions.RunDispatch(txn))

    txn = {'cashBalanceEffectFlag': True,
           'description': 'SELL TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 18.2,
                    'optRegFee': 0.25,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.3,
                    'secFee': 0.02},
           'netAmount': 1406.5,
           'orderDate': '2018-07-17T15:48:00+0000',
           'orderId': 'T1852183685',
           'settlementDate': '2018-07-18',
           'subAccount': '2',
           'transactionDate': '2018-07-17T15:55:26+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 15.0,
                               'cost': 1425.0,
                               'instruction': 'SELL',
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0SPY..HH80285000',
                                              'description': 'SPY Aug 17 2018 285.0 Call',
                                              'optionExpirationDate': '2018-08-17T05:00:00+0000',
                                              'putCall': 'CALL',
                                              'symbol': 'SPY_081718C285',
                                              'underlyingSymbol': 'SPY'},
                               'positionEffect': 'OPENING',
                               'price': 0.95},
           'transactionSubType': 'SL',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-07-17 * "(TRD) SELL TRADE" ^99988877766
        Assets:US:Ameritrade:Main:Options    -1500 SPY180817C285 {0.9500 USD}
        Expenses:Financial:Commissions       18.20 USD
        Expenses:Financial:Fees               0.30 USD
        Assets:US:Ameritrade:Main:Cash     1406.50 USD

    """, transactions.RunDispatch(txn))


def test_TRADE__SELL_TRADE__OPTION__CLOSING():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'SELL TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 44.45,
                    'optRegFee': 0.83,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.95,
                    'secFee': 0.02},
           'netAmount': 1154.6,
           'orderDate': '2018-07-23T15:01:33+0000',
           'orderId': 'T1857189566',
           'settlementDate': '2018-07-24',
           'subAccount': '2',
           'transactionDate': '2018-07-23T15:01:34+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 50.0,
                               'cost': 1200.0,
                               'instruction': 'SELL',
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0SPY..TH80250000',
                                              'description': 'SPY Aug 17 2018 250.0 Put',
                                              'optionExpirationDate': '2018-08-17T05:00:00+0000',
                                              'putCall': 'PUT',
                                              'symbol': 'SPY_081718P250',
                                              'underlyingSymbol': 'SPY'},
                               'positionEffect': 'CLOSING',
                               'price': 0.24},
           'transactionSubType': 'SL',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-07-23 * "(TRD) SELL TRADE" ^99988877766
        Assets:US:Ameritrade:Main:Options    -5000 SPY180817P250 {} @ 0.2400 USD
        Expenses:Financial:Commissions       44.45 USD
        Expenses:Financial:Fees               0.95 USD
        Assets:US:Ameritrade:Main:Cash     1154.60 USD
        Income:US:Ameritrade:Main:PnL

    """, transactions.RunDispatch(txn), allow_incomplete=True)

    txn = {'cashBalanceEffectFlag': True,
           'description': 'SELL TRADE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 14.45,
                    'optRegFee': 0.17,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.25,
                    'secFee': 0.08},
           'netAmount': 3335.3,
           'orderDate': '2018-02-16T19:38:30+0000',
           'orderId': 'T1711089300',
           'settlementDate': '2018-02-20',
           'subAccount': '2',
           'transactionDate': '2018-02-16T19:39:33+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 10.0,
                               'cost': 3350.0,
                               'instruction': 'SELL',
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0VTI..BG80137000',
                                              'description': 'VTI Feb 16 2018 137.0 Call',
                                              'optionExpirationDate': '2018-02-16T06:00:00+0000',
                                              'putCall': 'CALL',
                                              'symbol': 'VTI_021618C137',
                                              'underlyingSymbol': 'VTI'},
                               'positionEffect': 'CLOSING',
                               'price': 3.35},
           'transactionSubType': 'SL',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-02-16 * "(TRD) SELL TRADE" ^99988877766
        Assets:US:Ameritrade:Main:Options    -1000 VTI180216C137 {} @ 3.3500 USD
        Expenses:Financial:Commissions       14.45 USD
        Expenses:Financial:Fees               0.25 USD
        Assets:US:Ameritrade:Main:Cash     3335.30 USD
        Income:US:Ameritrade:Main:PnL

    """, transactions.RunDispatch(txn), allow_incomplete=True)


def test_TRADE__TRADE_CORRECTION():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'TRADE CORRECTION',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 19.99,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 5.74,
                    'secFee': 5.56},
           'netAmount': 427474.27,
           'settlementDate': '2018-08-21',
           'subAccount': '2',
           'transactionDate': '2018-08-20T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 1500.0,
                               'cost': 427500.0,
                               'instruction': 'SELL',
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '78462F103',
                                              'symbol': 'SPY'},
                               'price': 285.0},
           'transactionSubType': 'TC',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-08-20 * "(TRD) TRADE CORRECTION" ^99988877766
        Assets:US:Ameritrade:Main:SPY       -1500 SPY {285.0000 USD, 2018-08-20}
        Expenses:Financial:Commissions      19.99 USD
        Expenses:Financial:Fees              5.74 USD
        Assets:US:Ameritrade:Main:Cash  427474.27 USD

    """, transactions.RunDispatch(txn))


def test_TRADE__OPTION_ASSIGNMENT():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'OPTION ASSIGNMENT',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 19.99,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 5.74,
                    'secFee': 5.56},
           'netAmount': 427474.27,
           'settlementDate': '2018-08-21',
           'subAccount': '4',
           'transactionDate': '2018-08-20T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 1500.0,
                               'cost': 427500.0,
                               'instruction': 'SELL',
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '78462F103',
                                              'symbol': 'SPY'},
                               'price': 285.0},
           'transactionSubType': 'OA',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-08-20 * "(TRD) OPTION ASSIGNMENT" ^99988877766
        Assets:US:Ameritrade:Main:SPY       -1500 SPY {285.0000 USD, 2018-08-20}
        Expenses:Financial:Commissions      19.99 USD
        Expenses:Financial:Fees              5.74 USD
        Assets:US:Ameritrade:Main:Cash  427474.27 USD

    """, transactions.RunDispatch(txn))


def test_TRADE__CLOSE_SHORT_POSITION():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'CLOSE SHORT POSITION',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': -378391.0,
           'orderDate': '2018-08-30T14:26:12+0000',
           'orderId': 'T1893812562',
           'settlementDate': '2018-09-04',
           'subAccount': '4',
           'transactionDate': '2018-08-30T14:26:12+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 1300.0,
                               'cost': -378391.0,
                               'instruction': 'BUY',
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '78462F103',
                                              'symbol': 'SPY'},
                               'price': 291.07},
           'transactionSubType': 'CS',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-08-30 * "(TRD) CLOSE SHORT POSITION" ^99988877766
        Assets:US:Ameritrade:Main:SPY         1300 SPY {} @ 291.0700 USD
        Assets:US:Ameritrade:Main:Cash  -378391.00 USD
        Income:US:Ameritrade:Main:PnL

    """, transactions.RunDispatch(txn), allow_incomplete=True)


def test_RECEIVE_AND_DELIVER__STOCK_SPLIT():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'STOCK SPLIT',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.0,
           'settlementDate': '2017-10-17',
           'subAccount': '2',
           'transactionDate': '2017-10-18T00:26:12+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 500.0,
                               'cost': 0.0,
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '464288323',
                                              'symbol': 'NYF'}},
           'transactionSubType': 'SP',
           'type': 'RECEIVE_AND_DELIVER'}
    assertEqualEntries("""

      2017-10-18 * "(RAD) STOCK SPLIT" ^99988877766
        Assets:US:Ameritrade:Main:NYF         -500 NYF {}
        Assets:US:Ameritrade:Main:NYF         1000 NYF {}

    """, transactions.RunDispatch(txn), allow_incomplete=True)



def test_RECEIVE_AND_DELIVER__REMOVAL_OF_OPTION_DUE_TO_EXPIRATION():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'REMOVAL OF OPTION DUE TO EXPIRATION',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.0,
           'settlementDate': '2018-02-12',
           'subAccount': '2',
           'transactionDate': '2018-02-12T06:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 10.0,
                               'cost': 0.0,
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0QQQ..B980158000',
                                              'description': 'QQQ Feb 9 2018 158.0 Call',
                                              'optionExpirationDate': '2018-02-09T06:00:00+0000',
                                              'putCall': 'CALL',
                                              'symbol': 'QQQ_020918C158',
                                              'underlyingSymbol': 'QQQ'}},
           'transactionSubType': 'OX',
           'type': 'RECEIVE_AND_DELIVER'}
    assertEqualEntries("""

      2018-02-12 * "(RAD) REMOVAL OF OPTION DUE TO EXPIRATION" ^99988877766
        Assets:US:Ameritrade:Main:Options  -1000 QQQ180209C158 {} @ 0 USD
        Income:US:Ameritrade:Main:PnL

    """, transactions.RunDispatch(txn), allow_incomplete=True)


def test_RECEIVE_AND_DELIVER__REMOVAL_OF_OPTION_DUE_TO_EXPIRATION__negative():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'REMOVAL OF OPTION DUE TO EXPIRATION',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.0,
           'settlementDate': '2018-09-20',
           'subAccount': '2',
           'transactionDate': '2018-09-20T06:14:31+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 10.0,
                               'cost': 0.0,
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0XSP..UJ80275000',
                                              'optionExpirationDate': (
                                                  '2018-09-19T05:00:00+0000')}},
           'transactionSubType': 'OX',
           'type': 'RECEIVE_AND_DELIVER'}
    # TODO(blais): The current response does not allow us to distinguish between
    # closing long and short positions.
    assertEqualEntries("""

      2018-09-20 * "(RAD) REMOVAL OF OPTION DUE TO EXPIRATION" ^99988877766
        Assets:US:Ameritrade:Main:Options   -1000 XSP180919P275 {} @ 0 USD
        Income:US:Ameritrade:Main:PnL

    """, transactions.RunDispatch(txn), allow_incomplete=True)


def test_RECEIVE_AND_DELIVER__REMOVAL_OF_OPTION_DUE_TO_ASSIGNMENT():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'REMOVAL OF OPTION DUE TO ASSIGNMENT',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.0,
           'settlementDate': '2018-08-20',
           'subAccount': '2',
           'transactionDate': '2018-08-20T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 15.0,
                               'cost': 0.0,
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0SPY..HH80285000',
                                              'optionExpirationDate': '2018-08-17T05:00:00+0000'}},
           'transactionSubType': 'OA',
           'type': 'RECEIVE_AND_DELIVER'}
    assertEqualEntries("""

      2018-08-20 * "(RAD) REMOVAL OF OPTION DUE TO ASSIGNMENT" ^99988877766
        Assets:US:Ameritrade:Main:Options  -1500 SPY180817C285 {} @ 0 USD
        Income:US:Ameritrade:Main:PnL

    """, transactions.RunDispatch(txn), allow_incomplete=True)



def test_RECEIVE_AND_DELIVER__REMOVAL_OF_OPTION_DUE_TO_EXERCISE():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'REMOVAL OF OPTION DUE TO EXERCISE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.0,
           'settlementDate': '2018-09-10',
           'subAccount': '2',
           'transactionDate': '2018-09-10T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 6.0,
                               'cost': 0.0,
                               'instrument': {'assetType': 'OPTION',
                                              'cusip': '0XSP..U780290000',
                                              'optionExpirationDate': '2018-09-07T05:00:00+0000'}},
           'transactionSubType': 'OE',
           'type': 'RECEIVE_AND_DELIVER'}
    assertEqualEntries("""

      2018-09-10 * "(RAD) REMOVAL OF OPTION DUE TO EXERCISE" ^99988877766
        Assets:US:Ameritrade:Main:Options  -600 XSP180907P290 {} @ 0 USD
        Income:US:Ameritrade:Main:PnL

    """, transactions.RunDispatch(txn), allow_incomplete=True)


def test_TRADE__OPTION_EXERCISE():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'OPTION EXERCISE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 19.99,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 173980.01,
           'settlementDate': '2018-09-10',
           'subAccount': '2',
           'transactionDate': '2018-09-10T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 600.0,
                               'cost': 174000.0,
                               'instruction': 'SELL',
                               'instrument': {'cusip': '12505Q107', 'symbol': 'XSP'},
                               'price': 290.0},
           'transactionSubType': 'OE',
           'type': 'TRADE'}
    assertEqualEntries("""

      2018-09-10 * "(TRD) OPTION EXERCISE" ^99988877766
        Assets:US:Ameritrade:Main:XSP           -600 XSP {290.0000 USD}
        Expenses:Financial:Commissions         19.99 USD
        Assets:US:Ameritrade:Main:Cash     173980.01 USD

    """, transactions.RunDispatch(txn))



def test_RECEIVE_AND_DELIVER__MANDATORY__NAME_CHANGE():
    txn = {'cashBalanceEffectFlag': True,
           'description': 'MANDATORY - NAME CHANGE',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': 0.0,
           'settlementDate': '2018-06-04',
           'subAccount': '2',
           'transactionDate': '2018-06-04T05:00:01+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789,
                               'amount': 1430.0,
                               'cost': 0.0,
                               'instrument': {'assetType': 'EQUITY',
                                              'cusip': '73935A104'}},
           'transactionSubType': 'NC',
           'type': 'RECEIVE_AND_DELIVER'}
    assertEqualEntries("""

      2018-06-04 * "(RAD) MANDATORY - NAME CHANGE" ^99988877766

    """, transactions.RunDispatch(txn), allow_incomplete=True)


def test_JOURNAL__MARK_TO_THE_MARKET():
    txn = {'cashBalanceEffectFlag': False,
           'description': 'MARK TO THE MARKET',
           'fees': {'additionalFee': 0.0,
                    'cdscFee': 0.0,
                    'commission': 0.0,
                    'optRegFee': 0.0,
                    'otherCharges': 0.0,
                    'rFee': 0.0,
                    'regFee': 0.0,
                    'secFee': 0.0},
           'netAmount': -15.0,
           'settlementDate': '2018-08-31',
           'subAccount': '2',
           'transactionDate': '2018-09-01T03:58:42+0000',
           'transactionId': 99988877766,
           'transactionItem': {'accountId': 123456789, 'cost': 0.0},
           'transactionSubType': 'MK',
           'type': 'JOURNAL'}
    assert transactions.RunDispatch(txn) is None


if __name__ == '__main__':
    unittest.main()
