mk_lb.sh => builds a template of commands to run on a netscaler to build a new netscaler VIP and serviceGroup.  Crude, but works.  Defects on versions 10.5 and higher.

mk_lb_new.sh => a bit more flexible.  Should work on 10.5 and higher.  PRESUMES that the configuration from this site to get SSL up to grade A is completed:
https://www.citrix.com/blogs/2015/05/22/scoring-an-a-at-ssllabs-com-with-citrix-netscaler-the-sequel/

Also presumes the following has been run:
add policy expression response_2xx "HTTP.RES.STATUS.BETWEEN(200,299)"
add policy expression response_4xx "HTTP.RES.STATUS.BETWEEN(400,499)"
add policy expression response_5xx "HTTP.RES.STATUS.BETWEEN(500,599)"


