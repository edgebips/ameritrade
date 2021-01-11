"""Transaction list schema."""


TRANSACTION_SCHEMA = {
    "type": ['TRADE',
             'RECEIVE_AND_DELIVER',
             'DIVIDEND_OR_INTEREST',
             'ACH_RECEIPT',
             'ACH_DISBURSEMENT',
             'CASH_RECEIPT',
             'CASH_DISBURSEMENT',
             'ELECTRONIC_FUND',
             'WIRE_OUT',
             'WIRE_IN',
             'JOURNAL',
             'MEMORANDUM',
             'MARGIN_CALL',
             'MONEY_MARKET',
             'SMA_ADJUSTMENT'],
    "clearingReferenceNumber": "string",
    "subAccount": "string",
    "settlementDate": "string",
    "orderId": "string",
    "sma": 0,
    "requirementReallocationAmount": 0,
    "dayTradeBuyingPowerEffect": 0,
    "netAmount": 0,
    "transactionDate": "string",
    "orderDate": "string",
    "transactionSubType": "string",
    "transactionId": 0,  # Always present.
    "cashBalanceEffectFlag": False,
    "description": "string",
    "achStatus": ['Approved', 'Rejected', 'Cancel', 'Error'],
    "accruedInterest": 0,
    "fees": "object",
    "transactionItem": {
        "accountId": 0,  # Always present.
        "amount": 0,
        "price": 0,
        "cost": 0,
        "parentOrderKey": 0,
        "parentChildIndicator": "string",
        "instruction": "string",
        "positionEffect": "string",
        "instrument": {
            "symbol": "string",
            "underlyingSymbol": "string",
            "optionExpirationDate": "string",
            "optionStrikePrice": 0,
            "putCall": "string",
            "cusip": "string",
            "description": "string",
            "assetType": "string",
            "bondMaturityDate": "string",
            "bondInterestRate": 0
        }
    }
}


SCHEMA_TYPES = {
    'DIVIDEND_OR_INTEREST': {
        'FREE BALANCE INTEREST ADJUSTMENT',
        'LONG TERM GAIN DISTRIBUTION',
        'NON-TAXABLE DIVIDENDS',
        'ORDINARY DIVIDEND'},
    'ELECTRONIC_FUND': {
        'CLIENT REQUESTED ELECTRONIC FUNDING '
        'DISBURSEMENT (FUNDS NOW)',
        'CLIENT REQUESTED ELECTRONIC FUNDING RECEIPT '
        '(FUNDS NOW)'},
    'JOURNAL': {
        'MARK TO THE MARKET',
        'CASH ALTERNATIVES PURCHASE',
        'CASH ALTERNATIVES REDEMPTION'},
    'RECEIVE_AND_DELIVER': {
        'MANDATORY - NAME CHANGE',
        'CASH ALTERNATIVES INTEREST',
        'CASH ALTERNATIVES PURCHASE',
        'CASH ALTERNATIVES REDEMPTION',
        'REMOVAL OF OPTION DUE TO ASSIGNMENT',
        'REMOVAL OF OPTION DUE TO EXERCISE',
        'REMOVAL OF OPTION DUE TO EXPIRATION',
        'STOCK SPLIT',
        'INTERNAL TRANSFER BETWEEN ACCOUNTS OR ACCOUNT TYPES'},
    'TRADE': {
        'BUY TRADE',
        'OPTION ASSIGNMENT',
        'SELL TRADE',
        'TRADE CORRECTION'},
    'WIRE_IN': {
        'THIRD PARTY'}
}
