#!python3.6
# -*- coding: utf-8 -*-
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.

'''
記述子操作プログラム
'''

import requests
import sys, os
from openam_operator import openam_operator
from getpass import getpass
import json

def auth_info(hostname, message):
    '''
    ログイン
    '''

    #print("記述子を登録する側のログイン情報入力")
    print(message)
    if sys.version_info[0] <= 2:
        name = raw_input("ログインID: ")
    else:
        name = input("ログインID: ")
    password = getpass("パスワード: ")

    ret, uid, token = openam_operator.miauth(hostname, name, password)
    if ret is False:
        if uid.status_code == 401:
            print(uid.json()["message"])
        sys.exit(1)

    return uid, token

def descriptor_get(hostname, d_id, token=None):
    '''
    記述子の詳細を取得する
    @param hostname (string)
    @param d_id (string)
    @retval json 
    '''

    if token is None:
        uid, token = auth_info(hostname, "記述子取得する側のログイン情報入力")

    session = requests.Session()
    url = "https://%s:50443/inventory-api/v6/descriptors/%s"%(hostname, d_id)
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    ret = session.get(url, headers=headers)
    if ret.status_code == 200 or ret.status_code == 201:
        print("ID(%s) の記述子の詳細情報を取得しました"%d_id)
        #print(json.dumps(ret.json(), indent=2))
        pass
    else:
        print("url = %s"%url)
        print(ret.text)
        sys.exit(1)

    if ret.status_code == 200 or ret.status_code == 201:
        descriptor = ret.json()
        outfile = open("descriptor-%s.json"%d_id, "w")
        json.dump(ret.json(), outfile, indent=2, ensure_ascii=False)
        outfile.close()
    else:
        print(ret.text)
        sys.exit(1)

    return descriptor, headers

def descriptor_copy(descriptor, hostname, token=None, history=None):
    '''
    記述子複製
    '''

    if token is None:
        uid, token = auth_info(hostname, "記述子を複製する側のログイン情報入力")

    session = requests.Session()
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    url = "https://%s:50443/inventory-update-api/v6/descriptors"%hostname
    #print(url)
    ret = session.post(url, headers=headers, json=descriptor)
    if ret.status_code == 200 or ret.status_code == 201:
        print(ret.json())
    else:
        print(ret.text)
        sys.exit(1)

    descriptor_id_before = descriptor["descriptor_id"].split("/")[-1]
    descriptor_id_after = ret.json()["descriptor_id"].split("/")[-1]

    if history is None:
        if os.path.exists("descriptors.ids") is True:
            infile = open("descriptors.ids")
            d = json.load(infile)
            infile.close()
        else:
            d = {}
        outfile = open("descriptors.ids", "w")
    else:
        if os.path.exists(history) is True:
            infile = open(history)
            d = json.load(infile)
            infile.close()
        else:
            d = {}
        outfile = open(history, "w")
    d[descriptor_id_before] = descriptor_id_after
    json.dump(d, outfile, indent=4)
    outfile.close()

def descriptor_update(descriptor, update_descriptor_id, hostname, token=None):
    '''
    記述子複製
    '''

    if token is None:
        uid, token = auth_info(hostname, "記述子を更新する側のログイン情報入力")

    session = requests.Session()
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    # 更新される側の詳細取得
    url = "https://%s:50443/inventory-api/v6/descriptors/%s"%(hostname, update_descriptor_id)
    ret = session.get(url, headers=headers, json=descriptor)
    if ret.status_code == 200 or ret.status_code == 201:
        #print(ret.json())
        pass
    else:
        print(url)
        print(ret.text)
        sys.exit(1)
    
    d_dict = ret.json()

    for item in d_dict:
        if (item in descriptor) is True:
            d_dict[item] = descriptor[item]

    url = "https://%s:50443/inventory-update-api/v6/descriptors/%s"%(hostname, update_descriptor_id)
    ret = session.put(url, headers=headers, json=descriptor)
    if ret.status_code == 200 or ret.status_code == 201:
        print("記述子(%s) を更新しました。"%update_descriptor_id)
        pass
    else:
        print(url)
        print(ret.text)
        sys.exit(1)
    
def main():
    '''
    開始点
    '''

    url_from = None
    url_to = None
    d_id = None
    mode = None
    token_from = None
    token_to = None
    history_file = None
    print_help = False
    for item in sys.argv:
        item = item.split(":")
        if item[0] == "misystem_from":
            url_from = item[1]
        if item[0] == "misystem_to":
            url_to = item[1]
        if item[0] == "descriptor_id":
            d_id = item[1]
        if item[0] == "mode":
            mode = item[1]
        if item[0] == "token_from":
            token_from = item[1]
        if item[0] == "token_to":
            token_to = item[1]
        if item[0] == "history":
            history_file = item[1]
        if item[0] == "help":
            print_help = True

    if mode is None:
        print("モードを指定してください。")
        print_help = True
    if mode == "copy" or mode == "get":
        if url_from is None or d_id is None or mode is None:
            if d_id is None:
                print("記述子IDを指定してください。")
                print_help = True
            elif url_from is None:
                print("サイトURL(from)を指定してください。")
                print_help = True
    elif mode == "update":
        if history_file is not None:
            if os.path.exists(history_file) is False:
                print("履歴ファイル(%s)がありません。"%history_file)
                print_help = True
        else:
            print("履歴ファイルを指定してください")
            print_help = True
    else:
        print("不明なモード指定です(%s)"%mode)
        print_help = True

    if print_help is True:
        print("")
        print("記述子複製プログラム")
        print("Usage:")
        print("$ python3.6 %s [options]"%(sys.argv[0]))
        print("  Options:")
        print("")
        print("     mode          : copy 記述子複製を実行する")
        print("                   : get 記述子取得のみを実行する")
        print("                   : update history指定のファイルから複製後のアップデートを行う")
        print("     misystem_from : 複製元の環境指定（e.g. dev-u-tokyo.mintsys.jp）")
        print("     misystem_to   : 複製先の環境指定（指定がない場合は、同環境内で複製")
        print("     token_from    : 複製元のAPIトークン（無い場合、ログインプロンプト）")
        print("     token_to      : 複製先のAPIトークン（同上）")
        print("     descriptor_id : 複製したい記述子ID（e.g. D000020000031477）")
        print("     history       : 複製元と複製先のIDテーブル出力ファイル名）")
        sys.exit(1)

    if mode == "copy":
        d_dict, h = descriptor_get(url_from, d_id, token_from)
        if url_to is None and token_to is None:
            url_to = url_from
            token_to = token_from
        descriptor_copy(d_dict, url_to, token_to, history_file)
    elif mode == "get":
        d_dict, h = descriptor_get(hostname, d_id, token)
    elif mode == "update":
        infile = open(history_file)
        d_dict = json.load(infile)
        for d_id in d_dict:
            d_info, h = descriptor_get(url_from, d_id, token_from)
            descriptor_update(d_info, d_dict[d_id], url_to, token_to)
    else:
        print("misyste:%s / descriptor_id:%s / mode:%s"%(hostname, d_id, mode))

if __name__ == '__main__':
    main()

