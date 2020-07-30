#!/usr/bin/python3.6
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.
# -*- coding: utf-8 -*-

import wx
import wx.lib.mixins.listctrl as listmix

'''
checkボックス付きListCtrl用クラス
参考：https://www.ibm.com/developerworks/jp/opensource/library/os-python-kvm-scripting2/index.html
'''

class CheckListCtrl(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):
    '''
    '''

    def __init__(self, *args, **kwargs):
        '''
        コンストラクタ
        '''
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(2)
 
class SelectorBox ( wx.Frame ):
    
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Selection", pos = wx.DefaultPosition, size = wx.Size( 698,461 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        #self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        
        bSizer3 = wx.BoxSizer( wx.VERTICAL )
        
        #self.m_listCtrl4 = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_ICON )
        self.m_listCtrlSelections = CheckListCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, style=wx.LC_REPORT)

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
        self.Bind(wx.EVT_LIST_COL_CLICK, self.m_listCtrlSelectionsOnColClick, self.m_listCtrlSelections)
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
    
    def m_listCtrlSelectionsOnColClick(self, event):
        event.Skip()


