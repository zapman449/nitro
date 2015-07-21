A python front end for leveraging the NITRO REST API.
I found the REST API to be a huge pain.  So I buried it.

## Design goals:

1. A library to make most of the painful stuff easy.
2. A bunch of small and adaptable scripts which leverage the library
3. Use serviceGroups to manage most things.  Biggest concern of the
   library is to manage group membership.  
4. Use JSON files for configuration
5. Understand Netscaler HA configs, and only speak with the primary.  Should
   work with stand-alone servers too.

## Known limitations:

1. Currently there's no trivial way for a single server to exist in
   multiple groups.  This needs to be resolved soon.

## USAGE:
#### add-one-member.py AND remove-one-member.py
Adds or removes one member from a given group.
Example: Add system-name with IP of 11.22.33.44 to the group defined in group.json

    add-one-member.py -n ns.json -g group.json -s system-name -i 11.22.33.44

#### force-save.py
Force a config save
Example:

    force-save -n ./ns.json

#### group-remove-all.py
Removes all members from a group
Example:

    group-remove-all.py -n ns.json -g group.json

#### group-update.py
Updates a groups memberships to match the group.json file.  Extra
members are removed, new members added, members existing in both
are undisturbed.
Example:

    group-update.py -n ns.json -g group.json

#### list-all-groups.py
List all groups on netscaler
Example:

    list-all-groups.py -n ./ns.json

#### list-all-lbvservers.py
List all load balancing vservers on the netscaler
Example:

    list-all-lbvservers.py -n ./ns.json

#### list-group-members.py
List the current members of a group.  This ignores any servers listed
in group.json.
Example:

    list-group-members.py -n ns.json -g group.json

#### stats-all-lbvservers.py
Show the lb vserver stats for all lb vservers.  Pretty-prints the output.
(If you want to use this, you'll probably need to modify it to suit your
needs)
Example:

    stats-all-lbvservers.py -n ./ns.json

#### stats-group-members.py
Show group member stats.  Also ignores the server list in
group.json
Example:

    stats-group-members.py -n ns.json -g group.json

#### stats-group.py
Show the stats for a whole group.  Fairly useless.
Example:

    stats-group.py -n ns.json -g group.json

#### stats-lbvserver.py
Show the statistics for an lb vserver.  Pretty-prints the output
(If you want to use this, you'll probably need to modify it to suit your
needs)
Example:

    stats-lbvserver.p -n ns.json -l <lb-vserver-name>

#### codes-lbvserver.py
This will show a json dump of the current counters of 2xx, 4xx and 5xx
responses for an lb vserver.  Relies on the following netscaler settings:

a) These need to be estabished REWRITE rules:

    add expression response_4xx HTTP.RES.STATUS.BETWEEN(400,499)
    add expression response_2xx HTTP.RES.STATUS.BETWEEN(200,299)
    add expression response_5xx HTTP.RES.STATUS.BETWEEN(500,599)

b) For each lb vserver, you need to do the following (our policy is
to use the lb name, followed by the rewrite name):

    add rewritepolicy vorigin-ext-lb-response_2xx response_2xx norewrite
    add rewritepolicy vorigin-ext-lb-response_4xx response_4xx norewrite
    add rewritepolicy vorigin-ext-lb-response_5xx response_5xx norewrite
    bind lb vserver vorigin-ext-lb -policy vorigin-ext-lb-response_2xx -type RESPONSE -priority 100
    bind lb vserver vorigin-ext-lb -policy vorigin-ext-lb-response_4xx -type RESPONSE -priority 101
    bind lb vserver vorigin-ext-lb -policy vorigin-ext-lb-response_5xx -type RESPONSE -priority 102

Again, this pretty-prints the output. If you want to use this, you'll
probably need to modify it to suit your needs.
Example:

    codes-lbvserver.py -n ./ns.json -l vorigin-ext-lb

#### netscaler.py
The library.

## JSON Specifications

#### ns.json spec:
    {
      "nsips": ["192.168.177.21", "192.168.177.22"],
      "password": "api_user_password123",
      "protocol": "http",
      "user": "api_user",
      "verify": false
    }

The code automatically tries to see if the netscaler is an HA Pair,
and only will communicate with the current primary.  You can specify
http or https, and if you wish to verify the SSL cert for HTTPS.
user and password are fairly obvious.

#### group.json spec:
    {
      "svcgroupname": "vorigin",
      "port": 80,
      "servers": [
                   ["vorigin-qa-tor01-01", "192.168.46.101"],
                   ["vorigin-qa-tor01-02", "192.168.46.102"],
                   ["vorigin-qa-tor01-03", "192.168.46.96"],
                   ["vorigin-qa-tor01-04", "192.168.46.95"]
                 ]
    }

Specify the svcgroupname, the port for the group an the list of
servers who might be in the group.  Some commands rely on the
server list, some ignore it.  The serverlist is just a list of
two element lists.  The two elements are name and IP of the server.
