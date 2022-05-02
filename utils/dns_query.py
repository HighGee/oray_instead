# -*- coding:utf-8 -*-
# Design by Haiji
# Date 2020/7/12 08:33
import dns
import ipaddress
import subprocess
import dns.resolver


def isIP(ip):
    try:
        ipaddress.ip_address(ip)
    except Exception:
        return False
    return True


def get_address(item):
    try:
        return item.address
    except Exception:
        return


def DNSQuery(ip):
    """
    若是IPV4/V6则直接返回,若不是则获取记录后返回
    """
    dns_server = '114.114.114.114'
    result = {"status": "False"}
    ips = []

    if isIP(ip):
        ips.append(ip)
        result.update({'status': "True", 'ips': ips})
        return result

    try:
        dns_query = dns.message.make_query(ip, 'A')
        res = dns.query.udp(dns_query, dns_server, timeout=2)
        result['ips'] = [get_address(
            item) for answer in res.answer for item in answer.items if get_address(item)]  # noqa
    except Exception:
        cmd = 'dig %s @%s +short' % (ip, dns_server)
        exec_std = subprocess.getoutput(cmd)
        if not exec_std:
            result['ips'] = []
            return result
        exec_list = exec_std.split('\n')
        res_ips = [item for item in exec_list if isIP(item)]
        result['ips'] = res_ips
    return result
