#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.

'''
NIMS野口さん作成のインベントリAPIプログラムのラッパープログラム
'''

import sys, os
import time
import json
import datetime
import codecs
import glob
if sys.version_info[0] <= 2:
    import ConfigParser
    #from urlparse import urlparse
else:
    import configparser
    #from urllib.parse import urlparse
import subprocess
import shutil
from importlib import import_module

if os.name == "nt":
    import openam_operator
else:
    from openam_operator import openam_operator     # MIシステム認証ライブラリ

from InventoryOperatorGui import *
from getInventory import *
from postInventory4 import *
from checklistctrl import *
from addDictionaryAndFolders import *
from api_access import *
#from old_new import *
from analyze_inventory_json import *
from src_dst import *

ROOT_FOLDER = "root_folder"                     # 2018/08/15:folder->forder
CONFIG_FILENAME = "Inventory.conf"              # 入出力用コンフィグファイルの名前

def folderFactory(elements, space="", debug=True):
    '''
    root_folderの辞書から、再帰的にフォルダー情報とインベントリー情報を読み出し、辞書を作成する。
    '''

    space += "  "

    folders = []
    for item in elements:
        folder = {}
        folder_id = item["folder_id"].split("/")[-1]
        folder_name = item["folder_name"]
        folder["folder_id"] = folder_id
        folder["folder_name"] = folder_name
        folder["descriptors"] = {}
        folder["description"] = item["description"]
        folder["prediction_models"] = {}
        print("%s%s - %s"%(space, folder_id, folder_name))
        if ("descriptors" in item) is True:
            descriptors = item["descriptors"]
            for d in descriptors:
                print("%s  %s - %s"%(space, d["descriptor_id"].split("/")[-1], d["preferred_name"].split("@")[0])) 
                #folder["descriptors"].append("%s:%s"%(d["descriptor_id"].split("/")[-1], d["preferred_name"].split("@")[0]))
                #folder["descriptors"][d["preferred_name"].split("@")[0]] = d["descriptor_id"].split("/")[-1]
                folder["descriptors"][d["descriptor_id"].split("/")[-1]] = d["preferred_name"].split("@")[0]
        if ("prediction_models" in item) is True:
            predictions = item["prediction_models"]
            for p in predictions:
                print("%s  %s - %s"%(space, p["prediction_model_id"].split("/")[-1], p["preferred_name"].split("@")[0])) 
                #folder["prediction_models"].append("%s:%s"%(p["prediction_model_id"].split("/")[-1], p["preferred_name"].split("@")[0]))
                #folder["prediction_models"][p["preferred_name"].split("@")[0]] = p["prediction_model_id"].split("/")[-1]
                folder["prediction_models"][p["prediction_model_id"].split("/")[-1]] = p["preferred_name"].split("@")[0]
        if ("folders" in item) is True:
            folder["folders"] = folderFactory(item["folders"], space)
        folders.append(folder)

    return folders

def dict_print(elements, spc, debug=False):
    '''
    辞書を再帰的に表示する
    '''

    spc += "  "

    dictionary = {}
    inventory_id = None
    inventory_name = None
    for item in elements:
        if type(elements[item]) is dict:
            ret = dict_print(elements[item], spc, debug)
            for item in ret:
                dictionary[item] = ret[item]
                
        elif type(elements[item]) is list:
            list_elements = elements[item]
            for list_item in list_elements:
                if type(list_item) is dict:
                    ret = dict_print(list_item, spc, debug)
                    for item in ret:
                        dictionary[item] = ret[item]
                else:
                    if debug is True:
                        print("%s | %s"%(spc, list_item))
        else:

            if item == "preferred_name" or item == "software_tool_name":
                inventory_name = elements[item].split("@")[0]
            elif item == "descriptor_id":
                inventory_id = elements[item].split("/")[-1]
            elif item == "prediction_model_id":
                inventory_id = elements[item].split("/")[-1]
            elif item == "software_tool_id":
                inventory_id = elements[item].split("/")[-1]

            if debug is True:
                print("%s | %20s : %s"%(spc, item, elements[item]))

    if len(elements) == 2:
        #dictionary[inventory_name] = inventory_id
        dictionary[inventory_id] = inventory_name

    return dictionary

def folder_print(elements, spc, debug=False):
    '''
    root_folder以下、foldersを再帰的に表示する
    '''

    spc += "  "

    folders = {}
    folder_id = None
    folder_name = None
    dictionary_id = None
    retval = {}
    
    for item in elements:
        if type(elements[item]) is dict:
            ret = folder_print(elements[item], spc)
            if len(ret) != 0:
                for ret_item in ret:
                    retval[ret_item] = ret[ret_item]
                #print("ret = %s"%ret)
        elif type(elements[item]) is list:
            list_elements = elements[item]
            for list_item in list_elements:
                if type(list_item) is dict:
                    ret = folder_print(list_item, spc)
                    if len(ret) != 0:
                        for ret_item in ret:
                            retval[ret_item] = ret[ret_item]
                        #print("ret = %s"%ret)
                else:
                    if debug is True:
                        print("%s | %s"%(spc, list_item))
        else:

            #print("%s"%item)
            if item == "folder_id" or item == "folder_name" or item == "dictionary_id":
                if item == "folder_id":
                    folder_id = contents = elements[item].split("/")[-1]
                elif item == "dictionary_id":
                    dictionary_id = contents = elements[item].split("/")[-1]
                else:
                    folder_name = contents = elements[item]
                if folder_id is not None and folder_name is not None:
                    folders[folder_id] = [folder_name]
                    if len(retval) != 0:
                        #print("folders = %s"%folders)
                        folders[folder_id].append(retval)
                        retval = {}

                    folder_id = folder_name = None
            if debug is True:
                print("%s | %20s : %s"%(spc, item, elements[item]))

    return folders

