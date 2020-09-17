#!python3.6
# -*- coding: utf-8 -*-
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.

'''
予測モデル操作プログラム
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

def prediction_add_model_type_code(prediction, version=5):
    '''
    予測モデルモデルタイプコードの追加(API Version5まで)
    '''

    if version != 5:
        return prediction
    # copy to
    new_prediction = {}
    new_prediction["preferred_name"] = prediction["preferred_name"]
    new_prediction["preferred_name_language"] = prediction["preferred_name_lang"]
    new_prediction["prediction_model_alias_names"] = prediction["prediction_model_names"][1:]
    new_prediction["description"] = prediction["description"]
    if ("prediction_model_type_name" in prediction) is True:
        if prediction["prediction_model_type_name"] == "理論モデル":
            new_prediction["prediction_model_type_code"] = 10
        elif prediction["prediction_model_type_name"] == "経験モデル":
            new_prediction["prediction_model_type_code"] = 20
        else:
            new_prediction["prediction_model_type_code"] = 30
    new_prediction["input_ports"] = prediction["input_ports"]
    new_prediction["output_ports"] = prediction["output_ports"]
    new_prediction["metadata_list"] = prediction["metadata_list"]

    return new_prediction

def prediction_get(hostname, p_id, token=None):
    '''
    予測モデルの詳細を取得する
    @param hostname (string)
    @param p_id (string)
    @retval json 
    '''

    if token is None:
        uid, token = auth_info(hostname, "予測モデルを取得する側のログイン情報入力")

    session = requests.Session()
    url = "https://%s:50443/inventory-api/v6/prediction-models/%s"%(hostname, p_id)
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    ret = session.get(url, headers=headers)
    if ret.status_code != 500:
        print("%s の予測モデルの詳細情報を取得しました"%p_id)
        #print(json.dumps(ret.json(), indent=2))
        pass
    else:
        print(ret.text)
        sys.exit(1)

    prediction = ret.json()
    outfile = open("prediction-%s.json"%p_id, "w")
    json.dump(ret.json(), outfile, indent=2, ensure_ascii=False)
    outfile.close()

    return prediction, headers

def prediction_copy(prediction, hostname, token=None):
    '''
    予測モデル複製
    '''

    new_prediction = prediction_add_model_type_code(prediction, version=6)

    if token is None:
        uid, token = auth_info(hostname, "予測モデルを複製する側のログイン情報入力")
    
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    session = requests.Session()
    url = "https://%s:50443/inventory-update-api/v6/prediction-models"%hostname
    #print(url)
    ret = session.post(url, headers=headers, json=new_prediction)
    if ret.status_code != 500:
        print(ret.json())

def prediction_update(p1_dict, p2_dict, hostname, history, token=None):
    '''
    予測モデル更新
    @param p1_dict : 更新元の予測モデル詳細辞書
    @param p2_dict : 更新先の予測モデル詳細辞書
    '''

    if token is None:
        uid, token = auth_info(hostname, "予測モデルを更新する側のログイン情報入力")
    
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    # 更新する予測モデルID
    p_id = p2_dict["prediction_model_id"].split("/")[-1]

    # 更新先のキーと同じ更新元のキーの内容を更新先へコピー
    for key in p2_dict:
        if (key in p1_dict) is True:
            p2_dict[key] = p1_dict[key]

    # 記述子ID変更
    infile = open(history)
    d_ids = json.load(infile)
    infile.close()

    # 出力ポートの記述子
    for port in p2_dict["output_ports"]:
        port_d_id = port["descriptor_id"].split("/")[-1]
        for h_d_id in d_ids:
            if port_d_id == h_d_id:
                port["descriptor_id"] = "http://mintsys.jp/inventory/descriptors/%s"%d_ids[h_d_id]
    # 入力ポートの記述子
    for port in p2_dict["input_ports"]:
        port_d_id = port["descriptor_id"].split("/")[-1]
        for h_d_id in d_ids:
            if port_d_id == h_d_id:
                port["descriptor_id"] = "http://mintsys.jp/inventory/descriptors/%s"%d_ids[h_d_id]
    # メタデータ
    # タグリスト


    session = requests.Session()
    url = "https://%s:50443/inventory-update-api/v6/prediction-models/%s"%(hostname, p_id)
    #print(url)
    ret = session.put(url, headers=headers, json=ps_dict)
    if ret.status_code != 500:
        print(ret.json())

def prediction_add_discriptor(prediction, p_id, hostname, token=None):
    '''
    記述子追加
    '''

    if token is None:
        uid, token = auth_info(hostname, "予測モデルを編集する側のログイン情報入力")

    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    session = requests.Session()
    while True:
        print("追加する記述子IDの入力")
        if sys.version_info[0] <= 2:
            d_id = raw_input("記述子ID: ")
        else:
            d_id = input("記述子ID: ")
    
        if d_id == "":
            print("予測モデルを変更して終了します。")
            break
        if d_id == "end":
            print("予測モデルを変更せずに終了します。")
            return
    
        if d_id.startswith("D") is False:
            print("記述子のフォーマットが違います。Dxxxxxyyyyyyyyyy(%s)"%d_id)
            continue

        url = "https://%s:50443/inventory-api/v6/descriptors/%s"%(hostname, d_id)
        ret = session.get(url, headers=headers)
        if ret.status_code != 200:
            print("記述子取得失敗")
            print(ret.text)
            continue
        print("記述子名(%s):%s"%(d_id, ret.json()["preferred_name"]))
        if sys.version_info[0] <= 2:
            io = raw_input("to input(1) / to output(2): ")
        else:
            io = input("to input(1) / to output(2): ")
        if io != "1" and io != "2":
            continue

        new_port = {}
        new_port["port_name"] = ret.json()["preferred_name"]
        new_port["required"] = "true"
        new_port["descriptor_id"] = ret.json()["descriptor_id"]
        new_port["description"] = ret.json()["description"]
        new_port["tag_list"] = []
        new_port["metadata_list"] = []

        if io == "1":
            is_same = False
            for item in prediction["input_ports"]:
                if item["port_name"] == ret.json()["preferred_name"]:
                    is_same = True
            if is_same is True:
                print("ポート名(%s) はすでに入力ポートに登録があります。"%ret.json()["preferred_name"])
                continue
            prediction["input_ports"].append(new_port)
        else:
            is_same = False
            for item in prediction["output_ports"]:
                if item["port_name"] == ret.json()["preferred_name"]:
                    is_same = True
            if is_same is True:
                print("ポート名(%s) はすでに出力ポートに登録があります。"%ret.json()["preferred_name"])
                continue
            prediction["output_ports"].append(new_port)

    url = "https://%s:50443/inventory-update-api/v6/prediction-models/%s"%(hostname, p_id)
    ret = session.put(url, headers=headers, json=prediction)

    outfile = open("prediction-%s.json"%p_id, "w")
    json.dump(prediction, outfile, indent=2, ensure_ascii=False)
    outfile.close()

    if ret.status_code != 200 and ret.status_code != 201:
        print("変更に失敗しました。")
        print(ret.text)
        return
    else:
        print(ret.text)
        
def main():
    '''
    開始点
    '''

    url_from = None
    url_to = None
    p_id = None
    p_id_dest = None
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
        if item[0] == "prediction_id":
            d_id = item[1]
        if item[0] == "prediction_id_to":
            d_id_dest = item[1]
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
    if mode == "copy" or mode == "get" or mode == "add_desc":
        if url_from is None or d_id is None:
            if d_id is None:
                print("予測モデルIDを指定してください。")
                print_help = True
            elif url_from is None:
                print("サイトURL(from)を指定してください。")
                print_help = True
    elif mode == "update":
        if d_id is None:
            print("更新元の予測モデルIDを指定してください。")
            print_help = True
        if d_id_dest is None:
            print("更新先の予測モデルIDを指定してください。")
            print_help = True
        if history_file is not None:
            if os.path.exists(history_file) is False:
                print("記述子履歴ファイル(%s)がありません。"%history_file)
                print_help = True
        else:
            print("記述子履歴ファイルを指定してください")
            print_help = True
    else:
        print("不明なモード指定です(%s)"%mode)
        print_help = True

    if print_help is True:
        print("")
        print("予測モデル複製プログラム")
        print("Usage:")
        print("$ python3.6 %s [options]"%(sys.argv[0]))
        print("  Options:")
        print("")
        print("     mode          : copy 記述子複製を実行する")
        print("                   : get 記述子取得のみを実行する")
        print("                   : add_desc 入出力ポートを連続で登録する。")
        print("                   : update 複製後のアップデートを行う 要記述子履歴ファイル")
        print("     misystem_from : 複製元の環境指定（e.g. dev-u-tokyo.mintsys.jp）")
        print("     misystem_to   : 複製先の環境指定（指定がない場合は、同環境内で複製")
        print("     token_from    : 複製元のAPIトークン（無い場合、ログインプロンプト）")
        print("     token_to      : 複製先のAPIトークン（同上）")
        print("     prediction_id : 複製したい予測モデルID（e.g. M000020000031477）")
        print("  prediction_id_to : 更新先予測モデルID(e.g. M000020000031477) ")
        print("     history       : 複製元と複製先のIDテーブル出力ファイル名）")
        sys.exit(1)

    if mode == "copy":
        p_dict, h = prediction_get(url_from, p_id, token_from)
        if url_to is None and token_to is None:
            url_to = url_from
            token_to = token_from
        prediction_copy(p_dict, url_to, token_to)
    elif mode == "get":
        p_dict, h = prediction_get(url_from, p_id, token_from)
    elif mode == "add_desc":
        p_dict, h = prediction_get(url_from, p_id, token_from)
        prediction_add_discriptor(p_dict, p_id, url_from, token)
    elif mode == "update":
        # 更新元の情報取得
        p1_dict, h = prediction_get(url_from, p_id, token_from)
        if url_to is None and token_to is None:
            url_to = url_from
            token_to = token_from
        # 更新先の情報取得
        p2_dict, h = prediction_get(url_from, p_id_dest, token_from)
        # 更新
        prediction_update(p1_dict, p2_dict, url_to, history_file, token_to)

if __name__ == '__main__':
    main()

