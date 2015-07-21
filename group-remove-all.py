#!/usr/bin/env python

from __future__ import print_function, division, absolute_import, unicode_literals
import argparse
import pprint

import requests

import netscaler


def main(s, nsconf, groupconf):
    """main function.  finds what is there, then removes everything."""
    current_group = netscaler.get_group(s, nsconf, groupconf)
    future_group = set()
    servers_to_add = future_group - current_group
    servers_to_remove = current_group - future_group
    pprint.pprint(servers_to_add)
    print("######")
    pprint.pprint(servers_to_remove)
    for name, ip in servers_to_add:
        netscaler.add_to_group(name, ip, s, nsconf, groupconf)
    for name, ip in servers_to_remove:
        netscaler.remove_from_group(name, ip, s, nsconf, groupconf)
    if len(servers_to_add) + len(servers_to_remove) != 0:
        netscaler.save_config(s, nsconf)


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
    main(s, nsconf, groupconf)
