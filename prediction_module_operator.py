#!/usr/local/python2.7/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.

'''
modules.xmlを読み込み、指定されたIDのモジュール(複数可)を出力および指定されたmodules.xmlファイルをアセットAPIを使用してMIntシステムへ送り込む
一般的な編集機能はmisrc_prediction_editorに実装予定
'''

#from prediction_module_editor_gui import *
import sys, os
import xml.etree.ElementTree as ET
import datetime
if os.name == "nt":
    import openam_operator
else:
    from openam_operator import openam_operator     # MIシステム認証ライブラリ
#from openam_operator import openam_operator
from getpass import getpass
import json
import requests
from importlib import import_module
import pprint

history_db_package = None
siteid_table = {"dev-u-tokyo.mintsys.jp":2,
                "nims-dev.mintsys.jp":2,
                "nims.mintsys.jp":11,
                "u-tokyo.mintsys.jp":1,
                "sre.mintsys.jp":6}
api_version = {"dev-u-tokyo.mintsys.jp":"v1",
                "nims.mintsys.jp":"v3",
                "nims-dev.mintsys.jp":"v2",
                "u-tokyo.mintsys.jp":"v1",
                "sre.mintsys.jp":"v1"}

def getAllModulesViaAPI(hostname, token, allmodule_name="modules-all.xml"):
    '''
    APIを使用して登録済み削除済みを除く全予測モジュールを取り出す。
    @param hostname(string) MIntシステムサーバー名
    @param token(string)
    @param allmodule_name(string) 取り出した後のファイル名
    '''

    #print("予測モデルを取得する側のログイン情報入力")
    #if sys.version_info[0] <= 2:
    #    name = raw_input("ログインID: ")
    #else:
    #    name = input("ログインID: ")
    #password = getpass("パスワード: ")

    #ret, uid, token = openam_operator.miauth(hostname, name, password)
    #print(token)
    #uid, token = openam_operator.miLogin(hostname, "MIシステム管理者(%s)のログイン情報"%hostname)
    session = requests.Session()
    url = "https://%s:50443/asset-api/%s/prediction-modules"%(hostname, api_version[hostname])
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    ret = session.get(url, headers=headers)

    if ret.status_code == 200:
        print("全予測モジュール情報を取得しました")
        #print(json.dumps(ret.json(), indent=2))
    else:
        print(ret.text)
        #sys.exit(1)
        return False

    #prediction = ret.json()
    outfile = open(allmodule_name, "w")
    #outfile.write(json.dumps(prediction, indent=2, ensure_ascii=False))
    outfile.write(ret.text)
    outfile.close()
    return True

