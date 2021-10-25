#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.

'''
文献から予測モジュールを作成する際の実行スクリプト作成プログラム
'''

import sys, os
import pandas as pd
from glob import glob

# ヘッダーが２段構成なのでカラム位置の指定しやすくするための辞書を作成
headers = {"No.":"No.",
        "ページ(式番号)": 'ページ(式番号)',
        "式": '式',
        "Sympy式": 'Sympy式',
        "式の名称(左辺が示す物理量)": '式の名称(左辺が示す物理量)',
        "式の説明": '式の説明',
        "変数名1": '入力1',
        "説明1": 'Unnamed: 7',
        "単位1": 'Unnamed: 8',
        "変数名2": '入力2',
        "説明2": 'Unnamed: 10',
        "単位2": 'Unnamed: 11',
        "変数名3": '入力3',
        "説明3": 'Unnamed: 13',
        "単位3": 'Unnamed: 14',
        "変数名4": '入力4',
        "説明4": 'Unnamed: 16',
        "単位4": 'Unnamed: 17',
        "変数名5": '入力5',
        "説明5": 'Unnamed: 19',
        "単位5": 'Unnamed: 20',
        "変数名6": '入力6',
        "説明6": 'Unnamed: 22',
        "単位6": 'Unnamed: 23',
        "変数名7": '入力7',
        "説明7": 'Unnamed: 25',
        "単位7": 'Unnamed: 26',
        "変数名8": '入力8',
        "説明8": 'Unnamed: 28',
        "単位8": 'Unnamed: 29',
        "変数名9": '入力9',
        "説明9": 'Unnamed: 31',
        "単位9": 'Unnamed: 32',
        "変数名10": '入力10',
        "説明10": 'Unnamed: 34',
        "単位10": 'Unnamed: 35',
        "変数名11": '入力11',
        "説明11": 'Unnamed: 37',
        "単位11": 'Unnamed: 38',
        "変数名12": '入力12',
        "説明12": 'Unnamed: 40',
        "単位12": 'Unnamed: 41',
        "変数名13": '入力13',
        "説明13": 'Unnamed: 43',
        "単位13": 'Unnamed: 44',
        "変数名14": '入力14',
        "説明14": 'Unnamed: 46',
        "単位14": 'Unnamed: 47',
        "出力": '出力',
        "出力説明": 'Unnamed: 49',
        "出力単位": 'Unnamed: 50',
        "(入出力重複確認)": 'Unnamed: 51',
        'WF説明文(前半)': 'WF説明文(前半)',
        'WF説明文(後半)': 'WF説明文(後半)'
}
# スタブスクリプトの場所
STUB_DIR="scripts/stubs"
# 冒頭のシェバンとコピーライト
top_of_script = "#!/usr/bin/python3.6 \n# -*- coding: utf-8 -*-\n# Copyright (c) The University of Tokyo and\n# National Institute for Materials Science (NIMS). All rights reserved.\n# This document may not be reproduced or transmitted in any form,\n# in whole or in part, without the express written permission of\n# the copyright owners.\n"
#import_packs = 'import sys, os\n\nsys.path.append("/home/misystem/assets/modules/workflow_python_lib")\nfrom workflow_lib import *\n'
import_packs = 'import sys, os\n\nsys.path.append("/home/misystem/assets/modules/workflow_python_lib")\n#from workflow_lib import *\n'

