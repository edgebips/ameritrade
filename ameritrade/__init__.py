"""Bindings for the Ameritrade REST API.

Homepage: https://developer.tdameritrade.com

Usage:

    config = ameritrade.config_from_dir(config_dir=config_dir,
                                        redirect_uri='https://localhost:8444')
    api = ameritrade.open(config)
    instruments = api.SearchInstruments(symbol='Vanguard', projection='desc-search')

See schema.py for a description of all available methods.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from ameritrade import api
open = api.open
config_from_dir = api.config_from_dir

from ameritrade import scripts
add_script_args = scripts.add_args
config_from_args = scripts.config_from_args
