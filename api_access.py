#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.

'''
API Access関数
'''

import requests

def apiAccess(token, weburl, method="get", invdata=None, debug_print=False):
    '''
    Inventory Reference API Get method
    @param token(64character barer type token)
    @param weburl(URL for API access)
    @param invdata(body for access by json)
    @retval (json = dict) There is None if error has occured.
    '''

    # parameter
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': 'application/json',
               'Accept': 'application/json'}

    # http request
    session = requests.Session()
    session.trust_env = False

    if method == "get":
        res = session.get(weburl, json=invdata, headers=headers)
    elif method == "delete":
        res = session.delete(weburl, json=invdata, headers=headers)
    elif method == "post":
        res = session.post(weburl, json=invdata, headers=headers)
    #print res

    if res.status_code != 200 and res.status_code != 201:
        if debug_print is True:
            print("error   : ")
            print('status  : ' + str(res.status_code))
            print('body    : ' + res.text)
            print('-------------------------------------------------------------------')
            print('url     : ' + weburl)
            #print('headers : ' + str(res.headers))
            #print('headers : ' + str(headers))
        return False, res

    return True, res

