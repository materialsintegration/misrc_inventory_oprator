#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.

'''
OLD ID to NEW ID
'''
import os, sys
import json

sys.path.append("/home/misystem/assets/modules/misrc_inventory_management")
#from inventory_ids import *

def createOldNew(infilename, table_file):
    '''
    infilenameにあるMIntシステムのIDを抽出してテーブルを作成、残りを埋めてもらい、transateOldNewで使用する
    @param infilename(string)
    @param table_file(string)
    @retval (bool)
    '''

    infile = open(infilename)
    lines = infile.read()

    # 記述子発見
    
    # 予測モデル発見
    # 予測モジュール発見
    # ワークフロー発見


def translateOldNew(infilename, outfilename, src_site, dst_site):
    '''
    インベントリマネージャーを利用した新旧対応リストで変換する
    @param infilename(string)
    @param outfilename(string)
    @param src_site(string)
    @param dst_site(string)
    @retval (bool)
    '''

    d_ids = getInventoryData(src_site, dst_site, "descriptor")
    m_ids = getInventoryData(src_site, dst_site, "prediction_model")

    infile = open(infilename, "r")
    outfile = open(outfilename, "w")

    inlines = infile.read()
    for item in d_ids:
        inlines = inlines.replace(item, d_ids[item])
    for item in m_ids:
        print("ID(%s) to ID(%s)"%(item, m_ids[item]))
        inlines = inlines.replace(item, m_ids[item])

    outfile.write(inlines)

    infile.close()
    outfile.close()

    return True

def translateOldNew_with_table(table_file, infilename, outfilename):
    '''
    新旧対応表を使って、srcfileの旧文字列を新文字列にして、outfilenameへ出力する
    @param table(string) 新旧対応表のファイル名
    @param infilename(string)
    @param outfilename(string)
    @retval (bool)
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
    mode = None
    table_file = None
    src_file = None
    dst_file = None
    src_site = None
    dst_site = None
    go_help = False

    for item in sys.argv:
        items = item.split(":")
        if len(items) != 2:
            continue
        if items[0] == "mode":
            mode = items[1]
        elif items[0] == "table_file":
            table_file = items[1]
        elif items[0] == "src":
            src_file = items[1]
        elif items[0] == "dst":
            dst_file = items[1]
        elif items[0] == "src_site":
            src_site = items[1]
        elif items[0] == "dst_site":
            dst_site = items[1]
        else:
            print("未知のパラメータ指定(%s)です。"%item)
            go_help = True

    if mode == "table":
        print("未実装です。transモードのみ使用可能です。")
        go_help = True
        if table_file is None:
            print("変換テーブルファイルの指定がありません。")
            go_help = True
        elif src_file is None:
            print("変換元のファイルの指定がありません。")
            go_help = True
        else:
            if os.path.exists(src_file) is False:
                print("変換元のファイル(%s)がありません。"%src_file)
                go_help = True
    elif mode == "trans":
        if src_file is None:
            print("変換元のファイルの指定がありません。")
            go_help = True
        elif dst_file is None:
            print("変換後のファイルの指定がありません。")
            go_help = True
        elif src_site is None:
            print("変換元のサイトの指定がありません。")
            go_help = True
        elif dst_site is None:
            print("変換後のサイトの指定がありません。")
            go_help = True
        else:
            if os.path.exists(src_file) is False:
                print("変換元のファイル(%s)がありません。"%src_file)
                go_help = True

    if go_help is True:
        print("ID変換ツール")
        print("")
        print("usage:")
        print("   python src_dst.py src:<src file> dst:<dst file> src_site:<src site> dst_site:<dst site>")
        print("")
        print("       mode : 動作モード")
        print("              table : テーブルテンプレート作成")
        print("              trans : テーブルを使用し変換実行")
        print("      table : IDテーブルの指定")
        print("      src   : 変換元のファイル")
        print("      dst   : 変換後のファイル(上書き非推奨)")
        print("    src_site: 変換元のサイト(e.g. dev-u-tokyo.mintsys.jp")
        print("    dst_site: 変換後のサイト(e.g. nims.mintsys.jp")
        sys.exit(1)

    if mode == "table":
        retval = createOldNew(src_file, table_file)
    elif mode == "trans":
        retval = translateOldNew(src_file, dst_file, src_site, dst_site)

    if retval == False:
        sys.exit(1)

if __name__ == '__main__':
    main()