def make_object(inputs, outputs, object_script_name, stub_package, description):
    '''
    予測モジュール実行スクリプトを作成する。
    @param inputs(list)
    @param outputs(list)
    @param object_script_name(string)
    @param stub_package(string)
    @retval
    '''

    current_dir = os.getcwd()
    os.chdir("scripts")
    outfile = open(object_script_name, "w")
    outfile.write(top_of_script)                              # シェバンとか
    outfile.write("\n\n'''\n%s\n'''"%description)             # トップの説明
    outfile.write("\n%s\n"%import_packs)                      # 共通パッケージ
    #outfile.write('sys.path.append("./stubs")')              # スタブの場所
    outfile.write("\nfrom stubs.%s import *\n"%stub_package)  # スタブパッケージの読み込み

    # 入出力ポートの設定
    outfile.write("inputports = {")
    for i in range(len(inputs)):
        #print(inputs[i])
        if i == len(inputs) - 1:
            outfile.write("'%s':'%s.dat'}\n"%(inputs[i]["description"], inputs[i]["name"]))
        else:
            outfile.write("'%s':'%s.dat',\n              "%(inputs[i]["description"], inputs[i]["name"]))
    outfile.write("outputpots = {")
    for i in range(len(outputs)):
        #print(outputs[i])
        if i == len(outputs) - 1:
            outfile.write("'%s':''}\n"%outputs[i]["description"])
        else:
            outfile.write("'%s':'',\n              "%outputs[i]["description"])
    outfile.write("out_realnames = {")
    for i in range(len(outputs)):
        if i == len(outputs) - 1:
            outfile.write("'%s.dat':'%s'}\n"%(outputs[i]["name"], outputs[i]["description"]))
        else:
            outfile.write("'%s.dat':'%s',\n              "%(outputs[i]["name"], outputs[i]["description"]))
        
    outfile.write("\n")
    # ワークフロー実行スクリプト初期化
    outfile.write("wf_tool = MIApiCommandClass()\n")
    outfile.write("wf_tool.setInportNames(inputports)\n")
    outfile.write("wf_tool.setOutportNames(outputports)\n")
    outfile.write("wf_tool.setRealName(in_realnames)\n")
    outfile.write("wf_tool.Initialize(translate_input=True, translate_output=True)\n")
    outfile.write("\n")

    # 入力パラメータの取り込み
    for item in inputs:
        outfile.write("# %s\n"%item["description"])
        outfile.write("%s = None\n"%item["name"])
        outfile.write("if os.path.exists('%s.dat') is True:\n"%item["name"])
        outfile.write("    infile = open('%s.dat', 'r')\n"%item["name"])
        outfile.write("    %s = float(infile.read().split('\\n')[0])\n"%item["name"])

    outfile.write("\n")
    # ディレクトリ処理
    outfile.write("tool_dir = os.getcwd()        # ツールのディレクトリ名保存\n")

    # スタブ実行
    outfile.write("\n# スタブ実行\n")
    outfile.write("%s = calc("%outputs[0]["name"])
    for i in range(len(inputs)):
        if i == len(inputs) - 1:
            outfile.write("%s)\n"%inputs[i]["name"])
        else:
            outfile.write("%s, "%inputs[i]["name"])

    # 出力書き込み
    outfile.write("\n# 結果の書き込み\n")
    outfile.write("outfile = open('%s.dat', 'w')\n"%outputs[0]["name"])
    outfile.write("outfile.write('%%s\\n'%%%s)\n"%outputs[0]["name"])
    outfile.write("outfile.close()\n\n")

    # 書き込み終了
    outfile.close()
    os.chdir(current_dir)

def generateExecutables(repo_dir, scr_dir, inventory_list, prefix):
    '''
    記述子リストから実行スクリプトを作成し、そのファイル名を記述子リストへ追記する。
    @param repo_dir(string)
    @param scr_dir(string)
    @param inventory_list(string)
    @retval (bool)
    '''

    infile = pd.ExcelFile(inventory_list)
    df = infile.parse("計算式リスト")
    df2 = infile.parse("記述子リスト")
    #df[df.isna().any(axis=1) == False]
    #df[df["No."].isna() == False]
    df.dropna(how="all")

    # 実行スクリプト名用の列を追加
    df["実行スクリプト名"] = None

    # 入出力ポートの辞書
    # [
    #   {
    #     "No":number(int),
    #     "inputPorts":
    #       [
    #         {"name":name(string),
    #          "description":description(string)},
    #         {...},
    #         {"name":name(string),
    #          "description":description(string)},
    #       ],
    #     "outputPorts": 
    #       [
    #         {"name":name(string),
    #          "description":description(string)},
    #         {...},
    #         {"name":name(string),
    #          "description":description(string)},
    #       ],
    #     "stubScriptName":スタブスクリプト名(string),
    #     "stubPackegeName":スタブパッケージ名(string)
    #     "objectPathName":実行スクリプト名(string)
    #   }
    # ]
    in_out_dict = []
    # 入出力ポートとスタブ情報の収集
    current_dir = os.getcwd()
    for module_index in range(1, len(df[headers["No."]])):
        module_no = int(df["No."][module_index])
        module_description = df["式の説明"][module_index]
        print("No(%4d) / description(%s)"%(module_no, module_description))
        var_name_base = "変数名"
        var_desc_base = "説明"
        inputs = []
        for i in range(1, 15):
            name = df[headers[var_name_base + "%s"%i]][module_index]
            desc = df[headers[var_desc_base + "%s"%i]][module_index]
            # 入出力ポートが未設定のカラムは無視する。
            if pd.isnull(df[headers[var_name_base + "%s"%i]][module_index]) is True:
                continue
            inputs.append({"name":name, "description":desc})
        outputs = []
        name = df[headers["出力"]][module_index]
        desc = df[headers["出力説明"]][module_index]
        outputs.append({"name":name, "description":desc})
        os.chdir(STUB_DIR)
        stub_script = glob("*_%02d.py"%module_no)
        stub_package = None
        if len(stub_script) == 1:
            print(stub_script)
            stub_package = stub_script[0].split(".")[0] 
        if stub_package is None:
            print("No.(%d)のスタブ情報が取得できませんでした。(%s(%s))"%(module_index, stub_script, "*_%02d.py"%module_index))
            sys.exit(1)
        object_script_name = prefix + "_%02d.py"%module_no
        object_path_script = os.path.join(repo_dir, "scripts", object_script_name)
        in_out_dict.append({"No":module_index, "inputPorst":inputs, "outputPorts":outputs, "stubScriptName":stub_script, "stubPacakgeName":stub_package, "objectPathname":object_path_script})
        os.chdir(current_dir)

        make_object(inputs, outputs, object_script_name, stub_package, module_description)
        df["実行スクリプト名"][module_index] = object_script_name

    #print(df)
    writer = pd.ExcelWriter("./references/test.xlsx")
    df.to_excel(writer, sheet_name="計算式リスト")
    df2.to_excel(writer, sheet_name="記述子リスト")
    writer.save()
    writer.close()

