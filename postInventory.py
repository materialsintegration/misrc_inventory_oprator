# -*- coding: utf-8 -*-

# ****************************************************
# * postInventory2.py
# *
# *    write inventory descriptors
# *
# *  2018/06/11  T.Noguchi  create
# *
# ****************************************************

import os
import sys
import ast
#import configparser
import requests
import json
import codecs
import time
#from urllib.parse import urlparse
if sys.version_info[0] <= 2:
    import ConfigParser
    from urlparse import urlparse
else:
    import configparser
    from urllib.parse import urlparse

import module_inventory as inv

# =======================================
# config
# =======================================
webapi_refroot = 'https://nims.mintsys.jp:50443/inventory-api/v3'
webapi_updroot = 'https://nims.mintsys.jp:50443/inventory-update-api/v3'
#ifile = 'inventory_out_test.json'
#ofile = 'inventory_out.json'
mod_outf = 'modules_new.xml'

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
        {'name': 'modules.xml','type': str,  'required': True},
    ],
}

# replace json
replace_dic = {'preferred_name_lang': 'preferred_name_language', \
               'descriptor_names': 'descriptor_alias_names'}

# codec
codec = 'utf-8'

# response code
httpcode_success = 201

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

def postInventory_main(webapi_updroot):
    stime = time.time()
    print('----- start postInventory script -----')    

    # init

    # ///////////////////////////////
    # read config file
    # ///////////////////////////////   
    config = None
    config = configParse(conf_file)

    uid     = config['authorize']['user_id']
    token   = config['authorize']['token']
    url     = config['resource']['url']
    query   = config['resource']['query']
    lst     = config['file']['object']
    objs    = lst.split('\n')
    lst     = config['file']['inputfile']
    ifiles  = lst.split('\n')
    lst     = config['file']['outputfile']
    ofiles  = lst.split('\n')
    modules = config['file']['modules.xml']

    print('[conf file]')
    print('url         : ' + url)
    print('query       : ' + query)
    print('object      : ' + ', '.join(objs))
    print('input file  : ' + ', '.join(ifiles))
    print('output file : ' + ', '.join(ofiles))
    print('modules.xml : ' + modules)
    print('---------------------------------')

    # ///////////////////////////////
    # load resource
    # ///////////////////////////////
    print('load resource...')

    jsonData = []
    for i, obj in enumerate(objs):
        key1 = obj + 's'                     # descriptors
        key2 = obj.replace('-', '_') + '_id' # descriptor_id
        key3 = obj.replace('-', '_') + 's'   # prediction_models        

        # input file
        f = open(ifiles[i], 'r')

        # replace dickey for output
        txt = f.read()
        for k, v in replace_dic.items():
            txt_replace = txt.replace(k, v)

        jsonData.append(json.loads(txt_replace))

        f.close()

    print(json.dumps(jsonData, ensure_ascii=False, indent=4))
    print('---------------------------------')

    # ///////////////////////////////
    # update webapi
    # ///////////////////////////////
    print('update resource...')

    jstat = {}
    oldIDs = []
    newIDs = []
    for i, obj in enumerate(objs):
        # keyword set
        key1 = obj + 's'                     # descriptors
        key2 = obj.replace('-', '_') + '_id' # descriptor_id
        key3 = obj.replace('-', '_') + 's'   # prediction_models

        if (key3 not in jsonData[i]):
            continue

        print('[target : ' + obj + ']')

        dest_url = webapi_updroot + '/' + url + '/' + key1
        jstat[obj] = []
        for j, lst in enumerate(jsonData[i][key3]):
            # get old id
            json_old = jsonData[i][key3][j]
            if (key2 not in json_old):
                continue
            uri = json_old[key2]
            oldid = urlparse(uri).path.split('/')[-1]

            # call webapi updater
            rlt     = inv.webapi_inventory(token, dest_url, lst, 'post')
            rlt_dic = ast.literal_eval(rlt.text)

            # result
            jstat[obj].append(rlt.status_code)
            for k, v in rlt_dic.items():
                if (key2 in k):
                    oldIDs.append(oldid)
                    newIDs.append(urlparse(v).path.split('/')[-1])
                    break

            # show result
            if (rlt.status_code == httpcode_success):
                msg = '  ({0:0<2}): {1} - {2}'.format(j, \
                    jstat[obj][j], newIDs[-1])
            else:
                msg = '  ({0:0<2}): {1} - {2}'.format(j, \
                    jstat[obj][j], rlt.text)
            print(msg)

    print('---------------------------------')

    # ///////////////////////////////
    # make modules.xml
    # ///////////////////////////////
    print('make modules.xml...')

    # read xml
    f = open(modules, 'r')
    base_xml = f.read()
    f.close()

    # replace old-new id
    new_xml = base_xml
    for idx in range(0, len(oldIDs)):
        new_xml = new_xml.replace(oldIDs[idx], newIDs[idx])

    # output new xml
    f = open(mod_outf, 'w')
    f.write(new_xml)
    f.close()


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
        param = webapi_updroot
    postInventory_main(param)

