#!/usr/bin/env python

"""Library for leveraging the Netscaler Nitro REST API via python."""

from __future__ import print_function, division, absolute_import, unicode_literals
import argparse
import json
import os.path
import pprint
import sys

import requests


##############################################################################
# group membership changes


def get_lbvserver_codes(name, s, nsconf, verbose=False):
    """Get the response code counts and rates for 2xx, 4xx, 5xx"""
    url2xx = nsconf['baseurl'] + '/nitro/v1/stat/rewritepolicy/{0}-response_2xx'.format(name)
    url4xx = nsconf['baseurl'] + '/nitro/v1/stat/rewritepolicy/{0}-response_4xx'.format(name)
    url5xx = nsconf['baseurl'] + '/nitro/v1/stat/rewritepolicy/{0}-response_5xx'.format(name)
    response2xx = s.get(url2xx, auth=nsconf['auth'], verify=nsconf['verify'])
    response4xx = s.get(url4xx, auth=nsconf['auth'], verify=nsconf['verify'])
    response5xx = s.get(url5xx, auth=nsconf['auth'], verify=nsconf['verify'])
    results = []
    if response2xx.status_code != 200:
        print("got error for 2xx", response2xx.text)
    else:
        t = json.loads(response2xx.text)
        v = t['rewritepolicy'][0]
        v['helper_name'] = name
        v['helper_response_code'] = '2xx'
        results.append(v)
    if response4xx.status_code != 200:
        print("got error for 4xx", response4xx.text)
    else:
        t = json.loads(response4xx.text)
        v = t['rewritepolicy'][0]
        v['helper_name'] = name
        v['helper_response_code'] = '4xx'
        results.append(v)
    if response5xx.status_code != 200:
        print("got error for 5xx", response5xx.text)
    else:
        t = json.loads(response5xx.text)
        v = t['rewritepolicy'][0]
        v['helper_name'] = name
        v['helper_response_code'] = '5xx'
        results.append(v)
    return results


def get_group_stats(name, s, nsconf, verbose=False):
    """get the statistics for a whole group (useless... only showed enabled or not)"""
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.servicegroup+json"}
    url = nsconf['baseurl'] + '/nitro/v1/stat/servicegroup/{0}'.format(name)
    payload = {}
    response = s.get(url,
                     headers=headers,
                     data=json.dumps(payload),
                     auth=nsconf['auth'],
                     verify=nsconf['verify'])
    if verbose:
        print('getting stats for group:', name, 'code', response.status_code, '\ntext:', response.text)
    if response.status_code != 200:
        sys.exit("error retrieving group stats for {0}".format(name))
    else:
        return json.loads(response.text)


def get_group_member_stats(s, nsconf, groupconf, verbose=False):
    """Get the stats for all group members. NOTE: CURRENTLY BROKEN.  Use _works"""
    name = groupconf['svcgroupname']
    # port = groupconf['port']
    url = nsconf['baseurl'] + '/nitro/v1/stat/servicegroupmember/{0}'.format(name)
    # payload = {'servicegroupmember': {'svcgroupname': name}}
    response = s.get(url,
                     auth=nsconf['auth'],
                     verify=nsconf['verify'])
#                      headers=headers,
#                      data=json.dumps(payload),
    if verbose:
        print('getting stats for members of group:', name, 'code', response.status_code, '\ntext:', response.text)
    if response.status_code == 200:
        results = json.loads(response.text)
        return results
    else:
        sys.exit("failed to retrieve stats from group {0}".format(name))


