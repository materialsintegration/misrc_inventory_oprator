#!/usr/local/python2.7/bin/python
# -*- coding: utf-8 -*-

'''
NIMS野口さん作成のインベントリAPIプログラムのラッパープログラム
'''

from InventoryOperatorGui import *
import sys, os
import time
import json
import xml.etree.ElementTree as ET
import datetime


class InventoryOperator(InventoryOperatorGUI):
    '''
    '''

    def __init__(self, parent):
        '''
        '''

        InventoryOperatorGUI.__init__(self, parent)

def main():
    '''
    \u958b\u59cb\u70b9
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
                                        
