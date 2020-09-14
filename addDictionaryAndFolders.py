#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.

'''
辞書、フォルダーの作成
'''

import sys, os
import json
from api_access import *

def addFolder(token, weburl, dict_id, folder_id, table):
    '''
    フォルダーの登録
    @param token (string)
    @param weburl (string)
    @param dict_id (string)
    @param folder_id (string)
    @param table (dict)参照系APIの辞書取得で取得した辞書の構造を簡略化したdict
    @retval dictid, folderid (stringのtuple)
    dict_idとfoler_id以下に新しくfolderを作成していく
    '''

    for item in table:
        # まずフォルダーを追加する。
        body = {"folder_name": item["folder_name"], "description": item["description"]}
        url = weburl + "/%s"%dict_id + "/folders/%s"%folder_id + "/folders"
        ret, result = apiAccess(token, url, "post", body, debug_print=True)
        if ret is True:
            new_folder = result.json()["folder_id"].split("/")[-1]
            print("Added new Folder name(%s) / ID(%s) under dictionary id(%s)"%(item["folder_name"], new_folder, dict_id))
        else:
            return False
        # 次に登録した新しいフォルダに、記述子や予測モデルを登録する。
        for descriptor in item["descriptors"]:
            body = {"descriptor_id":descriptor}
            url = weburl + "/%s"%dict_id + "/folders/%s"%new_folder + "/descriptors"
            ret, result = apiAccess(token, url, "post", body, debug_print=True)
        for prediction_model in item["prediction_models"]:
            body = {"prediction_model_id":prediction_model}
            url = weburl + "/%s"%dict_id + "/folders/%s"%new_folder + "/prediction-models"
            ret, result = apiAccess(token, url, "post", body, debug_print=True)

        # 配下にフォルダーがある場合は、再帰的に呼び出す。
        if ("folders" in item) is True:
            addFolder(token, weburl, dict_id, new_folder, item["folders"])

    return True

def addDictionary(token, weburl, name, description):
    '''
    辞書の登録
    @param token (string)
    @param weburl (string)
    @param name (string)
    @param description (string)
    @retval dictid, folderid (stringのtuple)
    '''

    body = {"dictionary_name": name, "description": description}
    result, ret = apiAccess(token, weburl, "post", body, debug_print=True)
    #print(result)
    if result is True:
        return ret.json()["dictionary_id"].split("/")[-1], ret.json()["root_folder_id"].split("/")[-1]
    else:
        return False, ret.text

def addDictionaryAndFolders(token, weburl, table):
    '''
    table辞書の最初の項目を辞書として登録し、配下のfoldersを再帰的にその辞書のフォルダーとして登録していく。
    descriptorsとprediction_modelsをそれぞれのフォルダー以下へ登録する。
    @param table(dict) 参照系APIの辞書取得で取得した辞書の構造を簡略化したdict
    @retval なし
    '''

    # まずは辞書作成
    key = sorted(table.keys())[0]
    name = table[key]["folder_name"]
    description = table[key]["description"]
    dictid, folderid = addDictionary(token, weburl, name, description)

    print("")
    print("Added new dictionary name(%s) / ID(%s) / Folder ID(%s)"%(name, dictid, folderid))
    # 次に登録した新しい辞書に、記述子や予測モデルを登録する。
    for descriptor in table[key]["descriptors"]:
        body = {"descriptor_id":descriptor}
        url = weburl + "/%s"%dictid + "/folders/%s"%folderid + "/descriptors"
        ret, result = apiAccess(token, url, "post", body, debug_print=True)
    for prediction_model in table[key]["prediction_models"]:
        body = {"prediction_model_id":prediction_model}
        url = weburl + "/%s"%dictid + "/folders/%s"%folderid + "/prediction-models"
        ret, result = apiAccess(token, url, "post", body, debug_print=True)
    #for item in table["folders"]:
    #    addDictionaryAndFolders(folders_dict)
    addFolder(token, weburl, dictid, folderid, table[key]["folders"])


def main():
    '''
    開始点
    '''

    if len(sys.argv) == 1:
        print("need dict file")
        sys.exit(1)

    infile = open(sys.argv[1])
    folders_dict = json.load(infile)
    infile.close()

    token = sys.argv[2]
    weburl = sys.argv[3]

    #print(json.dumps(folders_dict, indent=2, ensure_ascii=False))
    addDictionaryAndFolders(token, weburl, folders_dict)

if __name__ == '__main__':
    main()

