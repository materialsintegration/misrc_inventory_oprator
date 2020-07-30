#!/usr/bin/python3.6
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.
# -*- coding: utf-8 -*-

'''
OLD ID to NEW ID
'''
import os, sys
import json

def translateOldNew(table_file, infilename, outfilename):
    '''
    新旧対応表を使って、srcfileの旧文字列を新文字列にして、newfileへ出力する
    @param table(string) 新旧対応表のファイル名
    @param srcfile(string)
    @param newfile(string)
    @retval なし
    '''

    old_new = {}
    if os.path.exists(table_file) is True:
        table = open(table_file, "r")
        old_new = json.load(table)
        table.close()

    if os.path.exists(infilename) is True:
        infile = open(infilename, "r")
    else:
        return False

    outfile = open(outfilename, "w")

    inlines = infile.read()
    for item in old_new:
        #print("old = %s to new = %s"%(item, old_new[item]))
        inlines = inlines.replace(item, old_new[item])

    outfile.write(inlines)

    infile.close()
    outfile.close()

    return True

def translateOldNew_obsolited(table_file, infilename, outfilename):
    '''
    * 新旧対応表のフォーマットが変更になったのでこちらは廃棄 *
    新旧対応表を使って、srcfileの旧文字列を新文字列にして、newfileへ出力する
    @param table(string) 新旧対応表のファイル名
    @param srcfile(string)
    @param newfile(string)
    @retval なし
    '''

    old_new = {}
    if os.path.exists(table_file) is True:
        table = open(table_file, "r")
        lines = table.read().split("\n")
        for aline in lines:
            if aline == "":
                continue
            #print("%s -> %s"%(aline.split()[0],aline.split()[1]))
            old_new[aline.split()[0]] = aline.split()[1]

        table.close()

    if os.path.exists(infilename) is True:
        infile = open(infilename, "r")
    else:
        return False

    outfile = open(outfilename, "w")

    inlines = infile.read()
    for item in old_new:
        #print("old = %s to new = %s"%(item, old_new[item]))
        inlines = inlines.replace(item, old_new[item])

    outfile.write(inlines)

    infile.close()
    outfile.close()

    return True

def main():
    '''
    開始点
    '''

    params_len = len(sys.argv)

    if len(sys.argv) != 4:
        print("usage:")
        print("   python old_new.py <table file> <src file> <new file>")
        sys.exit(1)

    table_file = sys.argv[1]
    infilename = sys.argv[2]
    outfilename = sys.argv[3]

    if translateOldNew(table_file, infilename, outfilename) is False:
        sys.exit(1)

if __name__ == '__main__':
    main()

