#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ALi
20180909
Python 3.7.0
"""

import dns.resolver  # pip install dnspython


"""
Get_MX() DNS MX记录查询
get(domain)
    In:
        domain 域名
    Out:
        查询成功 response[[优先级, 记录]]
        查询失败 False
"""


class Get_MX(object):
    def get(self, domain):
        try:
            response = []
            mxs = dns.resolver.query(domain, 'MX')
            for mx in mxs:
                response.append([mx.preference, str(mx.exchange)])
            return response
        except BaseException:
            return False
