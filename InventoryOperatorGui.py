# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Nov  6 2017)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class InventoryOperatorGUI
###########################################################################

class InventoryOperatorGUI ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Inventory Operator", pos = wx.DefaultPosition, size = wx.Size( 698,655 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		#self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_notebook2 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_panelInventoriReference = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self.m_panelInventoriReference, wx.ID_ANY, u"インベントリ取得" ), wx.VERTICAL )
		
		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_treeCtrlSelections = wx.TreeCtrl( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,200 ), wx.TR_DEFAULT_STYLE|wx.TR_HAS_BUTTONS|wx.TR_ROW_LINES|wx.TR_SINGLE )
		bSizer7.Add( self.m_treeCtrlSelections, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_buttonGetDictionary = wx.Button( sbSizer5.GetStaticBox(), wx.ID_ANY, u"辞書・フォルダ一覧", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer7.Add( self.m_buttonGetDictionary, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, 5 )
		
		
		sbSizer5.Add( bSizer7, 1, wx.EXPAND|wx.BOTTOM, 5 )
		
		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText31 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, u"辞書・フォルダーID:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )
		bSizer10.Add( self.m_staticText31, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticTextDictionaryAndFolderID = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticTextDictionaryAndFolderID.Wrap( -1 )
		bSizer10.Add( self.m_staticTextDictionaryAndFolderID, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer5.Add( bSizer10, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )
		
		fgSizer6 = wx.FlexGridSizer( 8, 4, 0, 0 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText291 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, u"設定ファイル", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText291.Wrap( -1 )
		fgSizer6.Add( self.m_staticText291, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrlConfFileNameSave = wx.TextCtrl( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer6.Add( self.m_textCtrlConfFileNameSave, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText301 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,-1 ), 0 )
		self.m_staticText301.Wrap( -1 )
		fgSizer6.Add( self.m_staticText301, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_buttonConfFileNameSave = wx.Button( sbSizer5.GetStaticBox(), wx.ID_ANY, u"Borwse...", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_buttonConfFileNameSave, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText29 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText29.Wrap( -1 )
		fgSizer6.Add( self.m_staticText29, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText43 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText43.Wrap( -1 )
		fgSizer6.Add( self.m_staticText43, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText30 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText30.Wrap( -1 )
		fgSizer6.Add( self.m_staticText30, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText45 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText45.Wrap( -1 )
		fgSizer6.Add( self.m_staticText45, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText35 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText35.Wrap( -1 )
		fgSizer6.Add( self.m_staticText35, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText36 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText36.Wrap( -1 )
		fgSizer6.Add( self.m_staticText36, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText32 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText32.Wrap( -1 )
		fgSizer6.Add( self.m_staticText32, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_buttonGetInventory = wx.Button( sbSizer5.GetStaticBox(), wx.ID_ANY, u"Inventory取得", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_buttonGetInventory, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer5.Add( fgSizer6, 0, wx.EXPAND|wx.TOP, 5 )
		
		
		bSizer8.Add( sbSizer5, 0, wx.EXPAND, 5 )
		
		sbSizer10 = wx.StaticBoxSizer( wx.StaticBox( self.m_panelInventoriReference, wx.ID_ANY, u"ユーザー情報（取得用）" ), wx.VERTICAL )
		
		fgSizer8 = wx.FlexGridSizer( 4, 3, 0, 0 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText24 = wx.StaticText( sbSizer10.GetStaticBox(), wx.ID_ANY, u"UserID", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		self.m_staticText24.Wrap( -1 )
		fgSizer8.Add( self.m_staticText24, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrlReferenceUserID = wx.TextCtrl( sbSizer10.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,-1 ), 0 )
		fgSizer8.Add( self.m_textCtrlReferenceUserID, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText28 = wx.StaticText( sbSizer10.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText28.Wrap( -1 )
		fgSizer8.Add( self.m_staticText28, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText25 = wx.StaticText( sbSizer10.GetStaticBox(), wx.ID_ANY, u"Token", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )
		fgSizer8.Add( self.m_staticText25, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlReferenceAccessToken = wx.TextCtrl( sbSizer10.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 400,-1 ), 0 )
		fgSizer8.Add( self.m_textCtrlReferenceAccessToken, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_buttonReferenceGetAccessToken = wx.Button( sbSizer10.GetStaticBox(), wx.ID_ANY, u"Token取得", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.m_buttonReferenceGetAccessToken, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText47 = wx.StaticText( sbSizer10.GetStaticBox(), wx.ID_ANY, u"Reference URL", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText47.Wrap( -1 )
		fgSizer8.Add( self.m_staticText47, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_comboBoxReferenceURLChoices = [ u"https://nims.mintsys.jp:50443/inventory-api/v3", u"https://dev-u-tokyo.mintsys.jp:50443/inventory-api/v3", u"https://u-tokyo.mintsys.jp:50443/inventory-api/v3" ]
		self.m_comboBoxReferenceURL = wx.ComboBox( sbSizer10.GetStaticBox(), wx.ID_ANY, u"Combo!", wx.DefaultPosition, wx.DefaultSize, m_comboBoxReferenceURLChoices, 0 )
		self.m_comboBoxReferenceURL.SetSelection( 0 )
		fgSizer8.Add( self.m_comboBoxReferenceURL, 0, wx.ALL, 5 )
		
		
		sbSizer10.Add( fgSizer8, 1, wx.EXPAND, 5 )
		
		
		bSizer8.Add( sbSizer10, 0, wx.EXPAND, 5 )
		
		
		self.m_panelInventoriReference.SetSizer( bSizer8 )
		self.m_panelInventoriReference.Layout()
		bSizer8.Fit( self.m_panelInventoriReference )
		self.m_notebook2.AddPage( self.m_panelInventoriReference, u"インベントリから取得", True )
		self.m_panelInventoryUpdate = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer9 = wx.BoxSizer( wx.VERTICAL )
		
		sbSizer51 = wx.StaticBoxSizer( wx.StaticBox( self.m_panelInventoryUpdate, wx.ID_ANY, u"投入" ), wx.VERTICAL )
		
		fgSizer7 = wx.FlexGridSizer( 8, 4, 0, 0 )
		fgSizer7.SetFlexibleDirection( wx.BOTH )
		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText46 = wx.StaticText( sbSizer51.GetStaticBox(), wx.ID_ANY, u"設定ファイル", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_staticText46.Wrap( -1 )
		fgSizer7.Add( self.m_staticText46, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlConfFileNameRead = wx.TextCtrl( sbSizer51.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_textCtrlConfFileNameRead, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText33 = wx.StaticText( sbSizer51.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.m_staticText33.Wrap( -1 )
		fgSizer7.Add( self.m_staticText33, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_buttonBrowseConfFileRead = wx.Button( sbSizer51.GetStaticBox(), wx.ID_ANY, u"Browse...", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.m_buttonBrowseConfFileRead, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer51.Add( fgSizer7, 1, wx.EXPAND, 5 )
		
		
		bSizer9.Add( sbSizer51, 0, wx.EXPAND, 5 )
		
		sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self.m_panelInventoryUpdate, wx.ID_ANY, u"削除" ), wx.VERTICAL )
		
		fgSizer61 = wx.FlexGridSizer( 5, 4, 0, 0 )
		fgSizer61.SetFlexibleDirection( wx.BOTH )
		fgSizer61.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText261 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_staticText261.Wrap( -1 )
		fgSizer61.Add( self.m_staticText261, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText271 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 110,-1 ), 0 )
		self.m_staticText271.Wrap( -1 )
		fgSizer61.Add( self.m_staticText271, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText282 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.m_staticText282.Wrap( -1 )
		fgSizer61.Add( self.m_staticText282, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_buttonDeleteInventories = wx.Button( sbSizer6.GetStaticBox(), wx.ID_ANY, u"削除...", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer61.Add( self.m_buttonDeleteInventories, 0, wx.RIGHT|wx.LEFT, 5 )
		
		
		sbSizer6.Add( fgSizer61, 1, wx.EXPAND, 5 )
		
		
		bSizer9.Add( sbSizer6, 0, wx.EXPAND, 5 )
		
		sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self.m_panelInventoryUpdate, wx.ID_ANY, u"ユーザー情報（投入または削除用）" ), wx.VERTICAL )
		
		fgSizer9 = wx.FlexGridSizer( 5, 3, 0, 0 )
		fgSizer9.SetFlexibleDirection( wx.BOTH )
		fgSizer9.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText241 = wx.StaticText( sbSizer8.GetStaticBox(), wx.ID_ANY, u"UserID", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		self.m_staticText241.Wrap( -1 )
		fgSizer9.Add( self.m_staticText241, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlUserUpdateID = wx.TextCtrl( sbSizer8.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 150,-1 ), 0 )
		fgSizer9.Add( self.m_textCtrlUserUpdateID, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText281 = wx.StaticText( sbSizer8.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText281.Wrap( -1 )
		fgSizer9.Add( self.m_staticText281, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText251 = wx.StaticText( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Token", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText251.Wrap( -1 )
		fgSizer9.Add( self.m_staticText251, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlUpdateAccessToken = wx.TextCtrl( sbSizer8.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 400,-1 ), 0 )
		fgSizer9.Add( self.m_textCtrlUpdateAccessToken, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_buttonUpdateGetAccessToken = wx.Button( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Token取得", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer9.Add( self.m_buttonUpdateGetAccessToken, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText48 = wx.StaticText( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Update URL", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText48.Wrap( -1 )
		fgSizer9.Add( self.m_staticText48, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_comboBoxUpdateURLChoices = [ u"https://nims.mintsys.jp:50443/inventory-update-api/v3", u"https://nims.mintsys.jp:50443/inventory-update-api/v3", u"https://dev-u-tokyo.mintsys.jp:50443/inventory-update-api/v3", u"https://u-tokyo.mintsys.jp:50443/inventory-update-api/v3", u"https://nims.mintsys.jp:50443/inventory-update-api/v3" ]
		self.m_comboBoxUpdateURL = wx.ComboBox( sbSizer8.GetStaticBox(), wx.ID_ANY, u"https://dev-u-tokyo.mintsys.jp:50443/inventory-update-api/v3", wx.DefaultPosition, wx.DefaultSize, m_comboBoxUpdateURLChoices, 0 )
		self.m_comboBoxUpdateURL.SetSelection( 2 )
		fgSizer9.Add( self.m_comboBoxUpdateURL, 0, wx.ALL, 5 )
		
		
		sbSizer8.Add( fgSizer9, 1, wx.EXPAND, 5 )
		
		
		bSizer9.Add( sbSizer8, 0, wx.EXPAND, 5 )
		
		
		self.m_panelInventoryUpdate.SetSizer( bSizer9 )
		self.m_panelInventoryUpdate.Layout()
		bSizer9.Fit( self.m_panelInventoryUpdate )
		self.m_notebook2.AddPage( self.m_panelInventoryUpdate, u"インベントリへの投入または削除", False )
		
		bSizer4.Add( self.m_notebook2, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer4 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.InventoryOperatorGUIOnClose )
		self.m_treeCtrlSelections.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.m_treeCtrlSelectionsOnTreeItemActivated )
		self.m_treeCtrlSelections.Bind( wx.EVT_TREE_KEY_DOWN, self.m_treeCtrlSelectionsOnTreeKeyDown )
		self.m_treeCtrlSelections.Bind( wx.EVT_TREE_SEL_CHANGED, self.m_treeCtrlSelectionsOnTreeSelChanged )
		self.m_treeCtrlSelections.Bind( wx.EVT_TREE_SEL_CHANGING, self.m_treeCtrlSelectionsOnTreeSelChanging )
		self.m_buttonGetDictionary.Bind( wx.EVT_BUTTON, self.m_buttonGetDictionaryOnButtonClick )
		self.m_buttonConfFileNameSave.Bind( wx.EVT_BUTTON, self.m_buttonConfFileNameSaveOnButtonClick )
		self.m_buttonGetInventory.Bind( wx.EVT_BUTTON, self.m_buttonGetInventoryOnButtonClick )
		self.m_buttonReferenceGetAccessToken.Bind( wx.EVT_BUTTON, self.m_buttonReferenceGetAccessTokenOnButtonClick )
		self.m_buttonBrowseConfFileRead.Bind( wx.EVT_BUTTON, self.m_buttonBrowseConfFileReadOnButtonClick )
		self.m_buttonDeleteInventories.Bind( wx.EVT_BUTTON, self.m_buttonDeleteInventoriesOnButtonClick )
		self.m_buttonUpdateGetAccessToken.Bind( wx.EVT_BUTTON, self.m_buttonUpdateGetAccessTokenOnButtonClick )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def InventoryOperatorGUIOnClose( self, event ):
		event.Skip()
	
	def m_treeCtrlSelectionsOnTreeItemActivated( self, event ):
		event.Skip()
	
	def m_treeCtrlSelectionsOnTreeKeyDown( self, event ):
		event.Skip()
	
	def m_treeCtrlSelectionsOnTreeSelChanged( self, event ):
		event.Skip()
	
	def m_treeCtrlSelectionsOnTreeSelChanging( self, event ):
		event.Skip()
	
	def m_buttonGetDictionaryOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonConfFileNameSaveOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonGetInventoryOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonReferenceGetAccessTokenOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonBrowseConfFileReadOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonDeleteInventoriesOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonUpdateGetAccessTokenOnButtonClick( self, event ):
		event.Skip()
	

###########################################################################
## Class DictionaryFolderSelector
###########################################################################

class DictionaryFolderSelector ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Dictionaries and Folders", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		#self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		m_sdbSizer = wx.StdDialogButtonSizer()
		self.m_sdbSizerOK = wx.Button( self, wx.ID_OK )
		m_sdbSizer.AddButton( self.m_sdbSizerOK )
		self.m_sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer.AddButton( self.m_sdbSizerCancel )
		m_sdbSizer.Realize();
		
		bSizer2.Add( m_sdbSizer, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )
		
		
		self.SetSizer( bSizer2 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.DictionaryFolderSelectorOnClose )
		self.m_sdbSizerCancel.Bind( wx.EVT_BUTTON, self.m_sdbSizerOnCancelButtonClick )
		self.m_sdbSizerOK.Bind( wx.EVT_BUTTON, self.m_sdbSizerOnOKButtonClick )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def DictionaryFolderSelectorOnClose( self, event ):
		event.Skip()
	
	def m_sdbSizerOnCancelButtonClick( self, event ):
		event.Skip()
	
	def m_sdbSizerOnOKButtonClick( self, event ):
		event.Skip()
	

###########################################################################
## Class SelectorBox
###########################################################################

class SelectorBox ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Selection", pos = wx.DefaultPosition, size = wx.Size( 698,461 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		#self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_listCtrlSelections = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_ICON )
		bSizer3.Add( self.m_listCtrlSelections, 1, wx.EXPAND, 5 )
		
		m_sdbSizer2 = wx.StdDialogButtonSizer()
		self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
		self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
		m_sdbSizer2.Realize();
		
		bSizer3.Add( m_sdbSizer2, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )
		
		
		self.SetSizer( bSizer3 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.SelectorBoxOnClose )
		self.m_sdbSizer2Cancel.Bind( wx.EVT_BUTTON, self.m_sdbSizer2OnCancelButtonClick )
		self.m_sdbSizer2OK.Bind( wx.EVT_BUTTON, self.m_sdbSizer2OnOKButtonClick )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def SelectorBoxOnClose( self, event ):
		event.Skip()
	
	def m_sdbSizer2OnCancelButtonClick( self, event ):
		event.Skip()
	
	def m_sdbSizer2OnOKButtonClick( self, event ):
		event.Skip()
	

