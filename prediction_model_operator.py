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
import json
from importlib import import_module

history_db_package = None
siteid_table = {"dev-u-tokyo.mintsys.jp":2,
                "nims.mintsys.jp":11,
                "u-tokyo.mintsys.jp":1}

def writeNewSrcDstList(src_id, dst_id):
    '''
    DBができるまで、実行時ディレクトリに"predictions.ids"ファイルに予測モデルの元先リストを作成する。
    '''

    if os.path.exists("predictions.ids") is True:
        infile = open("predictions.ids")
        d = json.load(infile)
        infile.close()
    else:
        d = {}
    outfile = open("predictions.ids", "w")
    d[src_id] = dst_id
    json.dump(d, outfile, indent=4)
    outfile.close()

def io_port_transform(p2_dict, url_from, url_to, history):
    '''
    入出力ポートの記述子変更。元先リストによる予測モデルの入出力ポートの記述子IDの変更
    
    '''

    global history_db_package
    global siteid_table

    # 記述子ID変更
    if history_db_package is not None:
        print("一元管理リスト")
        d_ids = history_db_package.getInventoryData(url_from, url_to)
    else:
        print("指定されたファイル")
        infile = open(history)
        d_ids = json.load(infile)
        infile.close()

    if d_ids is None or len(d_ids) == 0:
        print("元先リスト入手に失敗しました。(from(%s)/to(%s))"%(url_from, url_to))
        sys.exit(1)
    # 出力ポートの記述子
    for port in p2_dict["output_ports"]:
        port_d_id = port["descriptor_id"].split("/")[-1]
        for h_d_id in d_ids:
            if port_d_id == h_d_id:
                port["descriptor_id"] = "http://mintsys.jp/inventory/descriptors/%s"%d_ids[h_d_id]
        # メタデータ
        for item in port['metadata_list']:
            if ("meta_id" in item) is True:
                if item["meta_id"] is None:
                    continue
                item["meta_id"] = "MD" + "%05d"%siteid_table[url_to] + item["meta_id"][7:]
        # タグリスト
        for item in port['tag_list']:
            if ("tag_tree_id" in item) is True:
                item["tag_tree_id"] = "TT" + "%05d"%siteid_table[url_to] + item["tag_tree_id"][7:]
            if ("tag_id" in item) is True:
                item["tag_id"] = "TG" + "%05d"%siteid_table[url_to] + item["tag_id"][7:]
    # 入力ポートの記述子
    for port in p2_dict["input_ports"]:
        port_d_id = port["descriptor_id"].split("/")[-1]
        for h_d_id in d_ids:
            if port_d_id == h_d_id:
                port["descriptor_id"] = "http://mintsys.jp/inventory/descriptors/%s"%d_ids[h_d_id]
        # メタデータ
        for item in port['metadata_list']:
            if ("meta_id" in item) is True:
                if item["meta_id"] is None:
                    continue
                item["meta_id"] = "MD" + "%05d"%siteid_table[url_to] + item["meta_id"][7:]
        # タグリスト
        for item in port['tag_list']:
            if ("tag_tree_id" in item) is True:
                item["tag_tree_id"] = "TT" + "%05d"%siteid_table[url_to] + item["tag_tree_id"][7:]
            if ("tag_id" in item) is True:
                item["tag_id"] = "TG" + "%05d"%siteid_table[url_to] + item["tag_id"][7:]
    # メタデータ
    for item in p2_dict["metadata_list"]:
        if ("meta_id" in item) is True:
            if item["meta_id"] is None:
                continue
            item["meta_id"] = "MD" + "%05d"%siteid_table[url_to] + item["meta_id"][7:]

    return p2_dict

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
    @retval (json), token(string)
    '''

    if token is None:
        uid, token = openam_operator.miLogin(hostname, "予測モデルを取得する側のログイン情報入力")

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

    return prediction, token

def prediction_copy(prediction, hostname, token=None):
    '''
    予測モデル複製
    コピー元、コピー先サイトが同じ場合はこちらを使用する。違う場合は、prediction_updateを使用する。
    '''

    new_prediction = prediction_add_model_type_code(prediction, version=6)

    if token is None:
        uid, token = openam_operator.miLogin(hostname, "予測モデルを複製する側のログイン情報入力")
    
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

    srcId = prediction["prediction_model_id"].split("/")[-1]
    newId = ret.json()["prediction_model_id"].split("/")[-1]

    # 元IDと複製した先IDをリスト保存
    writeNewSrcDstList(srcId, newId)

def prediction_update(p1_dict, p2_dict, url_from, url_to, history, token=None, mode="update"):
    '''
    予測モデル更新
    予測モデル更新の他、違うサイトへの複製もこちらを使用する。
    @param p1_dict : 更新元の予測モデル詳細辞書
    @param p2_dict : 更新先の予測モデル詳細辞書
    '''

    if token is None:
        uid, token = openam_operator.miLogin(url_to, "予測モデルを更新する側のログイン情報入力")
    
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    # 更新先予測モデルID
    dst_p_id = p2_dict["prediction_model_id"].split("/")[-1]
    # 更新元予測モデルID
    src_p_id = p1_dict["prediction_model_id"].split("/")[-1]

    # 更新先のキーと同じ更新元のキーの内容を更新先へコピー
    for key in p2_dict:
        if (key in p1_dict) is True:
            p2_dict[key] = p1_dict[key]

    p2_dict = io_port_transform(p2_dict, url_from, url_to, history)

    session = requests.Session()
    if mode == "copy":
        url = "https://%s:50443/inventory-update-api/v6/prediction-models"%url_to
        #print(url)
        ret = session.post(url, headers=headers, json=p2_dict)
    else:
        url = "https://%s:50443/inventory-update-api/v6/prediction-models/%s"%(url_to, dst_p_id)
        #print(url)
        ret = session.put(url, headers=headers, json=p2_dict)

    if ret.status_code == 200 or ret.status_code == 201:
        if mode == "copy":
            new_id = ret.json()["prediction_model_id"].split("/")[-1]
            print("予測モデル(%s)を複製しました。"%new_id)
        else:
            print("予測モデル(%s)を更新しました。"%dst_p_id)
    else:
        if mode == "copy":
            print("予測モデル(%s)の複製に失敗しました"%src_p_id)
        else:
            print(str(p2_dict))
            print("予測モデル(%s)の更新に失敗しました"%dst_p_id)
        print(url)
        print(ret.json())
        sys.exit(1)

    # 元IDと複製した先IDをリスト保存
    writeNewSrcDstList(src_p_id, dst_p_id)

def prediction_add_discriptor(prediction, p_id, hostname, token=None):
    '''
    記述子追加
    '''

    if token is None:
        uid, token = openam_operator.miLogin(hostname, "予測モデルを編集する側のログイン情報入力")

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

    global history_db_package

    url_from = None
    url_to = None
    p_id = None
    p_id_dest = None
    mode = None
    token_from = None
    token_to = None
    history_file = None
    history_db = None
    print_help = False
    for item in sys.argv:
        item = item.split(":")
        if item[0] == "misystem_from":
            url_from = item[1]
        if item[0] == "misystem_to":
            url_to = item[1]
        if item[0] == "prediction_id":
            p_id = item[1]
        if item[0] == "prediction_id_to":
            p_id_dest = item[1]
        if item[0] == "mode":
            mode = item[1]
        if item[0] == "token_from":
            token_from = item[1]
        if item[0] == "token_to":
            token_to = item[1]
        if item[0] == "history":
            history_file = item[1]
        if item[0] == "history_db":
            history_db = item[1]
        if item[0] == "help":
            print_help = True

    if mode is None:
        print("モードを指定してください。")
        print_help = True
    if mode == "copy" and url_to is not None:
        if history_db is not None:
            package_file_name = os.path.join(history_db, "inventory_ids.py")
            if os.path.exists(package_file_name) is False:
                print("元先一元管理プログラムがありません。(%s)"%package_file_name)
                print_help = True
            else:
                sys.path.append(history_db)
                history_db_package = import_module("inventory_ids")
                history_db_package.setDbDirectory(history_db)
    elif mode == "copy" or mode == "get" or mode == "add_desc":
        if url_from is None or p_id is None:
            if p_id is None:
                print("予測モデルIDを指定してください。")
                print_help = True
            elif url_from is None:
                print("サイトURL(from)を指定してください。")
                print_help = True
    elif mode == "update":
        if p_id is None:
            print("更新元の予測モデルIDを指定してください。")
            print_help = True
        if p_id_dest is None:
            print("更新先の予測モデルIDを指定してください。")
            print_help = True
        if history_file is None and history_db is None:
            print("履歴ファイルまたは履歴DB情報がありません。")
            print_help = True
        elif history_file is not None:
            if os.path.exists(history_file) is False:
                print("記述子履歴ファイル(%s)がありません。"%history_file)
                print_help = True
        elif history_db is not None:
            package_file_name = os.path.join(history_db, "inventory_ids.py")
            if os.path.exists(package_file_name) is False:
                print("元先一元管理プログラムがありません。(%s)"%package_file_name)
                print_help = True
            else:
                sys.path.append(history_db)
                history_db_package = import_module("inventory_ids")
                history_db_package.setDbDirectory(history_db)
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
        print(" mode : 共通")
        print("     misystem_from : 複製元の環境指定（e.g. dev-u-tokyo.mintsys.jp）")
        print("     token_from    : 複製元のAPIトークン（無い場合、ログインプロンプト）")
        print("     prediction_id : 複製したい予測モデルID（e.g. M000020000031477）")
        print(" mode : copy/update")
        print("     misystem_to   : 複製先の環境指定（指定がない場合は、同環境内で複製")
        print("     token_to      : 複製先のAPIトークン（同上）")
        print("  prediction_id_to : 更新先予測モデルID(e.g. M000020000031477) ")
        print("     history       : 複製元と複製先のIDテーブル出力ファイル名")
        print("       or")
        print("     history_db    : misrc_inventory_managementプロジェクトの絶対パス")
        sys.exit(1)

    if mode == "copy":
        print("%s から %s へ %s の予測モデルを複製します。"%(url_from, url_to, p_id))
        p_dict, token = prediction_get(url_from, p_id, token_from)
        if url_to is None and token_to is None:
            # 同じサイトへの複製
            url_to = url_from
            token_to = token_from
            prediction_copy(p_dict, url_to, token_to)
        else:
            # 違うサイトへの複製
            p2_dict = p_dict
            prediction_update(p_dict, p2_dict, url_from, url_to, history_file, token_to, mode="copy")
    elif mode == "get":
        p_dict, token = prediction_get(url_from, p_id, token_from)
    elif mode == "add_desc":
        p_dict, token = prediction_get(url_from, p_id, token_from)
        prediction_add_discriptor(p_dict, p_id, url_from, token_from)
    elif mode == "update":
        # 更新元の情報取得
        p1_dict, token = prediction_get(url_from, p_id, token_from)
        if url_to is None and token_to is None:
            url_to = url_from
            token_to = token_from
        # 更新先の情報取得
        p2_dict, token_to = prediction_get(url_to, p_id_dest, token_to)
        # 更新
        prediction_update(p1_dict, p2_dict, url_from, url_to, history_file, token_to, mode="update")

if __name__ == '__main__':
    main()