def get_group_member_stats_works(s, nsconf, groupconf, verbose=False):
    """Get stats from all group members

    Working version of member_stats.  This will get all members' statistics
    of a given group.  The bad news of this is it queries the group, then
    queries each member in turn, rather than getting everything at once in
    a single query.
    """
    name = groupconf['svcgroupname']
    port = groupconf['port']
    jr = _get_group_base(s, nsconf, groupconf)
    results = []
    for server in jr['servicegroup_servicegroupmember_binding']:
        member_name = server['servername']
        # member_ip = server['ip']
        # headers = {'Content-Type': "application/vnd.com.citrix.netscaler.servicegroupmember+json"}
        url = nsconf['baseurl'] + '/nitro/v1/stat/servicegroupmember?args=servicegroupname:{0},serverName:{1},port:{2}'.format(name, member_name, port)
        # payload = {'servicegroupmember': {'svcgroupname': name}}
        response = s.get(url,
                         auth=nsconf['auth'],
                         verify=nsconf['verify'])
    #                      headers=headers,
    #                      data=json.dumps(payload),
        if verbose:
            print('getting stats for member', member_name, 'of group:', name, 'code', response.status_code, '\ntext:', response.text)
        if response.status_code == 200:
            temp_results = json.loads(response.text)
            to_add = temp_results['servicegroupmember'][0]
            to_add['helper_svcgroupname'] = name
            to_add['helper_port'] = port
            to_add['helper_svcgroupmember'] = member_name
            results.append(temp_results['servicegroupmember'][0])
    return results


def get_all_lbvserver_stats(s, nsconf, verbose=False):
    """Get the stats of all lbvservers"""
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.lbvserver+json"}
    url = nsconf['baseurl'] + '/nitro/v1/stat/lbvserver'
    payload = {}
    response = s.get(url,
                     headers=headers,
                     data=json.dumps(payload),
                     auth=nsconf['auth'],
                     verify=nsconf['verify'])
    if verbose:
        print('getting stats for all lbvservers: code', response.status_code, '\ntext:', response.text)
    if response.status_code != 200:
        sys.exit("error retrieving lbv stats")
    else:
        return json.loads(response.text)


def get_lbvserver_stats(name, s, nsconf, verbose=False):
    """Get the stats of a single lbvservers"""
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.lbvserver+json"}
    url = nsconf['baseurl'] + '/nitro/v1/stat/lbvserver/{0}'.format(name)
    payload = {}
    response = s.get(url,
                     headers=headers,
                     data=json.dumps(payload),
                     auth=nsconf['auth'],
                     verify=nsconf['verify'])
    if verbose:
        print('getting stats for lbvserver:', name, 'code', response.status_code, '\ntext:', response.text)
    if response.status_code != 200:
        sys.exit("error retrieving lbv stats for {0}".format(name))
    else:
        return json.loads(response.text)


##############################################################################
# group membership changes


def _server_exists(name, ip, s, nsconf, verbose=False):
    """Gets a server, if it exists"""
    url = nsconf['baseurl'] + '/nitro/v1/config/server/{0}'.format(name)
    response = s.get(url,
                     auth=nsconf['auth'],
                     verify=nsconf['verify'])
    if verbose:
        print('__getting server:', name, 'code', response.status_code, '\ntext:', response.text)
    if response.status_code == 404:
        return False
    if response.status_code == 200:
        body = response.json
        if ip == body['server']['ipaddress']:
            return True
        return False


def _server_binding_exists(name, ip, s, nsconf, verbose=False):
    """Sees if a server has any bindings still"""
    url = nsconf['baseurl'] + '/nitro/v1/config/server_binding/{0}'.format(name)
    response = s.get(url,
                     auth=nsconf['auth'],
                     verify=nsconf['verify'])
    if verbose:
        print('__getting server_binding:', name, 'code', response.status_code, '\ntext:', response.text)
    if response.status_code == 404:
        return False
    if response.status_code == 200:
        body = response.json
        # if lenbody['server_binding']['server_servicegroup_binding']:
        if len(body['server_binding']['server_servicegroup_binding']) == 0:
            return True
        return False


