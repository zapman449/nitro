#!/usr/bin/env python

from __future__ import print_function, division, absolute_import, unicode_literals
import argparse

import requests

import netscaler


def parse_cli():
    """duh."""
    parser = argparse.ArgumentParser(description='update netscaler group definition')
    parser = netscaler.parse_cli_netscaler_config(parser)
    parser = netscaler.parse_cli_group_config(parser)
    parser = netscaler.parse_cli_name_ip(parser)
    args = parser.parse_args()
    nsconf = netscaler.validate_cli_netscaler_config(args)
    groupconf = netscaler.validate_cli_group_config(args)
    return args, nsconf, groupconf


if __name__ == '__main__':
    args, nsconf, groupconf = parse_cli()
    s = requests.session()
    netscaler.add_to_group(args.servername,
                           args.ip,
                           s,
                           nsconf,
                           groupconf,
                           verbose=True)
    netscaler.save_config(s, nsconf)
