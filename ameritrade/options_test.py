__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

import datetime
from decimal import Decimal as D
from ameritrade import options


def _O(symbol, ymd, strike_str, side):
    return options.Option(symbol, datetime.date(*ymd), D(strike_str), side)

_TESTDATA = [
    ('VTI_021618C137',    '0VTI..BG80137000', _O('VTI',  (2018,  2, 16), D('137'),   'C')),
    ('VTI_031618C140',    '0VTI..CG80140000', _O('VTI',  (2018,  3, 16), D('140'),   'C')),
    ('QQQ_020918C158',    '0QQQ..B980158000', _O('QQQ',  (2018,  2,  9), D('158'),   'C')),
    ('QQQ_021618C160',    '0QQQ..BG80160000', _O('QQQ',  (2018,  2, 16), D('160'),   'C')),
    ('HDV_021618C88',     '0HDV..BG80088000', _O('HDV',  (2018,  2, 16),  D('88'),   'C')),
    ('VTI_021618C137',    '0VTI..BG80137000', _O('VTI',  (2018,  2, 16), D('137'),   'C')),
    ('QQQ_021618C160',    '0QQQ..BG80160000', _O('QQQ',  (2018,  2, 16), D('160'),   'C')),
    ('SPY_092818P270',    '0SPY..US80270000', _O('SPY',  (2018,  9, 28), D('270'),   'P')),
    ('SPY_031519P270',    '0SPY..OF90270000', _O('SPY',  (2019,  3, 15), D('270'),   'P')),
    ('VTI_031618C140',    '0VTI..CG80140000', _O('VTI',  (2018,  3, 16), D('140'),   'C')),
    ('SPY_092019P270',    '0SPY..UK90270000', _O('SPY',  (2019,  9, 20), D('270'),   'P')),
    ('SPY_081718C290',    '0SPY..HH80290000', _O('SPY',  (2018,  8, 17), D('290'),   'C')),
    ('SPY_081718C285',    '0SPY..HH80285000', _O('SPY',  (2018,  8, 17), D('285'),   'C')),
    ('SPY_081718P250',    '0SPY..TH80250000', _O('SPY',  (2018,  8, 17), D('250'),   'P')),
    ('SPY_081718P250',    '0SPY..TH80250000', _O('SPY',  (2018,  8, 17), D('250'),   'P')),
    ('SPY_081718P250',    '0SPY..TH80250000', _O('SPY',  (2018,  8, 17), D('250'),   'P')),
    ('SPY_081718C295',    '0SPY..HH80295000', _O('SPY',  (2018,  8, 17), D('295'),   'C')),
    ('SPY_032020P235',    '0SPY..OK00235000', _O('SPY',  (2020,  3, 20), D('235'),   'P')),
    ('SPY_121820P240',    '0SPY..XI00240000', _O('SPY',  (2020, 12, 18), D('240'),   'P')),
    ('SPY_090718C296',    '0SPY..I780296000', _O('SPY',  (2018,  9,  7), D('296'),   'C')),
    ('SPY_092118C299',    '0SPY..IL80299000', _O('SPY',  (2018,  9, 21), D('299'),   'C')),
    ('SPY_061920P260',    '0SPY..RJ00260000', _O('SPY',  (2020,  6, 19), D('260'),   'P')),
    ('XSP_091918P290',    '0XSP..UJ80290000', _O('XSP',  (2018,  9, 19), D('290'),   'P')),
    ('XSP_090718P290',    '0XSP..U780290000', _O('XSP',  (2018,  9,  7), D('290'),   'P')),
    ('XSP_090718P290',    '0XSP..U780290000', _O('XSP',  (2018,  9,  7), D('290'),   'P')),
    ('NDXP_011321C13280', '0NDXP.AD1328000A', _O('NDXP', (2021,  1, 13), D('13280'), 'C')),
    ('RUT_011521P1940',   '0RUT..MF11940000', _O('RUT',  (2021,  1, 15), D('1940'),  'P')),
]

def test_parse_option_symbol():
    for symbol, _, opt in _TESTDATA:
        assert opt == options.ParseOptionSymbol(symbol)

def test_make_option_symbol():
    for symbol, _, opt in _TESTDATA:
        assert options.MakeOptionSymbol(opt) == symbol

def test_parse_option_cusip():
    for _, cusip, opt in _TESTDATA:
        assert opt == options.ParseOptionCusip(cusip, 2019)

def test_make_option_cusip():
    for _, cusip, opt in _TESTDATA:
        assert options.MakeOptionCusip(opt) == cusip