def add_to_group(name, ip, s, nsconf, groupconf, verbose=False):
    """create server defined by name/ip and then bind it to a group."""
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.server+json"}
    url = nsconf['baseurl'] + '/nitro/v1/config/server?action=add'
    payload = {'server': {'name': name,
                          'ipaddress': ip}}
    response = s.post(url,
                      headers=headers,
                      data=json.dumps(payload),
                      auth=nsconf['auth'],
                      verify=nsconf['verify'])
    if verbose:
        print('adding server:', name, 'code', response.status_code, '\ntext:', response.text)
    #####
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.servicegroup_servicegroupmember_binding+json"}
    url = nsconf['baseurl'] + '/nitro/v1/config/servicegroup_servicegroupmember_binding/{0}'.format(groupconf['svcgroupname'])
    payload = {'servicegroup_servicegroupmember_binding': {'servicegroupname': groupconf['svcgroupname'],
                                                           'servername': name,
                                                           'port': groupconf['port']}}
    response = s.post(url,
                      headers=headers,
                      data=json.dumps(payload),
                      auth=nsconf['auth'],
                      verify=nsconf['verify'])
    if verbose:
        print('binding server', name, 'to group', groupconf['svcgroupname'], 'code', response.status_code, '\ntext:', response.text)


def remove_from_group(name, ip, s, nsconf, groupconf, verbose=False):
    """remove server defined by name/ip from a group, then destroy that server."""
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.servicegroup_servicegroupmember_binding+json"}
    url = nsconf['baseurl'] + '/nitro/v1/config/servicegroup_servicegroupmember_binding/{0}?action=unbind'.format(groupconf['svcgroupname'])
    payload = {'servicegroup_servicegroupmember_binding': {'servicegroupname': groupconf['svcgroupname'],
                                                           'servername': name,
                                                           'port': groupconf['port']}}
    # try port as str() next
    response = s.post(url,
                      headers=headers,
                      data=json.dumps(payload),
                      auth=nsconf['auth'],
                      verify=nsconf['verify'])
    if verbose:
        print('unbinding server', name, 'from group', groupconf['svcgroupname'], 'code', response.status_code, '\ntext:', response.text)
        print()
        print(json.dumps(payload))
    #####
        print('\n')
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.server+json"}
    url = nsconf['baseurl'] + '/nitro/v1/config/server/{0}'.format(name)
    # payload = {'server': {'name': name,
    #                       'ipaddress': ip},
    #            'name': name}
    response = s.delete(url,
                        headers=headers,
                        auth=nsconf['auth'],
                        verify=nsconf['verify'])
    #                     data=json.dumps(payload),
    if verbose:
        print('deleting server:', name, 'code', response.status_code, '\ntext:', response.text)


##############################################################################
# group details


def _get_group_base(s, nsconf, groupconf, verbose=False):
    """get the current servers in a group"""
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.servicegroup_servicegroupmember_binding+json"}
    url = nsconf['baseurl'] + '/nitro/v1/config/servicegroup_servicegroupmember_binding/{0}'.format(groupconf['svcgroupname'])
    payload = {'servicegroup_servicegroupmember_binding': {'servicegroupname': groupconf['svcgroupname']}}
    response = s.get(url,
                     headers=headers,
                     data=json.dumps(payload),
                     auth=nsconf['auth'],
                     verify=nsconf['verify'])
    # print('enumerating group', groupconf['svcgroupname'], 'code', response.status_code, '\ntext:', response.text)
    # pprint.pprint(json.loads(response.text))
    jr = json.loads(response.text)
    return jr


def get_group(s, nsconf, groupconf, verbose=False):
    """wrapper for _get_group_base.  only shows name and IP"""
    jr = _get_group_base(s, nsconf, groupconf)
    results = set()
    if 'servicegroup_servicegroupmember_binding' in jr:
        # cover the 'no servers in group case'
        for server in jr['servicegroup_servicegroupmember_binding']:
            results.add((server['servername'], server['ip']))
    return results


def get_group_verbose(s, nsconf, groupconf, verbose=False):
    """wrapper for _get_group_base.  Shows name, ip, state and server_state"""
    jr = _get_group_base(s, nsconf, groupconf)
    results = set()
    if 'servicegroup_servicegroupmember_binding' in jr:
        # cover the 'no servers in group case'
        for server in jr['servicegroup_servicegroupmember_binding']:
            results.add((server['servername'],
                         server['ip'],
                         server['state'],
                         server['svrstate']))
    return results


