#!/usr/bin/env python

from __future__ import print_function, division, absolute_import, unicode_literals
import argparse
import pprint

import requests

import netscaler


def parse_cli():
    """duh."""
    parser = argparse.ArgumentParser(description='update netscaler group definition')
    parser = netscaler.parse_cli_netscaler_config(parser)
    parser = netscaler.parse_cli_group_config(parser)
    args = parser.parse_args()
    nsconf = netscaler.validate_cli_netscaler_config(args)
    groupconf = netscaler.validate_cli_group_config(args)
    return args, nsconf, groupconf


if __name__ == '__main__':
    args, nsconf, groupconf = parse_cli()
    s = requests.session()
    results = netscaler.get_group_verbose(s, nsconf, groupconf)
    pprint.pprint(results)
