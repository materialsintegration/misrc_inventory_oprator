#!/usr/local/python2.7/bin/python
# -*- coding: utf-8 -*-

'''
NIMS野口さん作成のインベントリAPIプログラムのラッパープログラム
'''

from InventoryOperatorGui import *
import sys, os
import ast
import time
import json
import datetime
import codecs
import requests
if sys.version_info[0] <= 2:
    import ConfigParser
    #from urlparse import urlparse
else:
    import configparser
    #from urllib.parse import urlparse

from getInventory import *
from postInventory4 import *

ROOT_FOLDER = "root_forder"                     # 2018/08/15:folder->forder
CONFIG_FILENAME = "Inventory.conf"              # 入出力用コンフィグファイルの名前

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

    def __init__(self, parent):
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

        inifilename = "inventory-operator.ini"
        if os.path.exists(inifilename) is True:
            print "found init file"
            infile = open(inifilename)
            lines = infile.read()
            init_dic = ast.literal_eval(lines)
            if init_dic.has_key("Reference") is True:
                if init_dic["Reference"].has_key("UserID") is True:
                    if init_dic["Reference"]["UserID"] is not None: 
                        self.m_textCtrlReferenceUserID.SetValue(init_dic["Reference"]["UserID"])
                        self.userid_ref = init_dic["Reference"]["UserID"]
                    if init_dic["Reference"]["Token"] is not None: 
                        self.m_textCtrlReferenceAccessToken.SetValue(init_dic["Reference"]["Token"])
                        self.token_ref = init_dic["Reference"]["Token"]
                    if init_dic["Reference"]["URL"] is not None:
                        self.m_comboBoxReferenceURL.SetValue(init_dic["Reference"]["URL"])
                        self.url_ref = init_dic["Reference"]["URL"]
                    if init_dic["Reference"]["ConfFile"] is not None:
                        self.m_textCtrlConfFileNameSave.SetValue(init_dic["Reference"]["ConfFile"])
                        self.conffilesave = init_dic["Reference"]["ConfFile"]
            if init_dic.has_key("Update") is True:
                if init_dic["Update"].has_key("UserID") is True:
                    if init_dic["Update"]["UserID"] is not None: 
                        self.m_textCtrlUpdateUserID.SetValue(init_dic["Update"]["UserID"])
                        self.userid_upd = init_dic["Update"]["UserID"]
                    if init_dic["Update"]["Token"] is not None: 
                        self.m_textCtrlUpdateAccessToken.SetValue(init_dic["Update"]["Token"])
                        self.token_upd = init_dic["Update"]["Token"]
                    if init_dic["Update"]["URL"] is not None:
                        self.m_comboBoxUpdateURL.SetValue(init_dic["Update"]["URL"])
                        self.url_upd = init_dic["Update"]["URL"]
                    if init_dic["Update"]["ConfFile"] is not None:
                        self.m_textCtrlConfFileNameRead.SetValue(init_dic["Update"]["ConfFile"])
                        self.conffileread = init_dic["Update"]["ConfFile"]

        # ListCtrl準備
        self.imageList = wx.ImageList(16,16)
        self.root_pict = self.imageList.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16,16)))
        self.dir_pict = self.imageList.Add(wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR, wx.ART_OTHER, (16,16)))
        self.file_pict = self.imageList.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16,16)))
        self.root = None
        self.RefTree = {}
        self.UpdTree = {}

        self.DictionaryFoldersID = None
        self.DictionaryFoldersIDUpdate = None

        self.infilefilter = "All Files (*.*) |*.*"
        self.workdir = "./"                         # working directory name

        self.InitializeRefListCtrl()
        self.InitializeUpdListCtrl()

    #------------------ここからイベントハンドラ----------------------
    def InventoryOperatorGUIOnClose( self, event ):
        '''
        終了時の挙動
        '''

        init_dict = {}
        ref_dict = {}
        upd_dict = {}
        self.userid_ref = self.m_textCtrlReferenceUserID.GetValue()
        ref_dict["UserID"] = self.userid_ref
        self.token_ref = self.m_textCtrlReferenceAccessToken.GetValue()
        ref_dict["Token"] = self.token_ref
        self.url_ref = self.m_comboBoxReferenceURL.GetValue()
        ref_dict["URL"] = self.url_ref
        self.conffilesave = self.m_textCtrlConfFileNameSave.GetValue()
        ref_dict["ConfFile"] = self.conffilesave
        init_dict["Reference"] = ref_dict
        self.userid_upd = self.m_textCtrlUpdateUserID.GetValue()
        upd_dict["UserID"] = self.userid_upd
        self.token_upd = self.m_textCtrlUpdateAccessToken.GetValue()
        upd_dict["Token"] = self.token_upd
        self.url_upd = self.m_comboBoxUpdateURL.GetValue()
        upd_dict["URL"] = self.url_upd
        self.conffileread = self.m_textCtrlConfFileNameRead.GetValue()
        upd_dict["ConfFile"] = self.conffileread
        init_dict["Update"] = upd_dict
        

        outfile = open("inventory-operator.ini", "w")
        outfile.write(str(init_dict))
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
        weburl = referenceURL + '/inventory-api/v3/users/' + userid + '/dictionaries'

        ret = self.InventoryGet(token, weburl)

        self.ref_dictdict = ret["dictionaries"]

        self.InitializeRefListCtrl()
        self.AddDictionariesRefListCtrl()

        all_folders = {}
        for items in self.ref_dictdict:
            for item in items:
                if item == "dictionary_id":
                    weburl = referenceURL + '/inventory-api/v3/users/' + userid + '/dictionaries/' + items[item].split("/")[-1]
                    ret = self.InventoryGet(token, weburl)

                    if ret.has_key(ROOT_FOLDER) is True:
                        items2 = ret[ROOT_FOLDER]
                        #print items2
                        folders = folder_print(items2, "")
                        if len(folders) != 0:
                            for folder in folders:
                                all_folders[folder] = folders[folder]

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
        weburl = updateURL + '/inventory-api/v3/users/' + userid + '/dictionaries'

        ret = self.InventoryGet(token, weburl)

        self.upd_dictdict = ret["dictionaries"]

        self.InitializeUpdListCtrl()
        self.AddDictionariesUpdListCtrl()

        all_folders = {}
        for items in self.upd_dictdict:
            for item in items:
                if item == "dictionary_id":
                    weburl = updateURL + '/inventory-api/v3/users/' + userid + '/dictionaries/' + items[item].split("/")[-1]
                    ret = self.InventoryGet(token, weburl)

                    if ret.has_key(ROOT_FOLDER) is True:
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

        path = "users/" + self.m_textCtrlReferenceUserID.GetValue() + "/" + path
        self.MakeConfigFile(userid, token, path)

        url = self.m_comboBoxReferenceURL.GetValue()

        getInventory_main(url)

        event.Skip()

    def m_buttonInventoryUpdateOnButtonClick( self, event ):
        '''
        インベントリ情報の登録
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

        path = "users/" + self.m_textCtrlUpdateUserID.GetValue() + "/" + path
        self.MakeConfigFile(userid, token, path)

        url = self.m_comboBoxUpdateURL.GetValue()
        url = url + "/inventory-update-api/v3"

        postInventory_main(url)

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

        rfolder = wx.DirDialog(self, u"Config File Name for Reference", defaultPath=self.workdir)
        if rfolder.ShowModal() == wx.ID_OK:
            self.workdir = rfolder.GetPath()
            self.m_textCtrlConfFileNameSave.SetValue(self.workdir)

        rfolder.Destroy()

        event.Skip()
    
    def m_buttonBrowseConfFileReadOnButtonClick( self, event ):
        '''
        Update用作業ディレクトリの指定
        '''

        rfolder = wx.DirDialog(self, u"Config File Name for Reference", defaultPath=self.workdir)
        if rfolder.ShowModal() == wx.ID_OK:
            self.workdir = rfolder.GetPath()
            self.m_textCtrlConfFileNameRead.SetValue(self.workdir)

        rfolder.Destroy()

        event.Skip()
    
    def m_buttonDeleteInventoriesOnButtonClick( self, event ):
        '''
        インベントリ削除用ダイアログ
        '''

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
        data = self.m_treeCtrlSelections.GetItemData(selected).GetData()
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
    
    #------------------ここまでイベントハンドラ----------------------
    #------------------ここからメンバー関数--------------------------
    def InventoryGet(self, token, weburl, invdata=None):
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

        res = session.get(weburl, json=invdata, headers=headers)

        if str(res.status_code) != "200":
            print("error")
            print('status  : ' + str(res.status_code))
            print('body    : ' + res.text)
            print('-------------------------------------------------------------------')
            print('url     : ' + weburl)
            print('headers : ' + str(headers))
            return None

        #body_dict = ast.literal_eval(res.json())
        return res.json()

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
                    TreeItemData = wx.TreeItemData()
                    dict_instance = self.m_treeCtrlSelections.AppendItem(self.root, items[item], self.dir_pict, -1, TreeItemData)
                    print "%20s : %s"%(item, items[item])
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
                if self.RefTree.has_key(item) is True:
                    #print("create subtree under the folder id(%s)"%item)
                    for subitem1 in items:
                        #print("subitem1 = %s"%subitem1)
                        dict_id = self.m_treeCtrlSelections.GetItemData(self.RefTree[item]).GetData()[0]
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
                    TreeItemData = wx.TreeItemData()
                    dict_instance = self.m_treeCtrlSelectionsUpdate.AppendItem(self.root, items[item], self.dir_pict, -1, TreeItemData)
                    print "%20s : %s"%(item, items[item])
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
                if self.UpdTree.has_key(item) is True:
                    #print("create subtree under the folder id(%s)"%item)
                    for subitem1 in items:
                        #print("subitem1 = %s"%subitem1)
                        dict_id = self.m_treeCtrlSelectionsUpdate.GetItemData(self.UpdTree[item]).GetData()[0]
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

    def MakeConfigFile(self, userid, token, path, query=None):
        '''
        インベントリ操作用Configファイルの作成(存在すれば編集)
        '''

        if sys.version_info[0] <= 2:
            parser = ConfigParser.SafeConfigParser()
        else:
            parser = configparser.ConfigParser()

        conffilename = os.path.join(self.workdir, CONFIG_FILENAME)
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
        parser.set("file", "inputfile", "kushida_descriptors.json\n          kushida_prediction-models.json\n          kushida_software-tools.json")
        parser.set("file", "outputfile", "kushida_descriptors.json\n           kushida_prediction-models.json\n           kushida_software-tools.json")
        parser.set("file", "modules.xml", "modules_zeisei.xml")

        conffile = open(conffilename, "w")
        parser.write(conffile)
        conffile.close()

    def CheckUserIDAndToken(self):
        '''
        参照用ユーザーIDとTokenの確認
        '''
        userid = self.m_textCtrlReferenceUserID.GetValue()
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
        userid = self.m_textCtrlUpdateUserID.GetValue()
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
#    if params_len < 4:
#       print "python param_operater.py <src> <width %> <number> [d type] [seed]"
#       print "    src : \u5143\u306b\u3057\u305f\u3044\u5024"
#       print "    width: \u4e71\u6570\u767a\u751f\u306e\u5e45\uff08\uff05\uff09"
#       print "    number: \u4e71\u6570\u767a\u751f\u3055\u305b\u308b\u6570(int)"
#       print "    d type: \u5206\u5e03\u30bf\u30a4\u30d7\uff08\u30c7\u30d5\u30a9\u30eb\u30c8\u306fnormal\uff09"
#       print "    seed: \u4e71\u6570\u306e\u7a2e"

    app = wx.App(False)
    org = InventoryOperator(None)
    org.Show()

    app.MainLoop()

if __name__ == '__main__':
    main()
