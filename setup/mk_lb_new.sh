#!/bin/bash

USAGE() {
	echo "USAGE: $0 group_name domain region lb_ip lb_port <SSL|HTTP|TCP> <internal|external> holder_vs_id <new|reuse>"
	echo "new implies HTTP response counter policies do not exist yet."
	echo "Reuse assumes they are made already"
	echo "also gives one or two slcli commands to rename an instance"
	echo "holding the VIP ip (presumes softlayer)"
	echo "and/or add a dns record for this LB to the domain specified"
	echo
	echo "new and reuse are so you can setup multiple VIPs around the"
	echo "same service group.  This invocation set will build 3 vips"
	echo "(internal HTTP, external SSL external HTTP) around the same group:"
	echo
	echo "./mk_lb_new.sh iapi dom.companyname.com insightprod 10.02.03.44 80 HTTP internal 1111 new"
	echo "./mk_lb_new.sh iapi dom.companyname.com insightprod 11.22.33.44 443 SSL external 1111 reuse"
	echo "./mk_lb_new.sh iapi dom.companyname.com insightprod 11.22.33.44 80 HTTP external 1111 reuse"
	exit
}

if [ -z "$9" ]; then
	USAGE
fi

group_name=$1
domain=$2
environment=$3
lb_ip=$4
lb_port=$5
lb_protocol=$6
if [ "$lb_protocol" == "HTTPS" ]; then
	lb_protocol=SSL
fi
lb_protocol_lower=$(echo $lb_protocol | tr '[A-Z]' '[a-z]')
direction=$7
holder_vs_id=$8
new_policies=$9

if [ "$direction" == "internal" ]; then
	i='int'
else
	i='ext'
fi
lb_name=${group_name}-${environment}-${i}-${lb_protocol_lower}-lb

echo "add lb vserver ${lb_name} ${lb_protocol} ${lb_ip} ${lb_port} -persistenceType NONE -cltTimeout 180 -appflowLog DISABLED -icmpVsrResponse ACTIVE"

if [ ${new_policies} == "new" ]; then
	if [ "${lb_protocol}" == "HTTP" ] || [ "${lb_protocol}" == "SSL" ]; then
        echo "add rewrite policy ${group_name}-response_2xx response_2xx NOREWRITE"
        echo "add rewrite policy ${group_name}-response_4xx response_4xx NOREWRITE"
        echo "add rewrite policy ${group_name}-response_5xx response_5xx NOREWRITE"
	fi
fi

if [ "${lb_protocol}" == "HTTP" ] || [ "${lb_protocol}" == "SSL" ]; then
	group_protocol=HTTP
elif [ ${lb_protocol} == "TCP" ]; then
	group_protocol=TCP
fi

if [ $new_policies == "new" ]; then
    echo "add serviceGroup ${group_name} ${group_protocol} -maxClient 0 -maxReq 0 -cip DISABLED -usip NO -useproxyport YES -cltTimeout 180 -svrTimeout 360 -CKA YES -TCPB NO -CMP NO -appflowLog DISABLED"
fi

echo "bind lb vserver ${lb_name} ${group_name}"

if [ ${lb_protocol} == "HTTP" ] || [ ${lb_protocol} == "SSL" ]; then
    echo "bind lb vserver ${lb_name} -policyName ${lb_name}-response_2xx -priority 101 -gotoPriorityExpression END -type RESPONSE"
    echo "bind lb vserver ${lb_name} -policyName ${lb_name}-response_4xx -priority 102 -gotoPriorityExpression END -type RESPONSE"
    echo "bind lb vserver ${lb_name} -policyName ${lb_name}-response_5xx -priority 103 -gotoPriorityExpression END -type RESPONSE"
fi

if [ ${lb_protocol} == "SSL" ]; then
    echo "set ssl vserver iapi-devmvac-tor01-ext-lb -dh ENABLED -dhFile \"/nsconfig/ssl/dhkey2048.key\" -dhCount 1000 -ssl3 DISABLED"
    echo "bind lb vserver ${lb_name} -policyName pol_sts_force -priority 100 -gotoPriorityExpression END -type REQUEST"
    echo "bind ssl vserver ${lb_name} -cipherName default-cipher-group-vpx-2015-11-18"
    echo "bind ssl vserver ${lb_name} -certkeyName insight.ibmcloud.com-2015-11-18"
    echo "bind ssl vserver ${lb_name} -eccCurveName P_256"
    echo "bind ssl vserver ${lb_name} -eccCurveName P_384"
    echo "bind ssl vserver ${lb_name} -eccCurveName P_224"
    echo "bind ssl vserver ${lb_name} -eccCurveName P_521"
fi

echo "save config"

echo
echo "-----> here begin SLCLI commands which may be useful"
if [ "${direction}" == "internal" ]; then
    echo "slcli vs edit -H holds-${lb_name} $holder_vs_id"
fi
echo "slcli dns record-add --ttl 600 ${domain} ${lb_name} A ${lb_ip}"


exit


add rewrite policy iapi-devmvac-tor01-ext-lb-response_2xx response_2xx NOREWRITE
add rewrite policy iapi-devmvac-tor01-ext-lb-response_4xx response_4xx NOREWRITE
add rewrite policy iapi-devmvac-tor01-ext-lb-response_5xx response_5xx NOREWRITE
add lb vserver iapi-devmvac-tor01-ext-lb SSL 169.53.168.232 443 -persistenceType NONE -Listenpolicy None -cltTimeout 180 -appflowLog DISABLED -icmpVsrResponse ACTIVE
bind lb vserver iapi-devmvac-tor01-ext-lb iapi
bind lb vserver iapi-devmvac-tor01-ext-lb -policyName pol_sts_force -priority 100 -gotoPriorityExpression END -type REQUEST
bind lb vserver iapi-devmvac-tor01-ext-lb -policyName iapi-devmvac-tor01-ext-lb-response_2xx -priority 101 -gotoPriorityExpression END -type RESPONSE
bind lb vserver iapi-devmvac-tor01-ext-lb -policyName iapi-devmvac-tor01-ext-lb-response_4xx -priority 102 -gotoPriorityExpression END -type RESPONSE
bind lb vserver iapi-devmvac-tor01-ext-lb -policyName iapi-devmvac-tor01-ext-lb-response_5xx -priority 103 -gotoPriorityExpression END -type RESPONSE
set ssl vserver iapi-devmvac-tor01-ext-lb -dh ENABLED -dhFile "/nsconfig/ssl/dhkey2048.key" -dhCount 1000 -ssl3 DISABLED
bind ssl vserver iapi-devmvac-tor01-ext-lb -cipherName default-cipher-group-vpx-2015-11-18
bind ssl vserver iapi-devmvac-tor01-ext-lb -certkeyName insight.ibmcloud.com-2015-11-18
bind ssl vserver iapi-devmvac-tor01-ext-lb -eccCurveName P_256
bind ssl vserver iapi-devmvac-tor01-ext-lb -eccCurveName P_384
bind ssl vserver iapi-devmvac-tor01-ext-lb -eccCurveName P_224
bind ssl vserver iapi-devmvac-tor01-ext-lb -eccCurveName P_521
