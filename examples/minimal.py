#!/usr/bin/env python3
"""Absolute minimal example client program.

Set the following two environment variables to configure this:

  AMERITRADE_CLIENT_ID: Your API client id, of the form <USERNAME>@AMER.OAUTHAP
  AMERITRADE_CONFIG_DIR: A private directory where your secrets will be stored.

Make sure you generated the required SSL certificates in the config dir like the
README file says. If you don't like using environment variables, you can use
command-line options. Type --help to get the full list of --ameritrade-*
options.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

import argparse
import ameritrade

def main():
    parser = argparse.ArgumentParser()
    ameritrade.add_args(parser)
    args = parser.parse_args()
    config = ameritrade.config_from_args(args)
    api = ameritrade.open(config)

    # Success!
    print(api)


if __name__ == '__main__':
    main()