def build_group(name, s, nsconf, verbose=False):
    """build group as python object

    return a dict definition doc for a group with all relevant details.
    Encoded as a python object. You probably want build_group_json() instead.
    """
    result = {}
    result['svcgroupname'] = name
    jr = _get_group_base(s, nsconf, {'svcgroupname': name})
    result['servers'] = []
    for s in jr['servicegroup_servicegroupmember_binding']:
        result['servers'].append([s['servername'], s['ip']])
        result['port'] = s['port']
    return json.dumps(result, indent=4)


def build_group_json(name, s, nsconf, indent=4, verbose=False):
    """build group as a json object

    returns a json representation of a groups definition. useful for
    bootstrapping things. Indent is passed directly to json.dumps. set
    indent=none if you want a pure string
    """
    # grrr... need a file handle.
    result = build_group(name, s, nsconf, verbose=verbose)
    return json.dumps(result, indent=indent)


##############################################################################
# list groups, list vservers


def list_groups(s, nsconf, verbose=False):
    """list names of all groups"""
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.servicegroup+json"}
    url = nsconf['baseurl'] + '/nitro/v1/stat/servicegroup/'
    payload = {}
    response = s.get(url,
                     headers=headers,
                     data=json.dumps(payload),
                     auth=nsconf['auth'],
                     verify=nsconf['verify'])
    if verbose:
        print('getting stats for all groups. code', response.status_code, '\ntext:', response.text)
    if response.status_code != 200:
        sys.exit("error retrieving groups")
    r1 = json.loads(response.text)
    return r1['servicegroup']


def list_lbvservers(s, nsconf, verbose=False):
    """list names of all vservers"""
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.lbvserver+json"}
    url = nsconf['baseurl'] + '/nitro/v1/stat/lbvserver/'
    payload = {}
    response = s.get(url,
                     headers=headers,
                     data=json.dumps(payload),
                     auth=nsconf['auth'],
                     verify=nsconf['verify'])
    if verbose:
        print('getting stats for all lbvservers. code', response.status_code, '\ntext:', response.text)
    if response.status_code != 200:
        sys.exit("error retrieving groups")
    result = []
    r1 = json.loads(response.text)
    for lb in r1['lbvserver']:
        result.append({'name': lb['name'],
                       'ip': lb['primaryipaddress'],
                       'type': lb['type'],
                       'state': lb['state']})
    return result


##############################################################################
# save config, and front matter


def save_config(s, nsconf):
    """save the netscaler config"""
    headers = {'Content-Type': "application/vnd.com.citrix.netscaler.nsconfig+json"}
    url = nsconf['baseurl'] + '/nitro/v1/config/nsconfig?action=save'
    payload = {'nsconfig': {}}
    response = s.post(url,
                      headers=headers,
                      data=json.dumps(payload),
                      auth=nsconf['auth'],
                      verify=nsconf['verify'])
    print('saving... code', response.status_code, '\ntext:', response.text)


def setup_group(list_o_servers):
    """transform list o list of name,ip into a set"""
    results = set()
    for name, ip in list_o_servers:
        results.add((name, ip))
    return results


def is_ns_primary(nsip, nsconf):
    """Finds the primary netscaler IP

    Returns true of false.  Given an NSIP, determine if it's a primary (or
    only) address in a netscaler cluster
    """
    url = "{0}://{1}/nitro/v1/stat/hanode".format(nsconf['protocol'], nsip)
    resp = requests.get(url,
                        auth=nsconf['auth'],
                        verify=nsconf['verify'])
    # use a stand-alone requests object for this.  Everything else uses a
    # requests.session.
    if resp.status_code != 200:
        sys.exit("failed to check HA. Body is: " + resp.text)
    data = json.loads(resp.text)
    if data['hanode']["hacurstatus"] == "NO":
        return True
    elif data['hanode']['hacurmasterstate'] == 'Primary':
        return True
    else:
        return False


