# -*- coding: utf-8 -*-

# ****************************************************
# * module_inventory.py
# *
# *    read and write inventory function and procedure
# *
# *  2018/06/08  T.Noguchi  create
# *
# ****************************************************

import os
import sys
#sys.path.append('')

import requests
import json

#from miapi.system.command_line_interpreter import CommandLineInterpreter
#from miapi.system import runinfo

# -----------------------------------
# module variable
# -----------------------------------
app_format = 'application/json'
proxies    = {'http': 'http://wwwout.nims.go.jp', 
              'https': 'http://wwwout.nims.go.jp'}

# -----------------------------------
# local function
# -----------------------------------

# ---------------------------------------------
# operate inventory api
#
#  note)
# ---------------------------------------------
#
def webapi_inventory(token, weburl, invdata, ope):
    '''
    read inventory data
      [args]
        token     : authorization API token
        weburl    : webapi target access url
        invdata   : inventory data(json format)
        ope       : operation command
                    get    - read data
                    post   - write data
                    delete - delete data

    '''

    # init param
    headers = {'Authorization': 'Bearer ' + token, 
               'Content-Type': app_format, 
               'Accept': app_format}

    # http request
    session = requests.Session()
    session.trust_env = False

    if (ope == "get"):
        cmd = "session." + ope + \
            "(weburl, headers=headers)"
    elif (ope == "post"):
        cmd = "session." + ope + \
            "(weburl, json=invdata, headers=headers)"
    elif (ope == "delete"):
        cmd = "session." + ope + \
            "(weburl)"

    res = eval(cmd)

    # result
    #print('[request results]')
    #print('weburl  : ' + res.url)
    #print('status  : ' + str(res.status_code))
    #print('headers : ' + str(res.headers))
    #print('body    : ' + res.text)

    return res

# ---------------------------------------------
# parse json
#
#  note)
# ---------------------------------------------
#
def parse_json(jsonData, target):
    '''
    parse jsonData for target
      [args]
        jsonData  : input json data
        target    : object type
                     descriptor
                     prediction_models
                     software_tools

    '''

    # init
    res = 0

    return res



