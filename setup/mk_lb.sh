#!/bin/bash

USAGE() {
	echo "USAGE: $0 lb_name lb_ip lb_port lb_protocol group_name holder_vs_id"
	exit
}

if [ -z "$6" ]; then
	USAGE
fi

lb_name=$1
lb_ip=$2
lb_port=$3
lb_protocol=$4
group_name=$5
holder_vs_id=$6

echo "add lb vserver ${lb_name} ${lb_protocol} ${lb_ip} ${lb_port} -persistenceType NONE -cltTimeout 180 -appflowLog DISABLED -icmpVsrResponse ACTIVE"
if [ ${lb_protocol} == "HTTP" ] || [ ${lb_protocol} == "HTTPS" ]; then
   echo "add rewrite policy ${lb_name}-response_2xx response_2xx NOREWRITE"
   echo "add rewrite policy ${lb_name}-response_4xx response_4xx NOREWRITE"
   echo "add rewrite policy ${lb_name}-response_5xx response_5xx NOREWRITE"
fi
echo "add serviceGroup ${group_name} ${lb_protocol} -maxClient 0 -maxReq 0 -cip DISABLED -usip NO -useproxyport YES -cltTimeout 180 -svrTimeout 360 -CKA YES -TCPB NO -CMP NO -appflowLog DISABLED"
echo "bind lb vserver ${lb_name} ${group_name}"
if [ ${lb_protocol} == "HTTP" ] || [ ${lb_protocol} == "HTTPS" ]; then
   echo "bind lb vserver ${lb_name} -policyName ${lb_name}-response_2xx -priority 100 -gotoPriorityExpression END -type RESPONSE"
   echo "bind lb vserver ${lb_name} -policyName ${lb_name}-response_4xx -priority 101 -gotoPriorityExpression END -type RESPONSE"
   echo "bind lb vserver ${lb_name} -policyName ${lb_name}-response_5xx -priority 102 -gotoPriorityExpression END -type RESPONSE"
fi
echo "save config"

echo

echo "slcli vs edit -H holds-${lb_name} $holder_vs_id"
echo "slcli dns record-add --ttl 600 sunsl.weather.com ${lb_name} A ${lb_ip}"
