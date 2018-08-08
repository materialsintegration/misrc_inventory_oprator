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
## Class MyFrame2
###########################################################################

class MyFrame2 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Inventory Operator", pos = wx.DefaultPosition, size = wx.Size( 697,523 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer5 = wx.FlexGridSizer( 3, 1, 0, 0 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sbSizer10 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"ユーザー情報" ), wx.VERTICAL )
		
		fgSizer8 = wx.FlexGridSizer( 4, 3, 0, 0 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText24 = wx.StaticText( sbSizer10.GetStaticBox(), wx.ID_ANY, u"UserID", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		self.m_staticText24.Wrap( -1 )
		fgSizer8.Add( self.m_staticText24, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_textCtrlUserID = wx.TextCtrl( sbSizer10.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.m_textCtrlUserID, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText28 = wx.StaticText( sbSizer10.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText28.Wrap( -1 )
		fgSizer8.Add( self.m_staticText28, 0, wx.ALL, 5 )
		
		self.m_staticText25 = wx.StaticText( sbSizer10.GetStaticBox(), wx.ID_ANY, u"Token", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )
		fgSizer8.Add( self.m_staticText25, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlAccessToken = wx.TextCtrl( sbSizer10.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 400,-1 ), 0 )
		fgSizer8.Add( self.m_textCtrlAccessToken, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_buttonGetAccessToken = wx.Button( sbSizer10.GetStaticBox(), wx.ID_ANY, u"Token取得", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.m_buttonGetAccessToken, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer10.Add( fgSizer8, 1, wx.EXPAND, 5 )
		
		
		fgSizer5.Add( sbSizer10, 1, wx.EXPAND, 5 )
		
		sbSizer5 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"インベントリ取得" ), wx.VERTICAL )
		
		fgSizer6 = wx.FlexGridSizer( 8, 4, 0, 0 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText37 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText37.Wrap( -1 )
		fgSizer6.Add( self.m_staticText37, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText38 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, u"名称", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText38.Wrap( -1 )
		fgSizer6.Add( self.m_staticText38, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText39 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, u"ID番号", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText39.Wrap( -1 )
		fgSizer6.Add( self.m_staticText39, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText40 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText40.Wrap( -1 )
		fgSizer6.Add( self.m_staticText40, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText26 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, u"辞書", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )
		fgSizer6.Add( self.m_staticText26, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlDictionary = wx.TextCtrl( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrlDictionary, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticTextDictionaryID = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.m_staticTextDictionaryID.Wrap( -1 )
		fgSizer6.Add( self.m_staticTextDictionaryID, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_buttonGetDictionary = wx.Button( sbSizer5.GetStaticBox(), wx.ID_ANY, u"辞書取得", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_buttonGetDictionary, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText27 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, u"フォルダー", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText27.Wrap( -1 )
		fgSizer6.Add( self.m_staticText27, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlFolder = wx.TextCtrl( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrlFolder, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticTextFolderID = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.m_staticTextFolderID.Wrap( -1 )
		fgSizer6.Add( self.m_staticTextFolderID, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_buttonGetFolder = wx.Button( sbSizer5.GetStaticBox(), wx.ID_ANY, u"フォルダー取得", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_buttonGetFolder, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText29 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText29.Wrap( -1 )
		fgSizer6.Add( self.m_staticText29, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText43 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText43.Wrap( -1 )
		fgSizer6.Add( self.m_staticText43, 0, wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticText30 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText30.Wrap( -1 )
		fgSizer6.Add( self.m_staticText30, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText32 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText32.Wrap( -1 )
		fgSizer6.Add( self.m_staticText32, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText33 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, u"設定ファイル", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
		self.m_staticText33.Wrap( -1 )
		fgSizer6.Add( self.m_staticText33, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrlConfFileName = wx.TextCtrl( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrlConfFileName, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText46 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText46.Wrap( -1 )
		fgSizer6.Add( self.m_staticText46, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_buttonBrowseConfFile = wx.Button( sbSizer5.GetStaticBox(), wx.ID_ANY, u"Browse...", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_buttonBrowseConfFile, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText45 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText45.Wrap( -1 )
		fgSizer6.Add( self.m_staticText45, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText35 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText35.Wrap( -1 )
		fgSizer6.Add( self.m_staticText35, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText36 = wx.StaticText( sbSizer5.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText36.Wrap( -1 )
		fgSizer6.Add( self.m_staticText36, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_buttonGetInventory = wx.Button( sbSizer5.GetStaticBox(), wx.ID_ANY, u"Inventory取得", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_buttonGetInventory, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		sbSizer5.Add( fgSizer6, 1, wx.EXPAND, 5 )
		
		
		fgSizer5.Add( sbSizer5, 1, wx.EXPAND, 5 )
		
		sbSizer7 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"インベントリ反映" ), wx.VERTICAL )
		
		fgSizer7 = wx.FlexGridSizer( 8, 3, 0, 0 )
		fgSizer7.SetFlexibleDirection( wx.BOTH )
		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		sbSizer7.Add( fgSizer7, 1, wx.EXPAND, 5 )
		
		
		fgSizer5.Add( sbSizer7, 1, wx.EXPAND, 5 )
		
		sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"label" ), wx.VERTICAL )
		
		
		fgSizer5.Add( sbSizer8, 1, wx.EXPAND, 5 )
		
		
		bSizer4.Add( fgSizer5, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer4 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_buttonGetAccessToken.Bind( wx.EVT_BUTTON, self.m_buttonGetAccessTokenOnButtonClick )
		self.m_buttonGetDictionary.Bind( wx.EVT_BUTTON, self.m_buttonGetDictionaryOnButtonClick )
		self.m_buttonGetFolder.Bind( wx.EVT_BUTTON, self.m_buttonGetFolderOnButtonClick )
		self.m_buttonBrowseConfFile.Bind( wx.EVT_BUTTON, self.m_buttonBrowseConfFileOnButtonClick )
		self.m_buttonGetInventory.Bind( wx.EVT_BUTTON, self.m_buttonGetInventoryOnButtonClick )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def m_buttonGetAccessTokenOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonGetDictionaryOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonGetFolderOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonBrowseConfFileOnButtonClick( self, event ):
		event.Skip()
	
	def m_buttonGetInventoryOnButtonClick( self, event ):
		event.Skip()
	