def main(s, nsconf, groupconf):
    """main function.  finds what to add and remove, then orders it to happen"""
    current_group = get_group(s, nsconf, groupconf)
    future_group = setup_group(groupconf['servers'])
    servers_to_add = future_group - current_group
    servers_to_remove = current_group - future_group
    # pprint.pprint(servers_to_add)
    # print("######")
    # pprint.pprint(servers_to_remove)
    for name, ip in servers_to_remove:
        remove_from_group(name, ip, s, nsconf, groupconf)
    for name, ip in servers_to_add:
        add_to_group(name, ip, s, nsconf, groupconf)
    if len(servers_to_add) + len(servers_to_remove) != 0:
        save_config(s, nsconf)


def update_nsconf(nsconf):
    """adds helper values to nsconf. Also validates which IP is right."""
    nsconf['auth'] = (nsconf['user'], nsconf['password'])
    found = False
    for ip in nsconf['nsips']:
        if is_ns_primary(ip, nsconf):
            found = True
            break
    if found:
        nsconf['baseurl'] = '{0}://{1}'.format(nsconf['protocol'], ip)
        return None
    else:
        sys.exit("no valid netscaler found. try again in a few minutes")


def parse_cli_netscaler_config(parser):
    """add --netscaler_config argument to the parser"""
    parser.add_argument('-n', '--netscaler_config', required=True,
                        help='json formatted file specifying nsip, user, password,'
                             'access protocol (http or https), and verify (true'
                             'or false, for ssl key verification)')
    return parser


def parse_cli_group_config(parser):
    """add the --group_config object to the parser"""
    parser.add_argument('-g', '--group_config', required=True,
                        help='json formatted file specifying svcgroupname, port#, and'
                             'servers which is a list of lists specifying name,IP of'
                             'each member')
    return parser


def parse_cli_name_ip(parser):
    """add --servername and --ip to the parser"""
    parser.add_argument('-i', '--ip', required=True,
                        help='IP address to remove from group. requires server name too')
    parser.add_argument('-s', '--servername', required=True,
                        help='servername. requires ip too')
    return parser


def parse_cli_lbvserver_name(parser):
    """add --lbvserver name to the parser"""
    parser.add_argument('-l', '--lbvserver', required=True,
                        help='name of the lbvserver')
    return parser


def validate_cli_netscaler_config(args):
    """Validates netscaler config and builds remaining pieces in it."""
    if os.path.isfile(args.netscaler_config):
        with open(args.netscaler_config, 'r') as ns:
            try:
                nsconf = json.load(ns)
            except ValueError:
                sys.exit("Failed to parse json file {0}".format(args.netscaler_config))
        update_nsconf(nsconf)
        return nsconf
    else:
        sys.exit("no such netscaler config file {0}".format(args.netscaler_config))


def validate_cli_group_config(args):
    """validates group config"""
    if os.path.isfile(args.group_config):
        with open(args.group_config, 'r') as gc:
            try:
                groupconf = json.load(gc)
            except ValueError:
                sys.exit("Failed to parse json file {0}".format(args.group_config))
        return groupconf
    else:
        sys.exit("no such group config file {0}".format(args.group_config))


def parse_cli():
    """duh."""
    parser = argparse.ArgumentParser(description='update netscaler group definition')
    parser = parse_cli_netscaler_config()
    parser = parse_cli_group_config()
    parser.add_argument('--quiet', default=False, action='store_true',
                        help='show less output')
    args = parser.parse_args()
    nsconf = validate_cli_netscaler_config(args)
    groupconf = validate_cli_group_config(args)
    return args, nsconf, groupconf


if __name__ == '__main__':
    args, nsconf, groupconf = parse_cli()
    s = requests.session()
    if args.get_only:
        results = get_group_verbose()
        pprint.pprint(results)
    else:
        main(s, nsconf, groupconf)
