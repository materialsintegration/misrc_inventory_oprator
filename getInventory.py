# -*- coding: utf-8 -*-

# ****************************************************
# * getInventory2.py
# *
# *    read inventory descriptors
# *
# *  2018/07/20  T.Noguchi  create
# *
# ****************************************************

import os
import sys
import ast
import requests
if sys.version_info[0] <= 2:
    import ConfigParser
    from urlparse import urlparse
else:
    import configparser
    from urllib.parse import urlparse
import json
import codecs
import time

import module_inventory as inv

# =======================================
# config
# =======================================
webapi_refroot = 'https://nims.mintsys.jp:50443/inventory-api/v3'
webapi_updroot = 'https://nims.mintsys.jp:50443/inventory-update-api/v3'
#ifile = 'inventory_out.json'
#ofile = 'inventory_out.json'

# conf file
conf_file = "Inventory.conf"
config_settings = {
    'authorize': [
        {'name': 'user_id',   'type': str,  'required': True},
        {'name': 'token',     'type': str,  'required': True},
    ],
    'resource': [
        {'name': 'url',       'type': str,  'required': True},
        {'name': 'query',     'type': str,  'required': False},
    ],
    'file': [
        {'name': 'object',    'type': str,  'required': True},
        {'name': 'inputfile', 'type': str,  'required': True},
        {'name': 'outputfile','type': str,  'required': True},
    ],
}

# debug json
replace_dic = {'preferred_name_lang': 'preferred_name_language'}

# codec
codec = 'utf-8'

# response code
httpcode_success = 200

# =======================================
# local function
# =======================================
# read and set config param
def configParse(file_path) :

    ### File check
    if not os.path.exists(file_path) :
        raise IOError(file_path)

    if sys.version_info[0] <= 2:
        parser = ConfigParser.SafeConfigParser()
    else:
        parser = configparser.ConfigParser()
    parser.read(file_path)

    ### Convert to dictionary
    config = {}
    for sect in parser.sections() :
        config[sect] = {}
        for opt in parser.options(sect) :
            config[sect][opt] = parser.get(sect, opt)

    ### Data check and convert from type
#    for sect in config_settings.keys() :
    for sect in config.keys() :
        # multisector check
        if sect.startswith('resource') :
            sect_a = 'resource'
        else :
            sect_a = sect

        # check section
        if not sect_a in config_settings :
            raise KeyError(sect)

        for opt_attr in config_settings[sect_a] :
            # check need attributes
            if opt_attr['required'] and (not opt_attr['name'] in config[sect]) :

                raise KeyError(opt_attr['name'])

            # exchange
            if config[sect][opt_attr['name']] == 'None' :
                config[sect][opt_attr['name']] = None
            else :
                config[sect][opt_attr['name']] = opt_attr['type'](config[sect][opt_attr['name']])

    return config

# =======================================
# main
# =======================================

def getInventory_main(webapi_refroot,):
    stime = time.time()
    print('----- start getInventory script -----')    

    # init

    # ///////////////////////////////
    # read config file
    # ///////////////////////////////   
    config = None
    config = configParse(conf_file)

    uid   = config['authorize']['user_id']
    token = config['authorize']['token']
    url   = config['resource']['url']
    query = config['resource']['query']
    lst   = config['file']['object']
    objs  = lst.split('\n')
    lst   = config['file']['inputfile']
    ifiles = lst.split('\n') 
    lst   = config['file']['outputfile']
    ofiles = lst.split('\n') 

    print('[conf file]')
    print('url         : ' + url)
    print('query       : ' + query)
    print('object      : ' + ', '.join(objs))
    print('input file  : ' + ', '.join(ifiles))
    print('output file : ' + ', '.join(ofiles))
    print('-------------------------------------')

    # ///////////////////////////////
    # read inventory data
    # ///////////////////////////////
    print('read inventory... from %s'%webapi_refroot)

    IDs = {}
    for i, obj in enumerate(objs):
        # keyword set
        key1 = obj + 's'                     # descriptors
        key2 = obj.replace('-', '_') + '_id' # descriptior_id
        key3 = obj.replace('-', '_') + 's'   # prediction_models

        print('[' + obj + ']')
        print('')

        IDs[obj] = []

        # outfile
        jsonfile = ofiles[i]
        f = codecs.open(jsonfile, 'w', codec)

        # --------------------------------
        # get object list
        # --------------------------------
        # query param
        dest_url = webapi_refroot + '/' + url + '/' + \
                   key1 + '/?q=' + query

        # call webapi
        rlt = inv.webapi_inventory(token, dest_url, None, 'get')
        rlt_dic = ast.literal_eval(rlt.text) 
   
        if (rlt.status_code != httpcode_success):
            print('http request cause error')
            print('error code:' + str(rlt.status_code))
            print('headers   :' + str(rlt.headers))
            print('body      :' + rlt.text)
            continue

        # collect ids
        for j, lst in enumerate(rlt_dic[key3]):
             obj_id = lst[key2]
             IDs[obj].append(urlparse(obj_id).path.split('/')[-1])

        print('  objs:' + str(len(IDs[obj])))
        print('')

        # --------------------------------
        # get object detail
        # --------------------------------
        all_obj = []
        for j, objid in enumerate(IDs[obj]):
            # query param
            desc_url = webapi_refroot + '/' + key1 + '/' + objid

            # call webapi
            rlt = inv.webapi_inventory(token, desc_url, None, 'get')

            if (rlt.status_code != httpcode_success):
                print('http request cause error')
                print('error code:' + str(rlt.status_code))
                print('headers   :' + str(rlt.headers))
                print('body      :' + rlt.text)
            
                continue

            # debug keyname
            debug_json = rlt.text
            for k, v in replace_dic.items():
                debug_json = debug_json.replace(k, v)

            # set json
            rlt_dic = json.loads(debug_json)
            all_obj.append(rlt_dic)

        # --------------------------------
        #  output json
        # --------------------------------
        jsonData = {}
        jsonData[key3] = all_obj

        print(json.dumps(jsonData, ensure_ascii=False, indent=4))
        json.dump(jsonData, f, ensure_ascii=False, indent=4)

 
    print("------------------------------")
    print("normal completion of " + __file__ + "!!!")
    etime = time.time()
    print ('total time:' + str(etime - stime))
    #sys.exit()
    

if __name__== '__main__':

    param = None
    if len(sys.argv) == 2:
        param = sys.argv[1]

    if param is None:
        param = webapi_refroot

    getInventory_main(param)






