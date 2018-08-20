#!/usr/bin/env python3
"""Suitable quotes for daily short strangle options strategy.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import argparse
import logging

import ameritrade

def main():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    ameritrade.add_script_args(parser)
    args = parser.parse_args()
    api = ameritrade.open_with_args(args)

    print(api.GetAccounts())




if __name__ == '__main__':
    main()
