# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2020/7/12 08:33
import dns
import subprocess
import dns.resolver
from netaddr.ip import IPAddress


def isIP4or6(cfgstr):
    if '/' in cfgstr:
        text = cfgstr[:cfgstr.rfind('/')]
    else:
        text = cfgstr

    try:
        IPAddress(text)
        ipFlg = True
    except Exception:
        ipFlg = False

    return True if ipFlg else False


def DNSQuery(ip):
    """
    若是IPV4/V6则直接返回,若不是则获取记录后返回
    """
    dns_server = '114.114.114.114'
    result = {}
    ips = []
    ip_verify = isIP4or6(ip)
    if not ip_verify:
        result['status'] = "False"
        try:
            dns_query = dns.message.make_query(ip, 'A')
            res = dns.query.udp(dns_query, dns_server, timeout=2)
            for i in res.answer:
                for j in i.items:
                    try:
                        ips.append(j.address)
                    except Exception:
                        pass
            result['ips'] = ips
        except Exception:
            cmd = 'dig %s @%s +short' % (ip, dns_server)
            B = subprocess.getoutput(cmd).split('\n')
            res_ips = []
            if B == ['']:
                result['ips'] = []
            else:
                for item in B:
                    item_res = DNSQuery(item)
                    if item_res['status'] == 'False':
                        pass
                    else:
                        res_ips.append(item)
                result['ips'] = res_ips
        return result

    else:
        result['status'] = "True"
        ips.append(ip)
        result['ips'] = ips
        return result