def go_help():
    '''
    Usage表示
    '''

    print("記述子リストとスタブの指定からobjectPathに設定するスクリプトを作成する")
    print("")
    print("Usage: $ python repo_dir:<ディレクトリ名> scr_dir:<ディレクトリ名> inventory_list:記述子リスト prefix:<スクリプトの接頭辞>")
    print("")
    print("パラメータ詳細")
    print("        repo_dir    : リポジトリのディレクトリ名。")
    print("                      指定がない場合現在のディスプレイがリポジトリディレクトリと判断される。")
    print("        scr_dir     : リポジトリディレクトリ以下、スクリプトを作成するディレクトリの名前。")
    print("                      リポジトリディレクトリ以下にこのディレクトリがあるものと仮定する。")
    print("                      さらにこの下に、stubsというディレクトリがあると仮定し、")
    print("                      そこにスタブスクリプトがあるものと仮定して動作する")
    print("    inventory_list  : 情報の起点となるリスト。エクセルフォーマット")
    print("        prefix      : 作成するスクリプト名の接頭辞")
    print("")
    print("※作成されるスクリプトは、repo_dir/scr_dir/prefix_<index>.pyとなる。")

    sys.exit(1)

def main():
    '''
    開始点
    '''

    repo_dir = None
    scr_dir = None
    inventory_list = None
    prefix = None

    if len(sys.argv) == 1:
        go_help()
        sys.exit(0)

    for item in sys.argv:
        items = item.split(":")
        if len(items) != 2:
            continue
        if items[0] == "scr_dir":
            scr_dir = items[1]
        elif items[0] == "repo_dir":
            repo_dir = items[1]
        elif items[0] == "inventory_list":
            inventory_list = items[1]
        elif items[0] == "prefix":
            prefix = items[1]

    if repo_dir is None:                        # repo_dir未指定なら、repo_dirはカレントディレクトリとする。
        repo_dir = os.getcwd().split("/")[-1]
        work_dir = "./"
    else:
        work_dir = repo_dir
    if scr_dir is None:
        print("scriptsが含まれるディレクトリ名が指定されていません。")
        go_help()
    else:
        dirs = scr_dir.split("/")
        if len(dirs) == 1:
            script_dir = os.path.join(work_dir, dirs[0])
            if os.path.exists(script_dir) is False:
                print("スクリプト用のディレクトリ(%s)がありません。"%script_dir)
                go_help()

    if inventory_list is None:
        print("記述子リストファイルの指定がありません。")
    else:
        inventory_list = os.path.join(work_dir, inventory_list)
        if os.path.exists(inventory_list) is False:
            print("記述子リストファイル(%s)がありません。"%inventory_list)
            go_help()
    if prefix is None:
        print("objectPathスクリプト名の接頭辞の指定がありません。")
        sys.exit(1)

    print("作業ディレクトリ：%s"%work_dir)
    print("スクリプトディレクトリ：%s"%script_dir)
    print("記述子リスト：%s"%inventory_list)
    print("スクリプト接頭辞：%s"%prefix)
    generateExecutables(repo_dir, scr_dir, inventory_list, prefix)

if __name__ == '__main__':
    main()







