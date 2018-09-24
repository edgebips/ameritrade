import datetime
from decimal import Decimal
from ameritrade import options


def _O(symbol, ymd, strike_str, side):
    return options.Option(symbol, datetime.date(*ymd), Decimal(strike_str), side)

_TESTDATA = [
    ('VTI_021618C137', '0VTI..BG80137000', _O('VTI', (2018,  2, 16), Decimal('137'), 'C')),
    ('VTI_031618C140', '0VTI..CG80140000', _O('VTI', (2018,  3, 16), Decimal('140'), 'C')),
    ('QQQ_020918C158', '0QQQ..B980158000', _O('QQQ', (2018,  2,  9), Decimal('158'), 'C')),
    ('QQQ_021618C160', '0QQQ..BG80160000', _O('QQQ', (2018,  2, 16), Decimal('160'), 'C')),
    ('HDV_021618C88',  '0HDV..BG80088000', _O('HDV', (2018,  2, 16),  Decimal('88'), 'C')),
    ('VTI_021618C137', '0VTI..BG80137000', _O('VTI', (2018,  2, 16), Decimal('137'), 'C')),
    ('QQQ_021618C160', '0QQQ..BG80160000', _O('QQQ', (2018,  2, 16), Decimal('160'), 'C')),
    ('SPY_092818P270', '0SPY..US80270000', _O('SPY', (2018,  9, 28), Decimal('270'), 'P')),
    ('SPY_031519P270', '0SPY..OF90270000', _O('SPY', (2019,  3, 15), Decimal('270'), 'P')),
    ('VTI_031618C140', '0VTI..CG80140000', _O('VTI', (2018,  3, 16), Decimal('140'), 'C')),
    ('SPY_092019P270', '0SPY..UK90270000', _O('SPY', (2019,  9, 20), Decimal('270'), 'P')),
    ('SPY_081718C290', '0SPY..HH80290000', _O('SPY', (2018,  8, 17), Decimal('290'), 'C')),
    ('SPY_081718C285', '0SPY..HH80285000', _O('SPY', (2018,  8, 17), Decimal('285'), 'C')),
    ('SPY_081718P250', '0SPY..TH80250000', _O('SPY', (2018,  8, 17), Decimal('250'), 'P')),
    ('SPY_081718P250', '0SPY..TH80250000', _O('SPY', (2018,  8, 17), Decimal('250'), 'P')),
    ('SPY_081718P250', '0SPY..TH80250000', _O('SPY', (2018,  8, 17), Decimal('250'), 'P')),
    ('SPY_081718C295', '0SPY..HH80295000', _O('SPY', (2018,  8, 17), Decimal('295'), 'C')),
    ('SPY_032020P235', '0SPY..OK00235000', _O('SPY', (2020,  3, 20), Decimal('235'), 'P')),
    ('SPY_121820P240', '0SPY..XI00240000', _O('SPY', (2020, 12, 18), Decimal('240'), 'P')),
    ('SPY_090718C296', '0SPY..I780296000', _O('SPY', (2018,  9,  7), Decimal('296'), 'C')),
    ('SPY_092118C299', '0SPY..IL80299000', _O('SPY', (2018,  9, 21), Decimal('299'), 'C')),
    ('SPY_061920P260', '0SPY..RJ00260000', _O('SPY', (2020,  6, 19), Decimal('260'), 'P')),
    ('XSP_091918P290', '0XSP..UJ80290000', _O('XSP', (2018,  9, 19), Decimal('290'), 'P')),
    ('XSP_090718P290', '0XSP..U780290000', _O('XSP', (2018,  9,  7), Decimal('290'), 'P')),
]

def test_parse_option_symbol():
    for symbol, _, opt in _TESTDATA:
        assert opt == options.ParseOptionSymbol(symbol)

def test_make_option_symbol():
    for symbol, _, opt in _TESTDATA:
        assert options.MakeOptionSymbol(opt) == symbol

def test_parse_option_cusip():
    for _, cusip, opt in _TESTDATA:
        assert opt == options.ParseOptionCusip(cusip)

def test_make_option_cusip():
    for _, cusip, opt in _TESTDATA:
        assert options.MakeOptionCusip(opt) == cusip