class InventoryOperator(InventoryOperatorGUI):
    '''
    '''

    def __init__(self, parent, descriptor_ref_conf = "src_descriptors.conf", prediction_ref_conf = "src_prediction-models.conf", software_tool_ref_conf = "src_software-tools.conf", descriptor_upd_conf = "dst_descriptors.conf", prediction_upd_conf = "dst_prediction-models.conf", software_tool_upd_conf = "dst_software-tools.conf", modules_xml = "modules.xml", folders_ref_json = "src_folders.json", folders_upd_json = "dst_folders.json", debug_mode=False):
        '''
        初期化
        @params parent(親となるクラス。通常None)
        '''

        InventoryOperatorGUI.__init__(self, parent)

        self.userid_ref = None
        self.token_ref = None
        self.url_ref = None
        self.userid_upd = None
        self.token_upd = None
        self.url_upd = None
        self.conffilesave = None
        self.conffileread = None

        self.ref_dictdict = None                    # 参照側辞書の辞書
        self.UserList = {}                          # URL毎のUserIDをキーにしたTokenの辞書
        self.VersionList = {}                       # URL毎のバージョンの指定

        self.ref_folders = {}                       # 参照側、辞書毎のフォルダー格納。辞書。
        self.upd_folders = {}                       # 更新側、辞書毎のフォルダー格納。辞書。
        self.workdir = "./"                         # working directory name
        self.upd_workdir = "."                      # work directory for Update
        self.ref_workdir = "."                      # work directory for Reference

        # confファイル名
        self.descriptor_ref_conf = descriptor_ref_conf
        self.prediction_ref_conf = prediction_ref_conf
        self.software_tool_ref_conf = software_tool_ref_conf
        self.descriptor_upd_conf = descriptor_upd_conf
        self.prediction_upd_conf = prediction_upd_conf
        self.software_tool_upd_conf = software_tool_upd_conf
        # jsonファイル名
        self.descriptor_ref_json = "descriptor_ref.json"
        self.prediction_ref_json = "prediction_ref.json"
        self.software_tool_ref_json = "software_tool_ref.json"
        self.descriptor_upd_json = "descirptor_upd.json"
        self.prediction_upd_json = "prediction_upd.json"
        self.software_tool_upd_json = "software_tool_upd.json"
        # その他のファイル名
        self.modulesxml = modules_xml
        self.folders_ref = folders_ref_json
        self.folders_upd = folders_upd_json
        self.modulecopy_directory = "../../module_copy"
        self.inventory_management = "../../misrc_inventory_management"
        # 動的読み込みパッケージ用
        self.inventory_management_package = None

        # 起動時iniファイル情報の読み込み
        init_dic = self.readIniFile()
        #print("length of init_dic is %d"%len(init_dic))
        #print(init_dic)

        # TreeCtrl準備
        self.imageList = wx.ImageList(16,16)
        self.root_pict = self.imageList.Add(wx.ArtProvider.GetBitmap(wx.ART_HELP_BOOK, wx.ART_OTHER, (16,16)))
        self.dir_pict = self.imageList.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16,16)))
        self.file_pict = self.imageList.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16,16)))
        self.m_treeCtrlSelections.AssignImageList(self.imageList)
        self.root = None
        self.RefTree = {}
        self.UpdTree = {}

        # ListCtrl準備
        self.del_sel = None

        self.m_textCtrlUpdateAccessToken.Enable(False)
        self.m_textCtrlReferenceAccessToken.Enable(False)

        self.DictionaryFoldersID = None
        self.DictionaryFoldersIDUpdate = None

        self.infilefilter = "All Files (*.*) |*.*"

        self.UserIDAndToken = {}

        self.InitializeRefListCtrl()
        self.InitializeUpdListCtrl()

        self.progressDialog = None

        # 前回の設定読み込み
        self.readConfigFile()
        # JSONファイル名デフォルト値の表示
        self.m_textCtrlDescriptorFileNameRef.SetValue(self.descriptor_ref_conf)
        self.m_textCtrlDescriptorFileNameUpdate.SetValue(self.descriptor_upd_conf)
        self.m_textCtrlPredictionModelFilenameRef.SetValue(self.prediction_ref_conf)
        self.m_textCtrlPredictionModelFilenameUpdate.SetValue(self.prediction_upd_conf)
        self.m_textCtrlSoftwareToolFilenameRef.SetValue(self.software_tool_ref_conf)
        self.m_textCtrlSoftwareToolFilenameUpdate.SetValue(self.software_tool_upd_conf)
        self.m_textCtrlModulesXMLUpdate.SetValue(self.modulesxml)
        self.m_textCtrlFoldersFilenameRef.SetValue(self.folders_ref)
        self.m_textCtrlFoldersFilenameUpdate.SetValue(self.folders_upd)

        # ボタンの表示変更
        self.m_buttonDeleteInventories.SetLabel("inventry取得...")
        self.debug_mode = debug_mode

    #------------------ここからイベントハンドラ----------------------
    def InventoryOperatorGUIOnClose( self, event ):
        '''
        終了時の挙動
        '''

        init_dict = {}
        ref_dict = {}
        upd_dict = {}
        #self.userid_ref = self.m_textCtrlReferenceUserID.GetValue()
        self.userid_ref = self.m_comboBoxReferenceUserID.GetValue()
        ref_dict["UserID"] = self.userid_ref
        self.token_ref = self.m_textCtrlReferenceAccessToken.GetValue()
        ref_dict["Token"] = self.token_ref
        self.url_ref = self.m_comboBoxReferenceURL.GetValue()
        ref_dict["URL"] = self.url_ref
        self.ref_workdir = self.m_textCtrlConfFileNameSave.GetValue()
        ref_dict["ConfFile"] = self.ref_workdir
        init_dict["Reference"] = ref_dict
        #self.userid_upd = self.m_textCtrlUpdateUserID.GetValue()
        self.userid_upd = self.m_comboBoxUpdateUserID.GetValue()
        upd_dict["UserID"] = self.userid_upd
        self.token_upd = self.m_textCtrlUpdateAccessToken.GetValue()
        upd_dict["Token"] = self.token_upd
        self.url_upd = self.m_comboBoxUpdateURL.GetValue()
        upd_dict["URL"] = self.url_upd
        self.upd_workdir = self.m_textCtrlConfFileNameRead.GetValue()
        upd_dict["ConfFile"] = self.upd_workdir
        init_dict["Update"] = upd_dict

        if sys.version_info[0] <= 2:
            parser = ConfigParser.SafeConfigParser()
        else:
            parser = configparser.ConfigParser()

        inifilename = "./inventory-operator.ini"
        #inifilename = "Inventory.conf"
        if os.path.exists(inifilename) is True:
            parser.read(inifilename)

        if parser.has_section("Reference") is True:
            parser.set("Reference", "URL", ref_dict["URL"])
            parser.set("Reference", "conffile", ref_dict["ConfFile"])
            print("Reference/ConfFile = %s"%ref_dict["ConfFile"])
            #parser.set("Reference", "UserID", ref_dict["UserID"])
            #parser.set("Reference", "Token", ref_dict["Token"])
        if parser.has_section("Update") is True:
            parser.set("Update", "URL", upd_dict["URL"])
            parser.set("Update", "ConfFile", upd_dict["ConfFile"])
            #parser.set("Update", "UserID", upd_dict["UserID"])
            #parser.set("Update", "Token", upd_dict["Token"])
            parser.set("Update", "modules_xml_info", self.modulesxml)
        if parser.has_section("System") is False:
            parser.add_section("System")
        parser.set("System", "modulecopy", self.modulecopy_directory)
        parser.set("System", "inventory_management", self.inventory_management)

        outfile = open("inventory-operator.ini", "w")
        #outfile = open("Inventory.conf", "w")
        parser.write(outfile)
        outfile.close()

        event.Skip()

    def m_buttonReferenceGetAccessTokenOnButtonClick( self, event ):
        '''
        アクセストークンの取得
        '''

        event.Skip()

    def m_buttonGetDictionaryOnButtonClick( self, event ):
        '''
        参照用辞書・フォルダーの一覧取得
        '''

        userid, token = self.CheckUserIDAndToken()
        if userid is False or token is False:
            return

        referenceURL = self.m_comboBoxReferenceURL.GetValue()
        weburl = 'https://%s:50443'%referenceURL + '/inventory-api/v%s/users/'%self.VersionList[referenceURL]["ref_version"] + userid + '/dictionaries'

        result, ret = apiAccess(token, weburl, debug_print=True)

        ret = ret.json()

        self.ref_dictdict = ret["dictionaries"]

        self.InitializeRefListCtrl()
        self.AddDictionariesRefListCtrl()

        all_folders = {}
        for items in self.ref_dictdict:
            for item in items:
                if item == "dictionary_id":
                    weburl = 'https://%s:50443'%referenceURL + '/inventory-api/v%s/users/'%self.VersionList[referenceURL]["ref_version"] + userid + '/dictionaries/' + items[item].split("/")[-1]
                    result, ret = apiAccess(token, weburl)

                    ret = ret.json()
                    self.ref_folders[items[item].split("/")[-1]] = ret          # 辞書毎のフォルダーを記録

                    #if ret.has_key(ROOT_FOLDER) is True:
                    if (ROOT_FOLDER in ret) is True:
                        #print("ret = %s"%str(ret))
                        items2 = ret[ROOT_FOLDER]
                        #print items2
                        folders = folder_print(items2, "")
                        if len(folders) != 0:
                            for folder in folders:
                                all_folders[folder] = folders[folder]

        # for debug
        #for item in all_folders:
        #    print("key = %s / %s"%(item, all_folders[item]))

        self.AddFoldersRefListCtrl(all_folders)
        event.Skip()

    def m_buttonGetDictionaryUpdateOnButtonClick( self, event ):
        '''
        Update用辞書・フォルダー一覧取得ボタン
        '''

        userid, token = self.CheckUpdateUserIDAndToken()
        if userid is False or token is False:
            return

        updateURL = self.m_comboBoxUpdateURL.GetValue()
        weburl = 'https://%s:50443'%updateURL + '/inventory-api/v%s/users/'%self.VersionList[updateURL]["ref_version"] + userid + '/dictionaries'

        result, ret = apiAccess(token, weburl, debug_print=True)
        ret = ret.json()

        self.upd_dictdict = ret["dictionaries"]

        self.InitializeUpdListCtrl()
        self.AddDictionariesUpdListCtrl()

        all_folders = {}
        for items in self.upd_dictdict:
            for item in items:
                if item == "dictionary_id":
                    weburl = 'https://%s:50443'%updateURL + '/inventory-api/v%s/users/'%self.VersionList[updateURL]["ref_version"] + userid + '/dictionaries/' + items[item].split("/")[-1]
                    result, ret = apiAccess(token, weburl)
                    ret = ret.json()

                    #if ret.has_key(ROOT_FOLDER) is True:
                    if (ROOT_FOLDER in ret) is True:
                        #print("ret = %s"%str(ret))
                        items2 = ret[ROOT_FOLDER]
                        #print items2
                        folders = folder_print(items2, "")
                        if len(folders) != 0:
                            for folder in folders:
                                all_folders[folder] = folders[folder]

        self.AddFoldersUpdListCtrl(all_folders)

        event.Skip()
    
    def m_buttonGetInventoryOnButtonClick( self, event ):
        '''
        インベントリ情報の取得
        '''

        userid, token = self.CheckUserIDAndToken()
        if userid is False or token is False:
            return

        path = self.m_staticTextDictionaryAndFolderID.GetLabel()
        if path is None or path == "":
            dialog = wx.MessageDialog(self, u"辞書・フォルダーID情報が空です。", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False

        if os.path.exists(self.ref_workdir) is True:
            if os.path.isfile(self.ref_workdir) is True:
                dialog = wx.MessageDialog(self, u"作業ディレクトリ(%s)と同じ名前のファイルがあります。"%self.ref_workdir, style=wx.OK)
                dialog.ShowModal()
                dialog.Destroy()
                return False, False
        else:
            os.mkdir(self.ref_workdir)

        cwd = os.getcwd()
        os.chdir(self.ref_workdir)

        #==> 2020/01/27 フォルダー構造のjsonファイル作成
        folders_dict = {}
        dictid = self.m_staticTextDictionaryAndFolderID.GetLabel().split("/")[1]
        #print(json.dumps(self.ref_folders[dictid], indent=2, ensure_ascii=False))
        top_folder_id = self.ref_folders[dictid]["root_folder"]["folder_id"].split("/")[-1]
        top_dictionary_id = dictid
        top_folder_name = self.ref_folders[dictid]["root_folder"]["folder_name"].split("@")[0]
        top_folder_description = self.ref_folders[dictid]["root_folder"]["description"]
        print("%s - %s"%(top_folder_id, top_folder_name))
        #folders_dict[top_folder_id] = {"folder_name": top_folder_name, "description": top_folder_description, "folders":[], "descriptors":{}, "prediction_models":{}}
        folders_dict[top_dictionary_id] = {"folder_id": top_folder_id, "folder_name": top_folder_name, "description": top_folder_description, "folders":[], "descriptors":{}, "prediction_models":{}}

        if ("descriptors" in self.ref_folders[dictid]["root_folder"]) is True:         # 辞書直下にdescriptorがあれば
            descriptors = self.ref_folders[dictid]["root_folder"]["descriptors"]
            ds = {}
            for d in descriptors:
                did = d["descriptor_id"].split("/")[-1]
                dname = d["preferred_name"].split("@")[0]
                print("  %s - %s"%(did, dname))
                #folders_dict[top_folder_id]["descriptors"][did] = dname
                folders_dict[top_dictionary_id]["descriptors"][did] = dname
        if ("prediction_models" in self.ref_folders[dictid]["root_folder"]) is True:   # 辞書直下にprediction_modelがあれば
            predictions = self.ref_folders[dictid]["root_folder"]["prediction_models"]
            for p in predictions:
                pid = p["prediction_model_id"].split("/")[-1]
                pname = p["preferred_name"].split("@")[0]
                print("  %s - %s"%(pid, pname))
                #folders_dict[top_folder_id]["prediction_models"][pid] = pname
                folders_dict[top_dictionary_id]["prediction_models"][pid] = pname

        # root_folders/foldersデバッグプリント
        #print(json.dumps(self.ref_folders[dictid]["root_folder"], indent=2, ensure_ascii=False))
        # フォルダーと登録してある記述子情報の辞書作成
        if ('folders' in self.ref_folders[dictid]["root_folder"]) is True:
            folders = self.ref_folders[dictid]["root_folder"]["folders"]
            #folders_dict[top_folder_id]["folders"] = folderFactory(folders)
            folders_dict[top_dictionary_id]["folders"] = folderFactory(folders)

        outfile = open(self.folders_ref, "w")
        #print(json.dumps(folders_dict, indent=2, ensure_ascii=False))
        outfile.write((json.dumps(folders_dict, indent=2, ensure_ascii=False)))
        outfile.close()

        path = "users/" + self.m_staticTextReferenceUserID.GetLabel() + "/" + path
        self.MakeConfigFile(userid, token, path, self.ref_workdir)

        url = self.m_comboBoxReferenceURL.GetValue()
        ReferenceURL = self.m_comboBoxReferenceURL.GetValue()
        url = "https://%s:50443"%url + "/inventory-api/v%s"%self.VersionList[ReferenceURL]["ref_version"]

        # 従来の方法でInventory情報を入手する
        getInventory_main(url, self.VersionList[ReferenceURL]["ref_version"])

        # 入手したInventory情報を１ID毎にばらす
        self.divideInventories()

        os.chdir(cwd)

        event.Skip()

    def m_buttonInventoryUpdateOnButtonClick( self, event ):
        '''
        インベントリ情報の登録(登録先は辞書)
        '''

        userid, token = self.CheckUpdateUserIDAndToken()
        if userid is False or token is False:
            return

        path = self.m_staticTextDictionaryAndFolderIDUpdate.GetLabel()
        if path is None or path == "":
            dialog = wx.MessageDialog(self, u"辞書・フォルダーID情報が空です。", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False

        cwd = os.getcwd()
        os.chdir(self.upd_workdir)
        
        path = "users/" + self.m_staticTextUpdateUserID.GetLabel() + "/" + path
        self.MakeConfigFile(userid, token, path, self.upd_workdir)

        url = self.m_comboBoxUpdateURL.GetValue()
        updateURL = self.m_comboBoxUpdateURL.GetValue()
        url = "https://%s:50443"%url + "/inventory-update-api/v%s"%self.VersionList[updateURL]["upd_version"]

        postInventory_main(url)

        os.chdir(cwd)
        event.Skip()

    def m_buttonInventryUpdateWithDictFolderOnButtonClick( self, event ):
        '''
        インベントリ情報の登録（登録先は指定しない。元となるインベントリの帰属情報に従う。登録後、辞書およびフォルダー作成して、それぞれ配下に登録される）
        '''

        userid, token = self.CheckUpdateUserIDAndToken()
        if userid is False or token is False:
            return

        if os.path.exists(self.upd_workdir) is True:
            if os.path.isfile(self.upd_workdir) is True:
                dialog = wx.MessageDialog(self, u"作業ディレクトリ(%s)と同じ名前のファイルがあります。"%self.upd_workdir, style=wx.OK)
                dialog.ShowModal()
                dialog.Destroy()
                return False, False
        else:
            dialog = wx.MessageDialog(self, u"作業ディレクトリ(%s)がありません。"%self.upd_workdir, style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False
        
        # 予測モジュール格納ディレクトリの確認
        prediction_module_directory = self.m_textCtrlModulesXMLUpdate.GetValue()
        if os.path.exists(prediction_module_directory) is True and os.path.isdir(prediction_module_directory) is True:
            pass
        else:
            dialog = wx.MessageDialog(self, u"予測モジュール格納ディレクトリ(%s)がありません。"%prediction_module_directory, style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False

        dialog = wx.MessageDialog(self, u"辞書・フォルダーを作成しつつインベントリを登録します。", "Info", style=wx.YES|wx.NO)
        ret = dialog.ShowModal()
        dialog.Destroy()
        if ret == wx.ID_NO:
            return

        cwd = os.getcwd()
        os.chdir(self.upd_workdir)
        
        # 各confファイルの確認
        okUpdate = True
        needed_files = ""
        if os.path.exists(self.descriptor_upd_conf) is False:
            needed_files += self.descriptor_upd_conf
            okUpdate = False
        if os.path.exists(self.prediction_upd_conf) is False:
            if okUpdate is False:
                needed_files += "/"
            needed_files += self.prediction_upd_conf
            okUpdate = False
        if os.path.exists(self.software_tool_upd_conf) is False:
            if okUpdate is False:
                needed_files += "/"
            needed_files += self.software_tool_upd_conf
            okUpdate = False
        src_dst_filename = "descriptors.ids"

        if okUpdate is False:
            dialog = wx.MessageDialog(self, u"作業ディレクトリに必要なファイル(%s)がありません。"%needed_files, style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            os.chdir(cwd)
            return False, False

        # 構成ファイル必要事項追加
        if sys.version_info[0] <= 2:
            descriptor_parser = ConfigParser.SafeConfigParser()
            prediction_parser = ConfigParser.SafeConfigParser()
            software_tool_parser = ConfigParser.SafeConfigParser()
        else:
            descriptor_parser = configparser.ConfigParser()
            prediction_parser = configparser.ConfigParser()
            software_tool_parser = configparser.ConfigParser()

        url = self.m_comboBoxUpdateURL.GetValue()
        updateURL = self.m_comboBoxUpdateURL.GetValue()
        #site_to = url.split(".")[0]
        site_to = url

        ## 記述子用
        site_from = None
        descriptor_parser.read(self.descriptor_upd_conf)
        if descriptor_parser.has_section("authorize") is True:
            descriptor_parser.set("authorize", "hostPort", "%s:50443"%url)
            descriptor_parser.set("authorize", "apiversion", "%s"%self.VersionList[updateURL]["upd_version"])
            descriptor_parser.set("authorize", "user_id", userid)
            descriptor_parser.set("authorize", "token", token)
            if descriptor_parser.has_option("authorize", "site") is True:
                site_from = descriptor_parser.get("authorize", "site")

        # 記述子一元管理テーブルにしたがって取捨選択
        # 一元管理テーブルにあるIDはすでに複製が行われているので、ここで行わない。
        if self.inventory_management_package is None:
            sys.stderr.write("一元管理情報ライブラリが読み込まれていません。")
            sys.stderr.flush()
            return
        new_list = []
        # 元先リストDBから
        src_dst = self.inventory_management_package.getInventoryData(site_from, site_to)
        # 今回の辞書に含まれる記述子データ
        src_table = descriptor_parser.get("file", "inputfile").split("\n")
        # 新規コピーの必要性の確認
        for src_item in src_table:
            noNeedCopy = False
            for item in src_dst:
                if "inventory_%s.json"%item == src_item and src_dst[item] is not None:
                    noNeedCopy = True
            if noNeedCopy is False:
                new_list.append(src_item)
        # 新規コピーのmodule_copyプログラム用構成ファイルへの登録
        descriptor_jsons = ""
        for item in new_list:
            if descriptor_jsons == "":
                descriptor_jsons += "%s\n"%item
            else:
                descriptor_jsons += "           %s\n"%item
        descriptor_parser.set("file", "inputfile", descriptor_jsons)
        outfile = open(self.descriptor_upd_conf, "w")
        descriptor_parser.write(outfile)
        outfile.close()
        ## 予測モデル用
        prediction_parser.read(self.prediction_upd_conf)
        if prediction_parser.has_section("authorize") is True:
            prediction_parser.set("authorize", "hostPort", "%s:50443"%url)
            prediction_parser.set("authorize", "apiversion", "%s"%self.VersionList[updateURL]["upd_version"])
            prediction_parser.set("authorize", "user_id", userid)
            prediction_parser.set("authorize", "token", token)
        outfile = open(self.prediction_upd_conf, "w")
        prediction_parser.write(outfile)
        outfile.close()
        ## ソフトウェアツール用
        software_tool_parser.read(self.software_tool_upd_conf)
        if software_tool_parser.has_section("authorize") is True:
            software_tool_parser.set("authorize", "hostPort", "%s:50443"%url)
            software_tool_parser.set("authorize", "apiversion", "%s"%self.VersionList[updateURL]["upd_version"])
            software_tool_parser.set("authorize", "user_id", userid)
            software_tool_parser.set("authorize", "token", token)
        outfile = open(self.software_tool_upd_conf, "w")
        software_tool_parser.write(outfile)
        outfile.close()

        #return

        # 記述子登録
        if descriptor_jsons == "":
            # 一元管理データとの照合で新規コピーの必要が無い場合
            sys.stderr.write("新規登録する記述子はありません。")
            sys.stderr.flush()
            dialog = wx.MessageDialog(self, u"新規登録する記述子はありません。",style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            os.chdir(cwd)
            return False, False
        else:
            cmd = "python3.6 %s/script/opeInventory3.py %s"%(self.modulecopy_directory, self.descriptor_upd_conf)
            sys.stderr.write("記述子登録中...%s\n%s"%(os.getcwd(), cmd))
            sys.stderr.flush()
            ret = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
            lines = []
            if self.debug_mode is True:
                while True:
                    line = ret.stdout.readline()
                    if line:
                        print("%s"%line.split("\n")[0])
                        lines.append(line.split("\n")[0])
                    if not line and ret.poll() is not None:
                        break
            else:
                pass

            stdout, stderr = ret.communicate()
    
            # 新規コピー動作の確認
            if ret.returncode != 0:
                dialog = wx.MessageDialog(self, u"記述子登録に失敗しました。\n標準出力:\n%s\n標準エラー:\n%s"%(stdout, stderr), style=wx.OK)
                dialog.ShowModal()
                dialog.Destroy()
                os.chdir(cwd)
                print(u"記述子登録に失敗しました。\n標準出力:\n%s\n標準エラー:\n%s"%(stdout, stderr))
                return False, False

            # 元先リストファイルの確認
            if os.path.exists(src_dst_filename) is False:
                dialog = wx.MessageDialog(self, u"作業ディレクトリに記述子IDの元先対応ファイル(%s)がありません。"%src_dst_filename, style=wx.OK)
                dialog.ShowModal()
                dialog.Destroy()
                os.chdir(cwd)
                return False, False

            # 元先リストの追加
            infile = open(src_dst_filename)
            try:
                src_dst_dict = json.load(infile)
            except json.decoder.JSONDecodeError as e:
                sys.stderr.write("元先ファイル、読み込み中に例外発生\n")
                sys.stderr.write("%s\n"%e)
                sys.stderr.flush()
                infile.close()
                return
            infile.close()
            # 元先DBへ一旦格納
            src_dst = self.inventory_management_package.addInventoryData(site_from, site_to, src_dst_dict)

        # 元先ファイルの作成
        outfile = open("descriptors.ids", "w")
        json.dump(src_dst_dict, outfile, indent=2)
        outfile.close()

        # 予測モデル登録
        cmd = "python3.6 %s/script/opeInventory3.py %s %s"%(self.modulecopy_directory, self.prediction_upd_conf, src_dst_filename)
        sys.stderr.write("\n予測モデル登録中...%s\n%s\n"%(os.getcwd(), cmd))
        sys.stderr.flush()
        ret = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if self.debug_mode is True:
            while True:
                line = ret.stdout.readline()
                if line:
                    print("%s"%line.split("\n")[0])
                    lines.append(line.split("\n")[0])
                if not line and ret.poll() is not None:
                    break
        else:
            stdout, stderr = ret.communicate()
    
        if ret.returncode != 0:
            dialog = wx.MessageDialog(self, u"予測モデル登録に失敗しました。", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            os.chdir(cwd)
            return False, False

        # ソフトウェアツール登録
        sys.stderr.write("\nソフトウェアツール登録中...%s\n"%os.getcwd())
        sys.stderr.flush()

        # 予測モジュールファイル格納ディレクトリ名の取得
        prediction_module_directory = self.m_textCtrlModulesXMLUpdate.GetValue()
        current_dir = os.getcwd()
        os.chdir(prediction_module_directory)
        prediction_module_files = glob.glob("*.xml")
        os.chdir(current_dir)

        # 辞書・フォルダー元先変換その１（記述子ID）
        sys.stderr.write("辞書・フォルダーテーブルの記述子IDを新しくしています。\n")
        srcfile = self.folders_upd
        newfile = "folder_table.dat"
        #ret = translateOldNew(src_dst_filename, srcfile, newfile)
        ret = translateOldNew_with_table(src_dst_filename, srcfile, newfile)

        # 予測モジュール元先変換その１（記述子ID）
        sys.stderr.write("予測モジュールの記述子IDを新しい記述子IDに変更しています。\n")
        prediction_module_files_temp = []
        prediction_module_files_new = []
        for item in prediction_module_files:
            prediction_module_filename = os.path.join(prediction_module_directory, item)
            sys.stderr.write("%s\n"%prediction_module_filename)
            if os.path.exists(prediction_module_filename) is True:
                newfile1 = os.path.splitext(prediction_module_filename)[0] + "_temp1.xml"
                prediction_module_files_temp.append(os.path.join(prediction_module_directory, newfile1))
                newfile2 = os.path.splitext(prediction_module_filename)[0] + "_new.xml"
                prediction_module_files_new.append(os.path.join(prediction_module_directory, newfile2))
                #ret = translateOldNew(src_dst_filename, prediction_module_filename, newfile1)
                ret = translateOldNew_with_table(src_dst_filename, prediction_module_filename, newfile1)

        # 辞書・フォルダー元先変換その２（予測モデルID）
        sys.stderr.write("辞書・フォルダーテーブルの予測モデルIDを新しくしています。\n")
        src_dst_filename = "prediction_models.ids"
        if os.path.exists(src_dst_filename) is False:
            dialog = wx.MessageDialog(self, u"作業ディレクトリに予測モデルIDの元先対応ファイル(%s)がありません。"%src_dst_filename, style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            shutil.copyfile("folder_table.dat", self.folders_upd)
        else:
            srcfile = "folder_table.dat"
            newfile = self.folders_upd
            #ret = translateOldNew(src_dst_filename, srcfile, newfile)
            ret = translateOldNew_with_table(src_dst_filename, srcfile, newfile)

        # 予測モジュール元先変換その２（予測モデルID）
        sys.stderr.write("予測モジュールの予測モデルIDを新しい予測モデルIDに変更しています。\n")
        for i in range(len(prediction_module_files_temp)):
            if os.path.exists(prediction_module_files_temp[i]) is True:
                #ret2 = translateOldNew(src_dst_filename, prediction_module_files_temp[i], prediction_module_files_new[i])
                ret2 = translateOldNew_with_table(src_dst_filename, prediction_module_files_temp[i], prediction_module_files_new[i])
                sys.stderr.write("新しい予測モジュールのファイル名は%sです。"%prediction_module_files_new[i])

        # 辞書とフォルダーの作成とインベントリの登録
        infile = open(newfile)
        folders_dict = json.load(infile)
        infile.close()
        if ret is True:
            sys.stderr.write("\n辞書・フォルダーの登録と記述子、予測モデル、ソフトウェアツールの辞書、フォルダーへの登録中...\n")
            sys.stderr.flush()
            weburl = "https://%s:50443/inventory-update-api/v%s/users/%s/dictionaries"%(url, self.VersionList[updateURL]["upd_version"], userid)
            addDictionaryAndFolders(token, weburl, folders_dict)

        sys.stderr.write("\n")
        sys.stderr.flush()

        os.chdir(cwd)
        return
        event.Skip()

    def m_buttonInventryUpdateWithDictFolderOnButtonClick_discarded( self, event ):
        '''
        インベントリ情報の登録（登録先は辞書)

        ※ ※ ※ 新しい登録方法の実装によりこちらは用途廃棄(2020/02/14)

        '''

        userid, token = self.CheckUpdateUserIDAndToken()
        if userid is False or token is False:
            return

        dialog = wx.MessageDialog(self, u"辞書・フォルダーを作成しつつインベントリを登録します。", "Info", style=wx.YES|wx.NO)
        ret = dialog.ShowModal()
        dialog.Destroy()
        if ret == wx.ID_NO:
            return

        path = ""
        self.MakeConfigFile(userid, token, path, self.upd_workdir)

        url = self.m_comboBoxUpdateURL.GetValue()
        updateURL = self.m_comboBoxUpdateURL.GetValue()
        url = "https://%s:50443"%url + "/inventory-update-api/v%s"%self.VersionList[updateURL]["upd_version"]
        print(url)

        postInventory_main(url)

        # 記述子・予測モデル登録後、辞書・フォルダー作成と、記述子・予測モデルの辞書・フォルダーへの登録
        table_file = "old_new.lst"
        srcfile = self.folders_upd
        newfile = "folder_table.dat"
        #ret = translateOldNew(table_file, srcfile, newfile)
        ret = translateOldNew_with_table(table_file, srcfile, newfile)

        infile = open(newfile)
        folders_dict = json.load(infile)
        infile.close()
        if ret is True:
            weburl = "https://%s:50443/inventory-update-api/v%s/users/%s/dictionaries"%(url, userid, self.VersionList[updateURL]["upd_version"])
            addDictionaryAndFolders(token, weburl, folders_dict)

        event.Skip()

    def m_buttonBrowseConfFileOnReadButtonClick( self, event ):
        '''
        更新用Configファイルの設定
        '''

        event.Skip()

    def m_buttonUpdateGetAccessTokenOnButtonClick( self, event ):
        '''
        更新系API用アクセストークンの取得
        '''

        event.Skip()

    def m_buttonConfFileNameSaveOnButtonClick( self, event ):
        '''
        参照用作業ディレクトリの指定
        '''

        rfolder = wx.DirDialog(self, u"参照作業用のディレクトリの指定", defaultPath=self.ref_workdir)
        if rfolder.ShowModal() == wx.ID_OK:
            self.ref_workdir = rfolder.GetPath()
            self.m_textCtrlConfFileNameSave.SetValue(self.ref_workdir)

        rfolder.Destroy()

        event.Skip()
    
    def m_buttonBrowseConfFileReadOnButtonClick( self, event ):
        '''
        Update用作業ディレクトリの指定
        '''

        rfolder = wx.DirDialog(self, u"更新作業用のディレクトリの指定", defaultPath=self.upd_workdir)
        if rfolder.ShowModal() == wx.ID_OK:
            self.upd_workdir = rfolder.GetPath()
            self.m_textCtrlConfFileNameRead.SetValue(self.upd_workdir)

        rfolder.Destroy()

        event.Skip()
    
    def m_buttonDeleteInventoriesOnButtonClick( self, event ):
        '''
        インベントリ削除用ダイアログ
        '''

        userid, token = self.CheckUpdateUserIDAndToken()
        if userid is False or token is False:
            return

        path = self.m_staticTextDictionaryAndFolderIDUpdate.GetLabel()
        updateURL = self.m_comboBoxUpdateURL.GetValue()
        if path is None or path == "":
            dialog = wx.MessageDialog(self, u"辞書・フォルダーID情報が空です。", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False

        path = path.split('/')
        #url = os.path.join(path[0], path[1])
        url = path[0] + "/" + path[1]
        path = url
        path = "users/" + self.m_staticTextUpdateUserID.GetLabel() + "/" + path

        weburl = 'https://%s:50443'%updateURL + '/inventory-api/v%s/'%self.VersionList[updateURL]["ref_version"] + path
        result, ret = apiAccess(token, weburl)
        ret = ret.json()

        results = dict_print(ret, "")

        self.del_sel = SelectorBox(self)
        self.del_sel.Bind( wx.EVT_CLOSE, self.SelectorBoxOnClose )
        self.del_sel.m_sdbSizer2Cancel.Bind( wx.EVT_BUTTON, self.m_sdbSizer2OnCancelButtonClick )
        self.del_sel.m_sdbSizer2OK.Bind( wx.EVT_BUTTON, self.m_sdbSizer2OnOKButtonClick )
        self.del_sel.m_listCtrlSelections.Bind(wx.EVT_LIST_COL_CLICK, self.m_listCtrlSelectionsOnColClick)

        self.del_sel.m_listCtrlSelections.InsertColumn(0, "check", wx.LIST_FORMAT_LEFT, 60)
        self.del_sel.m_listCtrlSelections.InsertColumn(1, "Inventory Name", wx.LIST_FORMAT_LEFT, 200)
        self.del_sel.m_listCtrlSelections.InsertColumn(2, "Inventory ID", wx.LIST_FORMAT_LEFT, 130)
        self.del_sel.m_listCtrlSelections.InsertColumn(3, "created time", wx.LIST_FORMAT_LEFT, 120)
        self.del_sel.m_listCtrlSelections.InsertColumn(4, "modified time", wx.LIST_FORMAT_LEFT, 120)
        self.del_sel.m_listCtrlSelections.InsertColumn(5, "created by", wx.LIST_FORMAT_LEFT, 100)
        self.del_sel.m_listCtrlSelections.InsertColumn(6, "Deleted", wx.LIST_FORMAT_LEFT, 50)

        self.progressBar(0)
        self.progressDialog = wx.ProgressDialog(parent=self, title=u"Progress Dialog", message=u"inventory取得中...")
        self.progressDialog.Show()

        count = 0
        pcount = 1
        weburl = 'https://%s:50443'%updateURL + '/inventory-api/v%s/'%self.VersionList[updateURL]["ref_version"]
        for item in results:
            #print("key = %s / contens = %s"%(item, results[item]))
            if item[0] == "D":                   # descriptors
                path = weburl + "descriptors/"
            elif item[0] == "M":                 # prediction-models
                path = weburl + "prediction-models/"
            elif item[0] == "T":                 # software-tools
                path = weburl + "software-tools/"
            else:
                continue

            path = path + "%s"%item

            rslt, ret = apiAccess(token, path)
            self.progressBar(int(float(pcount) / float(len(results)) * 100))
            pcount += 1
            if rslt is False:
                continue
            ret = ret.json()
            self.del_sel.m_listCtrlSelections.InsertStringItem(count, "%d"%count)
            self.del_sel.m_listCtrlSelections.SetStringItem(count, 1, results[item])
            self.del_sel.m_listCtrlSelections.SetStringItem(count, 2, item)
            if rslt is False:
                self.del_sel.m_listCtrlSelections.SetItemBackgroundColour(count, wx.RED)
                self.del_sel.m_listCtrlSelections.SetStringItem(count, 6, "Deleted. in the Dictionary or the Folder")
            else:
                self.del_sel.m_listCtrlSelections.SetStringItem(count, 6, "")

                if ("creation_time" in ret) is True:
                    self.del_sel.m_listCtrlSelections.SetStringItem(count, 3, ret["creation_time"].replace("-", "/").replace("T", " "))
                if ("modified_time" in ret) is True:
                    self.del_sel.m_listCtrlSelections.SetStringItem(count, 4, ret["modified_time"].replace("-", "/").replace("T", " "))
                if ("created_by" in ret) is True:
                    self.del_sel.m_listCtrlSelections.SetStringItem(count, 5, ret["created_by"].replace("-", "/").replace("T", " "))
            count += 1

        self.progressBar(100)
        self.progressDialog.Destroy()
        self.progressDialog = None

        self.del_sel.Show()
        event.Skip()

    def progressBar(self, pos):
        '''
        プログレスバーの操作
        '''

        if self.progressDialog is not None:
            self.progressDialog.Update(pos)

    def m_listCtrlSelectionsOnColClick(self, event):
        '''
        列見出しがクリックされた
        '''

        print("column clicked %d"%event.GetColumn())

        if event.GetColumn() == 0:
            item = self.del_sel.m_listCtrlSelections.GetColumn(0)

            #print item.GetText()
            item_count = self.del_sel.m_listCtrlSelections.GetItemCount()
            if item.GetText() == "check":
                item.SetText("uncheck")
                self.del_sel.m_listCtrlSelections.SetColumn(0, item)
                for i in range(item_count):
                    self.del_sel.m_listCtrlSelections.CheckItem(i, True)
            else:
                item.SetText("check")
                self.del_sel.m_listCtrlSelections.SetColumn(0, item)
                for i in range(item_count):
                    self.del_sel.m_listCtrlSelections.CheckItem(i, False)

        event.Skip()

    def SelectorBoxOnClose(self, event):
        '''
        選択ボックスCloseボタン
        '''

        if self.del_sel is not None:
            self.del_sel.m_listCtrlSelections.ClearAll()
            self.del_sel.Close()
            del self.del_sel
            self.del_sel = None

        event.Skip()

    def m_sdbSizer2OnCancelButtonClick(self, event):
        '''
        選択ボックスCancelボタン
        '''

        self.del_sel.Close()
        del self.del_sel
        self.del_sel = None

        event.Skip()

    def m_sdbSizer2OnOKButtonClick(self, event):
        '''
        選択ボックスOkボタン
        '''

        # 実行問い合わせ
        dialog = wx.MessageDialog(self, "削除確認", "削除確認", style=wx.YES_NO)
        res = dialog.ShowModal()
        if res == wx.ID_NO:
            self.del_sel.Raise()
            return
        selections = {}
        deleted = {}
        item_count = self.del_sel.m_listCtrlSelections.GetItemCount()
        print("item_count = %d"%item_count)
        for i in range(item_count):
            inventory_id = self.del_sel.m_listCtrlSelections.GetItem(i, 2).GetText()
            if self.del_sel.m_listCtrlSelections.IsChecked(i) is True:
                selections[inventory_id] = True
            else:
                selections[inventory_id] = False

            items = self.del_sel.m_listCtrlSelections.GetItem(i, 6).GetText()
            if items != "":
                deleted[inventory_id] = True
            else:
                deleted[inventory_id] = False

        if len(selections) == 0:
            self.del_sel.Close()
            del self.del_sel
            self.del_sel = None
            return

        userid, token = self.CheckUpdateUserIDAndToken()
        if userid is False or token is False:
            return

        dict_folder = self.m_staticTextDictionaryAndFolderIDUpdate.GetLabel()
        updateURL = self.m_comboBoxUpdateURL.GetValue()
        if self.VersionList[updateURL]["upd_version"] != "1":
            weburl = 'https://%s:50443'%updateURL + '/inventory-update-api/v%s/'%self.VersionList[updateURL]["upd_version"]
        else:
            weburl = 'https://%s:50443'%updateURL + '/inventory-api/v1/'

        count = 1
        for key in selections:
            #print("key = %s / id = %s"%(key, selections[key]))
            if key[0] == "D":                   # descriptors
                path = weburl + "descriptors/"
            elif key[0] == "M":                 # prediction-models
                path = weburl + "prediction-models/"
            elif key[0] == "T":                 # software-tools
                path = weburl + "software-tools/"
            else:
                print("unknown inventory-type.")
                self.del_sel.Close()
                del self.del_sel
                self.del_sel = None
                return

            if selections[key] is False:
                continue

            if deleted[key] is True:                        # delete entry under dictionary and folder
                path = weburl + dict_folder + "/%s"%key
            else:                                           # delete inventory 
                path = path + "%s"%key

            #print("%04d:path = %s"%(count, path))
            result, ret = apiAccess(token, path, "delete")
            if result is True:
                print("successfully delete id(%s) of descriptor"%key)
            count += 1

        #print deleted
        self.del_sel.Close()
        del self.del_sel
        self.del_sel = None

        event.Skip()

    def m_treeCtrlSelectionsOnTreeItemActivated( self, event ):
        '''
        TreeCtrl OnTreeItemActivated Event
        '''

        print("OnTreeItemActivated Event")
        event.Skip()
    
    def m_treeCtrlSelectionsOnTreeKeyDown( self, event ):
        '''
        TreeCtrl OnTreeKeyDown Event
        '''

        print("OnTreeKeyDown Event")
        event.Skip()
    
    def m_treeCtrlSelectionsOnTreeSelChanged( self, event ):
        '''
        TreeCtrl OnTreeSelChanged Event
        '''

        #print("OnTreeSelChanged Event")
        selected = self.m_treeCtrlSelections.GetSelection()
        #print("selected tree is %s"%self.m_treeCtrlSelections.GetItemText(selected))
        if sys.version_info[0] <= 2:
            data = self.m_treeCtrlSelections.GetItemData(selected).GetData()
        else:
            data = self.m_treeCtrlSelections.GetItemData(selected)
        #print("data = %s"%data)
        #self.DictionaryFoldersID = "dictionaries/" + data[0] + "/folders/" + data[1]
        self.DictionaryFoldersID = "dictionaries/" + data[0]

        self.m_staticTextDictionaryAndFolderID.SetLabel(self.DictionaryFoldersID)
        event.Skip()
    
    def m_treeCtrlSelectionsOnTreeSelChanging( self, event ):
        '''
        TreeCtrl OnTreeSelChanging Event
        '''

        #print("OnTreeSelChanging Event")
        event.Skip()
    
    def m_treeCtrlSelectionsUpdateOnTreeItemActivated( self, event ):
        '''
        TreeCtrl OnTreeItemActivated Event
        '''

        print("OnTreeItemActivated Event")
        event.Skip()
    
    def m_treeCtrlSelectionsUpdateOnTreeKeyDown( self, event ):
        '''
        TreeCtrl OnTreeKeyDown Event
        '''

        print("OnTreeKeyDown Event")
        event.Skip()
    
    def m_treeCtrlSelectionsUpdateOnTreeSelChanged( self, event ):
        '''
        TreeCtrl OnTreeSelChanged Event
        '''

        selected = self.m_treeCtrlSelectionsUpdate.GetSelection()
        data = self.m_treeCtrlSelectionsUpdate.GetItemData(selected).GetData()
        self.DictionaryFoldersIDUpdate = "dictionaries/" + data[0] + "/folders/" + data[1]
        #self.DictionaryFoldersIDUpdate = "dictionaries/" + data[0]

        self.m_staticTextDictionaryAndFolderIDUpdate.SetLabel(self.DictionaryFoldersIDUpdate)
        event.Skip()
    
    def m_treeCtrlSelectionsUpdateOnTreeSelChanging( self, event ):
        '''
        TreeCtrl OnTreeSelChanging Event
        '''

        event.Skip()
    
    def m_comboBoxUpdateURLOnCombobox( self, event ):
        '''
        更新系のURLを変更したので、伴ってUserIDの選択リストを変更する
        '''

        url = self.m_comboBoxUpdateURL.GetValue()
        idsAndtokens = self.UserList[url]
        userid_choice = []
        # userid 選択肢構築
        for item in idsAndtokens:
            userid_choice.append(item.split(":")[0])

        self.m_comboBoxUpdateUserID.Clear()
        self.m_comboBoxUpdateUserID.SetItems(userid_choice)
        self.m_comboBoxUpdateUserID.SetSelection(0)
        self.m_comboBoxUpdateUserIDOnCombobox(None)

        if event is not None:
            event.Skip()

    def m_comboBoxReferenceURLOnCombobox( self, event ):
        '''
        参照系のURLを変更したので、伴ってUserIDの選択リストを変更する
        '''

        url = self.m_comboBoxReferenceURL.GetValue()
        idsAndtokens = self.UserList[url]
        userid_choice = []
        # userid 選択肢構築
        for item in idsAndtokens:
            userid_choice.append(item.split(":")[0])

        self.m_comboBoxReferenceUserID.Clear()
        #print("userid_choice = %s"%userid_choice)
        self.m_comboBoxReferenceUserID.SetItems(userid_choice)
        self.m_comboBoxReferenceUserID.SetSelection(0)
        self.m_comboBoxReferenceUserIDOnCombobox(None)

        if event is not None:
            event.Skip()

    def m_comboBoxReferenceUserIDOnCombobox( self, event ):
        '''
        参照系のUserIDを変更したので、対応するトークンをセット
        '''

        username = self.m_comboBoxReferenceUserID.GetValue()
        url = self.m_comboBoxReferenceURL.GetValue()
        ids = self.UserList[url]
        #if ids.has_key(username) is True:
        if (username in ids) is True:
            self.m_staticTextReferenceUserID.SetLabel(ids[username].split(":")[0])
            self.m_textCtrlReferenceAccessToken.SetValue(ids[username].split(":")[1])

        if event is not None:
            event.Skip()
    
    def m_comboBoxUpdateUserIDOnCombobox( self, event ):
        '''
        更新系のUserIDを変更したので、対応するトークンをセット
        '''

        username = self.m_comboBoxUpdateUserID.GetValue()
        url = self.m_comboBoxUpdateURL.GetValue()
        ids = self.UserList[url]
        #if ids.has_key(username) is True:
        if (username in ids) is True:
            self.m_staticTextUpdateUserID.SetLabel(ids[username].split(":")[0])
            self.m_textCtrlUpdateAccessToken.SetValue(ids[username].split(":")[1])

        if event is not None:
            event.Skip()

    def m_buttonDescriptorBrowseUpdateOnButtonClick( self, event ):
        '''
        更新系の記述子リストのファイル名指定。
        '''

        filename_dialog = wx.FileDialog(self, u"記述子登録用構成ファイルの名前を指定してください。", self.upd_workdir, u"", u"conf file (*.conf) |*.conf| All file (*.*)|*.*", style=wx.FD_OPEN)
        if filename_dialog.ShowModal() == wx.ID_OK:
            filename = filename_dialog.GetFilename()
            self.m_textCtrlDescriptorFileNameUpdate.SetValue(filename)

    def m_buttonPredictionBrowsUpdateOnButtonClick( self, event ):
        '''
        更新系の予測モデルリストのファイル名指定。
        '''
        filename_dialog = wx.FileDialog(self, u"予測モデル登録用構成ファイルの名前を指定してください。", self.upd_workdir, u"", u"conf file (*.conf) |*.conf| All file (*.*)|*.*", style=wx.FD_OPEN)
        if filename_dialog.ShowModal() == wx.ID_OK:
            filename = filename_dialog.GetFilename()
            self.m_textCtrlPredictionModelFilenameUpdate.SetValue(filename)

    def m_buttonSoftwareToolBrowseUpdateOnButtonClick( self, event ):
        '''
        更新系のソフトウェアツールリストのファイル名指定。
        '''
        filename_dialog = wx.FileDialog(self, u"ソフトウェアツール登録用構成ファイルの名前を指定してください。", self.upd_workdir, u"", u"conf file (*.conf) |*.conf| All file (*.*)|*.*", style=wx.FD_OPEN)
        if filename_dialog.ShowModal() == wx.ID_OK:
            filename = filename_dialog.GetFilename()
            self.m_textCtrlSoftwareToolFilenameUpdate.SetValue(filename)

    def m_buttonDescriptorBrowseRefOnButtonClick( self, event ):
        '''
        参照系の記述子リストのファイル名指定。
        '''
        filename_dialog = wx.FileDialog(self, u"記述子取り出し用の構成ファイルの名前を指定してください。", self.ref_workdir, u"", u"conf file (*.conf) |*.conf| All file (*.*)|*.*", style=wx.FD_OPEN)
        if filename_dialog.ShowModal() == wx.ID_OK:
            filename = filename_dialog.GetFilename()
            self.m_textCtrlDescriptorFileNameRef.SetValue(filename)

    def m_buttonPredictionBrowsRefOnButtonClick( self, event ):
        '''
        参照系の予測モデルリストのファイル名指定。
        '''
        filename_dialog = wx.FileDialog(self, u"予測モデル取り出し用の構成ファイルの名前を指定してください。", self.ref_workdir, u"", u"conf file (*.conf) |*.conf| All file (*.*)|*.*", style=wx.FD_OPEN)
        if filename_dialog.ShowModal() == wx.ID_OK:
            filename = filename_dialog.GetFilename()
            self.m_textCtrlPredictionModelFilenameRef.SetValue(filename)

    def m_buttonSoftwareToolBrowseRefOnButtonClick( self, event ):
        '''
        参照系のソフトウェアツールリストのファイル名指定。
        '''
        filename_dialog = wx.FileDialog(self, u"ソフトウェアツール取り出し用の構成ファイルの名前を指定してください。", self.ref_workdir, u"", u"conf file (*.conf) |*.conf| All file (*.*)|*.*", style=wx.FD_OPEN)
        if filename_dialog.ShowModal() == wx.ID_OK:
            filename = filename_dialog.GetFilename()
            self.m_textCtrlSoftwareToolFilenameRef.SetValue(filename)

    def m_buttonModuleXMLBrowseUpdateOnButtonClick( self, event ):
        '''
        予測モジュールXMLディレクトリの指定
        '''
        #filename_dialog = wx.FileDialog(self, u"予測モジュールのファイル名を指定してください。", self.upd_workdir, u"", u"XML file (*.xml) |*.xml| All file (*.*)|*.*", style=wx.FD_OPEN)
        rfolder = wx.DirDialog(self, u"予測モジュールが格納されているディレクトリの指定", defaultPath=self.upd_workdir)
        if rfolder.ShowModal() == wx.ID_OK:
            dirname = rfolder.GetPath()
            self.m_textCtrlModulesXMLUpdate.SetValue(dirname)
            self.modulesxml = self.m_textCtrlModulesXMLUpdate.GetValue()


    def m_buttonFoldersBorwsUpdateOnButtonClick( self, event ):
        '''
        更新系の辞書・フォルダー情報を格納したファイルの指定
        '''

        filename_dialog = wx.FileDialog(self, u"辞書・フォルダー情報のファイル名を指定してください。", self.upd_workdir, u"", u"JSON file (*.json) |*.json| All file (*.*)|*.*", style=wx.FD_OPEN)
        if filename_dialog.ShowModal() == wx.ID_OK:
            filename = filename_dialog.GetFilename()
            self.m_textCtrlFoldersFilenameUpdate.SetValue(filename)

    def m_buttonFoldersBrowsRefOnButtonClick( self, event ):
        '''
        参照系の辞書・フォルダー情報を格納したファイルの指定
        '''
        filename_dialog = wx.FileDialog(self, u"辞書・フォルダー情報のファイル名を指定してください。", self.ref_workdir, u"", u"JSON file (*.json) |*.json| All file (*.*)|*.*", style=wx.FD_OPEN)
        if filename_dialog.ShowModal() == wx.ID_OK:
            filename = filename_dialog.GetFilename()
            self.m_textCtrlFoldersFilenameRef.SetValue(filename)

    #------------------ここまでイベントハンドラ----------------------
    #------------------ここからメンバー関数--------------------------
    def divideInventories(self):
        '''
        カレントディレクトリにある各Inventoryを出力したJSONファイルを分解して、更新に備える。
        1, 記述子、予測モデル、ソフトウェアツールのJSONをID毎のファイルに分解する。
        2, 平行して記述子、予測モデル、ソフトウェアツールの更新用構成ファイルを分解したjsonファイルを使用して作成する。
        '''

        okConvert = True
        if os.path.exists(self.descriptor_ref_json) is False:
            okConvert = False
        if os.path.exists(self.prediction_ref_json) is False:
            okConvert = False
        if os.path.exists(self.software_tool_ref_json) is False:
            okConvert = False

        if okConvert is False:
            dialog = wx.MessageDialog(self, u"必要なファイル(*.json)がありません", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return

        userid, token = self.CheckUserIDAndToken()

        analyze_inventory_json(self.descriptor_ref_json, self.prediction_ref_json, self.software_tool_ref_json, self.descriptor_upd_conf, self.prediction_upd_conf, self.software_tool_upd_conf)

    def InitializeRefListCtrl(self):
        '''
        参照側辞書・フォルダーのツリーを初期化する
        @param なし
        @retval なし
        '''

        self.m_treeCtrlSelections.DeleteAllItems()
        self.root = self.m_treeCtrlSelections.AddRoot("Root", self.root_pict, -1, None)

        return

    def InitializeUpdListCtrl(self):
        '''
        更新側辞書・フォルダーのツリーを初期化する
        @param なし
        @retval なし
        '''

        self.m_treeCtrlSelectionsUpdate.DeleteAllItems()
        self.root = self.m_treeCtrlSelectionsUpdate.AddRoot("Root", self.root_pict, -1, None)

        return

    def AddDictionariesRefListCtrl(self):
        '''
        参照側、辞書・フォルダーのツリーに辞書を作成する。
        対象の辞書はself.ref_dictdict
        '''

        self.RefTree = {}
        for items in self.ref_dictdict:
            dict_id = None
            root_folder_id = None
            dict_instance = None
            for item in items:
                if item == "dictionary_name":
                    TreeItemData = wx.TreeItemData("Dummy")
                    #dict_instance = self.m_treeCtrlSelections.AppendItem(self.root, items[item], self.dir_pict, -1, TreeItemData)
                    dict_instance = self.m_treeCtrlSelections.AppendItem(self.root, items[item], self.dir_pict, -1)
                    #print ("%20s : %s"%(item, items[item]))
                if item == "dictionary_id":
                    dict_id = items[item].split("/")[-1]
                if item == "root_folder_id":
                    root_folder_id  = items[item].split("/")[-1]
            if root_folder_id is not None and dict_instance is not None:
                TreeItemData = wx.TreeItemData([dict_id, root_folder_id])
                self.m_treeCtrlSelections.SetItemData(dict_instance, TreeItemData)
                self.RefTree[root_folder_id] = dict_instance
            else:
                print("IDか名前が無かったためにツリーが作成されませんでした。(%s)"%str(items))

        #for item in self.RefTree:
        #    print("id = %s / instance = %s"%(item, self.RefTree[item]))
        self.m_treeCtrlSelections.Expand(self.root)
        return

    def AddFoldersRefListCtrl(self, all_folders):
        '''
        参照側。既存のツリー配下に同じフォルダIDを親に持つフォルダーをぶら下げる
        @param all_folders(dict)
        @retval なし
        '''

        for item in all_folders:
            items = all_folders[item]
            #print("id = %s / folders = %s"%(item, items))
            if len(items) != 1:
                items = items[1:][0]
                #if self.RefTree.has_key(item) is True:
                if (item in self.RefTree) is True:
                    #print("create subtree under the folder id(%s)"%item)
                    for subitem1 in items:
                        #print("subitem1 = %s"%subitem1)
                        if sys.version_info[0] <= 2:
                            dict_id = self.m_treeCtrlSelections.GetItemData(self.RefTree[item]).GetData()[0]
                        else:
                            dict_id = self.m_treeCtrlSelections.GetItemData(self.RefTree[item])[0]
                        print("dict_id = %s"%str(dict_id))
                        TreeItemData = wx.TreeItemData([dict_id, subitem1])
                        tree_item = self.m_treeCtrlSelections.AppendItem(self.RefTree[item],
                                                                         items[subitem1][0],
                                                                         self.dir_pict,
                                                                         -1,
                                                                         TreeItemData)
                        if len(items[subitem1]) == 1:
                            pass
                        else:
                            self.AddFoldersRefListCtrlSub(tree_item, dict_id, items[subitem1])

    def AddFoldersRefListCtrlSub(self, tree_item, dict_id, folders):
        '''
        参照側。tree_itemのツリーにfoldersにあるIDを親にもつフォルダをぶら下げる
        @param tree_item(TreeCtrlのAppendItemされたインスタンス)
        @param folders(dict)
        @retval なし
        '''

        folders = folders[1:][0]
        for item in folders:
            #print("folders = %s"%folders)
            TreeItemData = wx.TreeItemData([dict_id, item])
            sub_tree_item = self.m_treeCtrlSelections.AppendItem(tree_item,
                                                             folders[item][0],
                                                             self.dir_pict,
                                                             -1,
                                                             TreeItemData)
            if len(folders[item]) != 1:
                self.AddFoldersRefListCtrlSub(sub_tree_item, dict_id, folders[item])

    def AddDictionariesUpdListCtrl(self):
        '''
        更新側、辞書・フォルダーのツリーに辞書を作成する。
        対象の辞書はself.ref_dictdict
        '''

        self.UpdTree = {}
        for items in self.upd_dictdict:
            dict_id = None
            root_folder_id = None
            dict_instance = None
            for item in items:
                if item == "dictionary_name":
                    #TreeItemData = wx.TreeItemData()
                    TreeItemData = wx.TreeItemData("Dummy")
                    #dict_instance = self.m_treeCtrlSelectionsUpdate.AppendItem(self.root, items[item], self.dir_pict, -1, TreeItemData)
                    dict_instance = self.m_treeCtrlSelectionsUpdate.AppendItem(self.root, items[item], self.dir_pict, -1)
                    print ("%20s : %s"%(item, items[item]))
                if item == "dictionary_id":
                    dict_id = items[item].split("/")[-1]
                if item == "root_folder_id":
                    root_folder_id  = items[item].split("/")[-1]
            if root_folder_id is not None and dict_instance is not None:
                TreeItemData = wx.TreeItemData([dict_id, root_folder_id])
                self.m_treeCtrlSelectionsUpdate.SetItemData(dict_instance, TreeItemData)
                self.UpdTree[root_folder_id] = dict_instance
            else:
                print("IDか名前が無かったためにツリーが作成されませんでした。(%s)"%str(items))

        self.m_treeCtrlSelectionsUpdate.Expand(self.root)
        return

    def AddFoldersUpdListCtrl(self, all_folders):
        '''
        更新側。既存のツリー配下に同じフォルダIDを親に持つフォルダーをぶら下げる
        @param all_folders(dict)
        @retval なし
        '''

        for item in all_folders:
            items = all_folders[item]
            #print("id = %s / folders = %s"%(item, items))
            if len(items) != 1:
                items = items[1:][0]
                #if self.UpdTree.has_key(item) is True:
                if (item in self.UpdTree) is True:
                    #print("create subtree under the folder id(%s)"%item)
                    for subitem1 in items:
                        #print("subitem1 = %s"%subitem1)
                        if sys.version_info[0] <= 2:
                            dict_id = self.m_treeCtrlSelectionsUpdate.GetItemData(self.UpdTree[item]).GetData()[0]
                        else:
                            dict_id = self.m_treeCtrlSelectionsUpdate.GetItemData(self.UpdTree[item])[0]
                        TreeItemData = wx.TreeItemData([dict_id, subitem1])
                        tree_item = self.m_treeCtrlSelectionsUpdate.AppendItem(self.UpdTree[item],
                                                                         items[subitem1][0],
                                                                         self.dir_pict,
                                                                         -1,
                                                                         TreeItemData)
                        if len(items[subitem1]) == 1:
                            pass
                        else:
                            self.AddFoldersUpdListCtrlSub(tree_item, dict_id, items[subitem1])

    def AddFoldersUpdListCtrlSub(self, tree_item, dict_id, folders):
        '''
        更新側。tree_itemのツリーにfoldersにあるIDを親にもつフォルダをぶら下げる
        @param tree_item(TreeCtrlのAppendItemされたインスタンス)
        @param folders(dict)
        @retval なし
        '''

        folders = folders[1:][0]
        for item in folders:
            #print("folders = %s"%folders)
            TreeItemData = wx.TreeItemData([dict_id, item])
            sub_tree_item = self.m_treeCtrlSelectionsUpdate.AppendItem(tree_item,
                                                             folders[item][0],
                                                             self.dir_pict,
                                                             -1,
                                                             TreeItemData)
            if len(folders[item]) != 1:
                self.AddFoldersUpdListCtrlSub(sub_tree_item, dict_id, folders[item])

    def readIniFile(self):
        '''
        保存値の読み込み
        '''

        if sys.version_info[0] <= 2:
            parser = ConfigParser.SafeConfigParser()
        else:
            parser = configparser.ConfigParser()

        inifilename = "./inventory-operator.ini"
        #inifilename = "Inventory.conf"
        if os.path.exists(inifilename) is False:             # 存在しない場合、雛形をコピーして使用
            shutil.copy("inventory-operator.template", inifilename)

        parser.read(inifilename)

        savevalue = {}
        if parser.has_section("System") is True:
            if parser.has_option("System", "modulecopy") is True:
                self.modulecopy_directory = parser.get("System", "modulecopy")
            if parser.has_option("System", "inventory_management") is True:
                self.inventory_management = parser.get("System", "inventory_management")
                sys.path.append(self.inventory_management)
                #from invenrory_ids import *
                self.inventory_management_package = import_module("inventory_ids")
                self.inventory_management_package.setDbDirectory(self.inventory_management)
        if parser.has_section("Reference") is True:
            savevalue["Reference"] = {}
            if parser.has_option("Reference", "URL") is True:
                savevalue["Reference"]["URL"] = parser.get("Reference", "URL")
            if parser.has_option("Reference", "ConfFile") is True:
                savevalue["Reference"]["ConfFile"] = parser.get("Reference", "ConfFile")
                print("Reference/ConfFile = %s"%parser.get("Reference", "ConfFile"))
            if parser.has_option("Reference", "UserID") is True:
                savevalue["Reference"]["UserID"] = parser.get("Reference", "UserID")
            if parser.has_option("Reference", "Token") is True:
                savevalue["Reference"]["Token"] = parser.get("Reference", "Token")
            if parser.has_option("Reference", "descriptor_conf") is True:
                savevalue["Reference"]["descriptor_conf"] = parser.get("Reference", "descriptor_conf")
            if parser.has_option("Reference", "prediction_conf") is True:
                savevalue["Reference"]["prediction_conf"] = parser.get("Reference", "prediction_conf")
            if parser.has_option("Reference", "software_tool_conf") is True:
                savevalue["Reference"]["software_tool_conf"] = parser.get("Reference", "software_tool_conf")
            if parser.has_option("Reference", "folder_info") is True:
                savevalue["Reference"]["folder_info"] = parser.get("Reference", "folder_info")
        if parser.has_section("Update") is True:
            savevalue["Update"] = {}
            if parser.has_option("Update", "URL") is True:
                savevalue["Update"]["URL"] = parser.get("Update", "URL")
            if parser.has_option("Update", "ConfFile") is True:
                savevalue["Update"]["ConfFile"] = parser.get("Update", "ConfFile")
            if parser.has_option("Update", "UserID") is True:
                savevalue["Update"]["UserID"] = parser.get("Update", "UserID")
            if parser.has_option("Update", "Token") is True:
                savevalue["Update"]["Token"] = parser.get("Update", "Token")
            if parser.has_option("Update", "descriptor_conf") is True:
                savevalue["Update"]["descriptor_conf"] = parser.get("Update", "descriptor_conf")
            if parser.has_option("Update", "prediction_conf") is True:
                savevalue["Update"]["prediction_conf"] = parser.get("Update", "prediction_conf")
            if parser.has_option("Update", "software_tool_conf") is True:
                savevalue["Update"]["software_tool_conf"] = parser.get("Update", "software_tool_conf")
            if parser.has_option("Update", "folder_info") is True:
                savevalue["Update"]["folder_info"] = parser.get("Update", "folder_info")
            if parser.has_option("Update", "modules_xml_info") is True:
                savevalue["Update"]["modules_xml_info"] = parser.get("Update", "modules_xml_info")

        servers = ""
        if parser.has_section("Servers") is True:
            if parser.has_option("Servers", "servers") is True:
                servers = parser.get("Servers", "servers").split()

        if len(servers) != 0:
            self.m_comboBoxReferenceURL.Clear()
            self.m_comboBoxReferenceURL.SetValue("")
            self.m_comboBoxUpdateURL.Clear()
            self.m_comboBoxUpdateURL.SetValue("")
            self.m_comboBoxReferenceURL.SetItems(servers)
            self.m_comboBoxUpdateURL.SetItems(servers)

        for item in servers:
            #print("server : %s"%item)
            if parser.has_section(item) is True:
                self.UserList[item] = {}
                self.VersionList[item] = {}
                usernames = userids = tokenlist = None
                if parser.has_option(item, "username") is True:
                    usernames = parser.get(item, "username").split(",")
                if parser.has_option(item, "userid") is True:
                    userids = parser.get(item, "userid").split()
                if parser.has_option(item, "token") is True:
                    tokenlist = parser.get(item, "token").split()
                if usernames is not None and userids is not None and tokenlist is not None:
                    for i in range(len(usernames)):
                        self.UserList[item][usernames[i]] = userids[i] + ":" + tokenlist[i]
                version = "3.0"
                if parser.has_option(item, "ref_version") is True:
                    version = parser.get(item, "ref_version")
                    self.VersionList[item]["ref_version"] = version
                if parser.has_option(item, "upd_version") is True:
                    version = parser.get(item, "upd_version")
                    self.VersionList[item]["upd_version"] = version

        if ("Reference" in savevalue) is True:
            if ("UserID" in savevalue["Reference"]) is True:
                if savevalue["Reference"]["UserID"] is not None: 
                    self.m_comboBoxReferenceUserID.SetValue(savevalue["Reference"]["UserID"])
                    self.userid_ref = savevalue["Reference"]["UserID"]
            if ("URL" in savevalue["Reference"]) is True:
                if savevalue["Reference"]["URL"] != "":
                    self.m_comboBoxReferenceURL.SetValue(savevalue["Reference"]["URL"])
                    self.url_ref = savevalue["Reference"]["URL"]
                    self.m_comboBoxReferenceURLOnCombobox(None)
            if ("Token" in savevalue["Reference"]) is True:
                if savevalue["Reference"]["Token"] != "":
                    self.m_textCtrlReferenceAccessToken.SetValue(savevalue["Reference"]["Token"])
                    self.token_ref = savevalue["Reference"]["Token"]
            if ("ConfFile" in savevalue["Reference"]) is True:
                if savevalue["Reference"]["ConfFile"] != "":
                    self.m_textCtrlConfFileNameSave.SetValue(savevalue["Reference"]["ConfFile"])
                    self.ref_workdir = savevalue["Reference"]["ConfFile"]
            if ("descriptor_conf" in savevalue["Reference"]) is True:
                if savevalue["Reference"]["descriptor_conf"] != "":
                    self.descriptor_ref_conf = savevalue["Reference"]["descriptor_conf"]
            if ("prediction_conf" in savevalue["Reference"]) is True:
                if savevalue["Reference"]["prediction_conf"] != "":
                    self.prediction_ref_conf = savevalue["Reference"]["prediction_conf"]
            if ("software_tool_conf" in savevalue["Reference"]) is True:
                if savevalue["Reference"]["software_tool_conf"] != "":
                    self.software_tool_ref_conf = savevalue["Reference"]["software_tool_conf"]
            if ("folder_info" in savevalue["Reference"]) is True:
                if savevalue["Reference"]["folder_info"] != "":
                    self.folders_ref = savevalue["Reference"]["folder_info"]
        if ("Update" in savevalue) is True:
            if ("UserID" in savevalue["Update"]) is True:
                if savevalue["Update"]["UserID"] is not None: 
                    self.m_comboBoxUpdateUserID.SetValue(savevalue["Update"]["UserID"])
                    self.userid_upd = savevalue["Update"]["UserID"]
            if ("URL" in savevalue["Update"]) is True:
                if savevalue["Update"]["URL"] != "":
                    self.m_comboBoxUpdateURL.SetValue(savevalue["Update"]["URL"])
                    self.url_upd = savevalue["Update"]["URL"]
                    self.m_comboBoxUpdateURLOnCombobox(None)
            if ("Token" in savevalue["Update"]) is True:
                if savevalue["Update"]["Token"] != "":
                    self.m_textCtrlUpdateAccessToken.SetValue(savevalue["Update"]["Token"])
                    self.token_upd = savevalue["Update"]["Token"]
            if ("ConfFile" in savevalue["Update"]) is True:
                if savevalue["Update"]["ConfFile"] != "":
                    self.m_textCtrlConfFileNameRead.SetValue(savevalue["Update"]["ConfFile"])
                    self.upd_workdir = savevalue["Update"]["ConfFile"]
            if ("descriptor_conf" in savevalue["Update"]) is True:
                if savevalue["Update"]["descriptor_conf"] != "":
                    self.descriptor_upd_conf = savevalue["Update"]["descriptor_conf"]
            if ("prediction_conf" in savevalue["Update"]) is True:
                if savevalue["Update"]["prediction_conf"] != "":
                    self.prediction_upd_conf = savevalue["Update"]["prediction_conf"]
            if ("software_tool_conf" in savevalue["Update"]) is True:
                if savevalue["Update"]["software_tool_conf"] != "":
                    self.software_tool_upd_conf = savevalue["Update"]["software_tool_conf"]
            if ("folder_info" in savevalue["Update"]) is True:
                if savevalue["Update"]["folder_info"] != "":
                    self.folders_upd = savevalue["Update"]["folder_info"]
            if ("modules_xml_info" in savevalue["Update"]) is True:
                if savevalue["Update"]["modules_xml_info"] != "":
                    self.modulesxml = savevalue["Update"]["modules_xml_info"]

        #print self.UserList
        #print self.VersionList
        return savevalue

    def readConfigFile(self):
        '''
        インベントリ操作用Configファイルの内容を取得する
        '''

        if sys.version_info[0] <= 2:
            parser = ConfigParser.SafeConfigParser()
        else:
            parser = configparser.ConfigParser()

        conffilename = os.path.join(self.workdir, CONFIG_FILENAME)
        if os.path.exists(conffilename) is True:
            parser.read(conffilename)
        else:
            return

    def MakeConfigFile(self, userid, token, path, workdir, query=None):
        '''
        インベントリ操作用Configファイルの作成(存在すれば編集)
        '''

        if sys.version_info[0] <= 2:
            parser = ConfigParser.SafeConfigParser()
        else:
            parser = configparser.ConfigParser()

        conffilename = os.path.join(workdir, CONFIG_FILENAME)
        if os.path.exists(conffilename) is True:
            parser.read(conffilename)

        if parser.has_section("authorize") is False:
            parser.add_section("authorize")
        parser.set("authorize", "user_id", userid)
        parser.set("authorize", "token", token)

        if parser.has_section("resource") is False:
            parser.add_section("resource")
        parser.set("resource", "url", path)
        if query is None:
            query = ""
        parser.set("resource", "query", query)

        if parser.has_section("file") is False:
            parser.add_section("file")

        parser.set("file", "object", "descriptor\n       prediction-model\n       software-tool")
        parser.set("file", "inputfile", "%s\n          %s\n          %s"%(self.descriptor_ref_json, self.prediction_ref_json, self.software_tool_ref_json))
        parser.set("file", "outputfile", "%s\n           %s\n           %s"%(self.descriptor_ref_json, self.prediction_ref_json, self.software_tool_ref_json))
        parser.set("file", "modules.xml", "%s"%self.modulesxml)
        parser.set("file", "folders_ref", "%s"%self.folders_ref)
        parser.set("file", "folders_update", "%s"%self.folders_upd)

        conffile = open(conffilename, "w")
        parser.write(conffile)
        conffile.close()

    def CheckUserIDAndToken(self):
        '''
        参照用ユーザーIDとTokenの確認
        '''

        # 認証
        passwd = self.m_textCtrlReferencePasswd.GetValue()
        username = self.m_textCtrlReferenceUserName.GetValue()
        if passwd == "" or username == "":
            dialog = wx.MessageDialog(self, u"User Nameかパスワードが空です", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False
        server = self.m_comboBoxReferenceURL.GetValue()

        print("server = %s"%server)
        ret, uid, token = openam_operator.miauth(server, username, passwd, debug=5)

        if ret is False:
            dialog = wx.MessageDialog(self, u"ユーザー認証に失敗しました", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False

        self.m_staticTextReferenceUserID.SetLabel(uid)
        token = self.m_textCtrlReferenceAccessToken.SetValue(token)

        userid = self.m_staticTextReferenceUserID.GetLabel()
        if userid is None or userid == "":
            dialog = wx.MessageDialog(self, u"UserIDが空です", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False
        token = self.m_textCtrlReferenceAccessToken.GetValue()
        if token is None or token == "":
            dialog = wx.MessageDialog(self, u"Tokenが空です", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False

        return userid, token

    def CheckUpdateUserIDAndToken(self):
        '''
        更新用ユーザーIDとTokenの確認
        '''

        # 認証
        passwd = self.m_textCtrlUpdatePasswd.GetValue()
        username = self.m_textCtrlUpdateUserName.GetValue()
        if passwd == "" or username == "":
            dialog = wx.MessageDialog(self, u"User Nameかパスワードが空です", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False
        server = self.m_comboBoxUpdateURL.GetValue()

        ret, uid, token = openam_operator.miauth(server, username, passwd)

        if ret is False:
            dialog = wx.MessageDialog(self, u"ユーザー認証に失敗しました", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False

        self.m_staticTextUpdateUserID.SetLabel(uid)
        token = self.m_textCtrlUpdateAccessToken.SetValue(token)

        userid = self.m_staticTextUpdateUserID.GetLabel()
        if userid is None or userid == "":
            dialog = wx.MessageDialog(self, u"UserIDが空です", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False
        token = self.m_textCtrlUpdateAccessToken.GetValue()
        if token is None or token == "":
            dialog = wx.MessageDialog(self, u"Tokenが空です", "Error", style=wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
            return False, False

        return userid, token

def main():
    '''
    開始点
    '''

    params_len = len(sys.argv)
    #print("params_len = %d"%params_len)

    # デフォルト値
    descriptor_list = "src_descriptor.json"
    prediction_list = "src_prediction.json"
    software_tool_list = "src_software_tool.json"
    folders_list = "src_folders.json"
    modules_xml = "modules.xml"
    debug_mode = False
    for items in sys.argv:
        items = items.split(":")
        if items[0] == "debug":
            debug_mode = True

    app = wx.App(False)
    org = InventoryOperator(None, descriptor_list, prediction_list, software_tool_list, modules_xml=modules_xml, folders_ref_json=folders_list, debug_mode=debug_mode)
    org.Show()

    app.MainLoop()

if __name__ == '__main__':
    main()