def getModules(modules_filename, predictions, ident_nodelete=False, version=None):
    '''
    XMLから指定のモジュールを切り出す。
    '''

    if os.path.exists(modules_filename) is False:
        print("cannot find module files(%s)"%modules_filename)
    if modules_filename[0] == "~":
        home_dir = os.path.expanduser("~")
        modules_filename = os.path.join(home_dir, modules_filename[2:])
    
    et = ET.parse(modules_filename)
    docroot = et.getroot()
    #print(docroot.tag)
    candidate_modules = {}
    for prediction_id in predictions:
        candidate_modules[prediction_id] = []
        for item in docroot:
            #print(item.tag)
            subelem = item.find(".//dc:identifier", {'dc': 'http://purl.org/dc/elements/1.1/'})
            if subelem is None:
                # idefitifieが無い場合対象外とする
                continue
            if subelem.text != prediction_id:
                # 指定したIDと違う物は対象外とする
                continue
            subelem = item.find(".//predictionModuleSchema:version", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
            if subelem is None:
                # versionが無い場合対象外とする
                continue
    
            candidate_modules[prediction_id].append(item)
        if len(candidate_modules[prediction_id]) == 0:
            print("予測モジュールid(%s)は登録がありませんでした。"%prediction_id)
    
    #for item in candidate_modules:
    #    print("対象ID(%s)の候補数：%d"%(item, len(candidate_modules[item])))
    #print(len(candidate_modules))
    for prediction_id in candidate_modules:
        rev = 0
        minor = 0
        major = 0
        target_modules = []
        if len(candidate_modules[prediction_id]) != 0:
            for item in candidate_modules[prediction_id]:
                #全elementを見るために
                #for element in item.iter():
                #    print("%s - %s"%(element.tag, element.text))
                #print(item.tag)
                subelem = item.find(".//predictionModuleSchema:version", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
                v1 = int(subelem.text.split(".")[0])
                v2 = int(subelem.text.split(".")[1])
                v3 = int(subelem.text.split(".")[2])
                if v1 >= major or v2 >= minor or v3 >= rev:
                    target_module = item
                    major = v1
                    minor = v2
                    rev = v3
                target_modules.append(target_module)
    
            #root = ET.Element("modules", {"xmlns":"http://www.example.com/predictionModuleSchema", "xsi:schemaLocation":"http://www.example.com/predictionModuleSchema predictionModuleSchema.xsd"})
            #print("%d.%d.%d"%(major, minor, rev))
            root = ET.Element("modules")
            for element in target_modules:
                version_element = element.find(".//predictionModuleSchema:version", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
                v1 = int(version_element.text.split(".")[0])
                v2 = int(version_element.text.split(".")[1])
                v3 = int(version_element.text.split(".")[2])
                if version is not None:                 # バージョン指定があった場合
                    if v1 == version[0] and v2 == version[1] and v3 == version[2]:
                        pass
                    else:
                        continue
                else:
                    if v1 == major and v2 == minor and v3 == rev:
                        pass
                    else:
                        continue
                    
                if ident_nodelete is False:
                    sube = element.find(".//dc:identifier", {'dc': 'http://purl.org/dc/elements/1.1/'})
                    element.remove(sube)
                    #sube = element.find(".//predictionModuleSchema:version", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
                    version_element.text = "1.0.0"
                root.append(element)
         
            new_tree = ET.ElementTree(element=root)
         
            ET.register_namespace("", "http://www.example.com/predictionModuleSchema")
            #new_tree.write("prediction_modules.xml", xml_declaration=True, encoding='UTF-8')
            new_tree.write("prediction-%s.xml"%prediction_id, xml_declaration=True, encoding='UTF-8')
            print("指定されたID(%s)の予測モジュールを prediction-%s.xml というファイル名で出力しました。"%(prediction_id, prediction_id))
        else:
            print("指定されたID(%s)の予測モジュールは登録が無かったのでファイルとして出力しませんでした。"%prediction_id)


def checkID(misystem_from, misystem_to, filename):
    '''
    元先IDのデータベースから、予測モデルID、記述子IDの変換を行う。
    @param misystem_from (string)
    @param misystem_to (string)
    @param filename 予測モジュール名１つ
    @retval 問題なければ、document(Element)。失敗すればFalseが返る。
    '''

    global history_db_package
    # 予測モデルの元先リスト入手
    p_dict = history_db_package.getInventoryData(misystem_from, misystem_to, "prediction_model")
    # 記述子の元先リスト入手
    d_dict = history_db_package.getInventoryData(misystem_from, misystem_to)

    # 対象予測モジュールの変換
    print("予測モジュールファイル(%s)の変更"%filename)
    et = ET.parse(os.path.join(os.getcwd(), filename))
    docroot = et.getroot()
    inports = docroot.findall(".//predictionModuleSchema:inputPorts", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
    #print(len(inports))
    outports = docroot.findall(".//predictionModuleSchema:outputPorts", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
    pmodel = docroot.find(".//predictionModuleSchema:predictionModel", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
    for inport in inports:
        items = inport.findall(".//predictionModuleSchema:descriptor", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
        for item in items:
            #print("記述子(%s) ...."%item.text)
            isNoId = False
            for d_id in d_dict:
                #print("     対応記述子(%s)"%d_id)
                if item.text == d_id:
                    item.text = d_dict[d_id]
                    isNoId = True
            if isNoId is False:
                print("記述子ID(%s)の登録がありません。"%item.text)
                return False
    for inport in outports:
        items = inport.findall(".//predictionModuleSchema:descriptor", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
        for item in items:
            #print("記述子(%s) ...."%item.text)
            isNoId = False
            for d_id in d_dict:
                #print("     対応記述子(%s)"%d_id)
                if item.text == d_id:
                    item.text = d_dict[d_id]
                    isNoId = True
            if isNoId is False:
                print("記述子ID(%s)の登録がありません。"%item.text)
                return False
    isNoId = False
    for item in p_dict:
        if pmodel.text == item:
            isNoId = True
            pmodel.text = p_dict[item]
    if isNoId is False:
        print("予測モデルID(%s)の登録がありません。"%pmodel.text)
        return False

    return docroot

def importModules(misystem_from, misystem_to, modules, token):
    '''
    予測モジュールのインポートを行う。
    @param misystem_from(string)
    @param misystem_to(string)
    @param modules(list) 予測モジュールファイルのリスト
    @retval 予測モジュールIDのリスト。新規登録の場合のみ。その他は空のリスト。
    '''

    print(os.getcwd())
    if token is None:
        if misystem_from != misystem_to:
            # 別サイトへのインポートの場合
            uid, token = openam_operator.miLogin(misystem_to, "MIシステム管理者(%s)のログイン情報"%misystem_to)
        else:
            # 同じサイトへのインポート
            uid, token = openam_operator.miLogin(misystem_from, "MIシステム管理者(%s)のログイン情報"%misystem_to)
    
        if uid is None and token is None:
            print("ログイン失敗")
            sys.exit(1)

    # トークン取得とAPI準備
    session = requests.Session()
    url = "https://%s:50443/asset-api/%s/prediction-modules"%(misystem_to, api_version[misystem_to])
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    new_modules = []
    for filename in modules:

        if misystem_from != misystem_to:
            target_module = checkID(misystem_from, misystem_to, filename)

            if target_module is False:
                sys.exit(1)
            #root = ET.Element("modules", {"xmlns":"http://www.example.com/predictionModuleSchema", "xsi:schemaLocation":"http://www.example.com/predictionModuleSchema predictionModuleSchema.xsd"})
            root = ET.Element("modules")
            for element in target_module:
                sube = element.find(".//dc:identifier", {'dc': 'http://purl.org/dc/elements/1.1/'})
                if sube is not None:
                    current_id = sube.text
                    element.remove(sube)
                sube = element.find(".//predictionModuleSchema:version", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
                if sube is not None:
                    sube.text = "1.0.0"
            root.append(element)
         
            new_tree = ET.ElementTree(element=root)
     
            ET.register_namespace("", "http://www.example.com/predictionModuleSchema")
            new_tree.write("prediction_modules.xml", xml_declaration=True, encoding='UTF-8')
    
            filename = "prediction_modules.xml"
        else:
            root = ET.parse(filename)
            ident_element = root.find(".//dc:identifier", {'dc': 'http://purl.org/dc/elements/1.1/'})
            if ident_element is not None:
                current_id = ident_element.text
            else:
                current_id = ""
            prediction_model = root.find(".//predictionModuleSchema:predictionModel", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
            if prediction_model is not None:
                prediction_id = prediction_model.text
            else:
                prediction_id = ""

        #sys.exit(0)
        if current_id != "":
            print("予測モジュールファイル名（旧ID%s）をインポート中"%current_id)
        else:
            print("新規予測モジュール(予測モデルID(%s))をインポート中"%prediction_id)
        infile = open(filename, "rb")
        contents = infile.read()
        infile.close()
        ret = session.put(url, headers=headers, data=contents)
        if ret.status_code == 200:
            print("予測モジュールファイル名（%s）をインポートしました"%filename)
            if ret.text != "":
                root = ET.fromstring(ret.text)
                ident_element = root.find(".//dc:identifier", {'dc': 'http://purl.org/dc/elements/1.1/'})
                version_element = root.find(".//predictionModuleSchema:version", {"predictionModuleSchema": "http://www.example.com/predictionModuleSchema"})
                if ident_element is not None:
                    print("新規作成された予測モジュールIDは %s です。"%ident_element.text)
                    module = {"module_id":ident_element.text, "version":version_element.text}
                    new_modules.append(module)
        else:
            print(ret.text)

    return token, new_modules

def addPrivilegs(misystem_to, token, new_modules, privileges):
    '''
    権限設定
    @param misystem_to(string)
    @param token(string)
    @param new_modules(list)
    @param privileges(list)
    @retval なし
    '''

    # トークン取得とAPI準備
    session = requests.Session()
    url = "https://%s:50443/asset-api/%s/prediction-modules/permission"%(misystem_to, api_version[misystem_to])
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}

    for item in new_modules:
        contents = {}
        contents["prediction_modules"] = []
        module_uri = "http://mintsys.jp/assets/prediction-modules/%s"%item["module_id"]
        contents["prediction_modules"].append({"prediction_module_id":"%s"%module_uri, "version":"%s"%item["version"]})
        contents["user_groups"] = []
        contents["user_groups"].append({"user_group_ids":privileges, "permission":"executable"})
        pprint.pprint(contents)
        ret = session.put(url, headers=headers, json=contents)
        if ret.status_code != 200:
            print(ret.text)
            sys.exit(1)
    
def main():
    '''
    開始点
    '''

    predictions = []
    modules_filename = ""
    process_mode = ""                   # ファイルから切り出し
    ident_nodelete = False
    misystem_from = ""
    misystem_to = None
    go_help = False
    history_db = None
    privileges = None
    token = None
    version = None
    apiversion = None
    global history_db_package
    global api_version

    for item in sys.argv:
        if item == "--ident-nodelete":
            ident_nodelete = True
            continue
        items = item.split(":")
        if items[0] == "predictions":
            pmodules = items[1].split(",")
            for pmodule in pmodules:
                predictions.append(pmodule)
        elif items[0] == "mode":
            process_mode = items[1]
        elif items[0] == "modulefile":
            modules_filename = items[1]
        elif items[0] == "misystem_from":
            misystem_from = items[1]
        elif items[0] == "help":
            go_help = True
        elif items[0] == "history_db":
            history_db = items[1]
        elif items[0] == "misystem_to":
            misystem_to = items[1]
        elif items[0] == "privileges":
            privileges = items[1].split(",")
        elif items[0] == "token":
            token = items[1]
        elif items[0] == "version":
            vcheck = items[1].split(".")
            if len(vcheck) == 3:
                try:
                    version = [int(vcheck[0]), int(vcheck[1]), int(vcheck[2])]
                except:
                    print("バージョンチェック異常(%s)"%items[1])
            else:
                print("バージョンチェック異常(%s)"%items[1])
        elif items[0] == "api_version":
            apiversion = items[1]
        #else:
        #    modules_filename = item

    # APIバージョン確認
    if apiversion is not None:
        api_version[misystem_from] = apiversion
    print(str(predictions))
    print(modules_filename)
    if process_mode == "file":
        if modules_filename == "":
            go_help = True
    if process_mode == "import":
        if predictions == "":
            go_help = True
    if process_mode == "file" or process_mode == "export":
        if len(predictions) == 0:
            go_help = True

    if process_mode == "file":
        getModules(modules_filename, predictions, ident_nodelete)
    elif process_mode == "export":
        # 一旦全部取り出してから必要な編集（idenfierタグやversionタグ）を行う。
        modules_filename = "modules-all.xml"
        if token is None:
            uid, token = openam_operator.miLogin(misystem_from, "MIシステム管理者(%s)のログイン情報"%misystem_from)
            if uid is None and token is None:
                print("ログイン失敗")
                sys.exit(1)

        if getAllModulesViaAPI(misystem_from, token) is False:
            go_help = True
        else:
            getModules(modules_filename, predictions, ident_nodelete, version)
    elif process_mode == "import":
        # モジュールインポートモード
        new_modules = []
        if modules_filename != "":
            modules_filename = modules_filename.split(",")
            for pfile in modules_filename:
                # 指定されたファイルの存在チェック
                if os.path.exists(pfile) is False:
                    print("インポート対象のファイル(%s)がありません"%pfile)
                    go_help = True
        else:
            print("インポート対象のファイルの指定がありません")
            go_help = True
        if misystem_to is not None:
            if history_db is None:
                print("元先一元管理プログラムを指定してください。")
                go_help = True
            else:
                package_file_name = os.path.join(history_db, "inventory_ids.py")
                if os.path.exists(package_file_name) is False:
                    print("元先一元管理プログラムがありません。(%s)"%package_file_name)
                    go_help = True
                else:
                    sys.path.append(history_db)
                    history_db_package = import_module("inventory_ids")
                    history_db_package.setDbDirectory(history_db)
        if misystem_from is None:
            print("予測モジュールファイルの取得元サイト名がありません。")
            go_help = True
        if misystem_to is None:
            print("同じサイトへのインポートを行います。")
            misystem_to = misystem_from
        if go_help is False:
            token, new_modules = importModules(misystem_from, misystem_to, modules_filename, token)
            if privileges is not None and len(new_modules) != 0:                  # 権限設定
                addPrivilegs(misystem_to, token, new_modules, privileges)
    else:
        print("対応する動作モードがありません")
        go_help = True

    if go_help is True:
        print("")
        print("Usage python3.6 %s mode:<mode> predictions:<prediction_id>,[<prediction_id>,<prediction_id>,...] modulesfile:<modules.xml> misystem_from:サイトURL [misystem_to:サイトURL] [privileges:<user_group ID>,<user_group ID>,...] [--ident-nodelete] [version:x.y.z]"%sys.argv[0])
        print("")
        print("    予測モジュール切り出し、送り込みプログラム")
        print("    バージョン番号は、最新（各数字が最大）のもの")
        print("")
        print("予測モデル切り出し(アセットAPI使用)")
        print("             mode : export")
        print("    misystem_from : export対象のサイト名(e.g. dev-u-tokyo.mintsys.jp)")
        print("          version : export対象のバージョン（e.g. x.y.z）")
        print("      api_version : アセットAPIのバージョン指定（e.g. v3 or v4）")
        print("")
        print("予測モデル切り出し(全予測モジュールファイル使用)")
        print("             mode : file")
        print("       modulefile : asset管理画面から、exportした全予測もジュールの入ったXMLファイル。")
        print("                    predictionsで指定した予測モジュールを切り出す。")
        print("")
        print("export/file 共通")
        print("      predictions : Pで始まる予測モジュール番号。複数指定可。")
        print(" --ident-nodelete : identifierタグを削除しない。versionを1.0.0に変更しない")
        print("")
        print("予測モデル送り込み")
        print("             mode : import")
        print("       modulefile : インポートしたい予測モジュールXMLファイル。複数指定可")
        print("       history_db : misrc_inventory_managementプロジェクトの絶対パス")
        print("                    missytem_fromとmisystem_toが違う（サイト間コピー）場合必須")
        print("    misystem_from : XMLファイルを取得したサイト名(e.g. u-tokyo.mintsys.jp)")
        print("      misystem_to : インポート先のサイト名(e.g. nims.mintsys.jp)")
        print("                    インポート先のサイト名が違う（サイト間コピー）場合、history_dbに従ってインベントリを")
        print("                    変更します。history_dbに登録が無いとコピーは失敗します。")
        print("       privileges : 権限設定したいグループID。複数指定可。サイト間コピーまたは新規登録時のみ。")
        print("")  
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()

