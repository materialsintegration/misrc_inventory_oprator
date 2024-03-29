#!/usr/bin/python3.6
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.
# -*- coding: utf-8 -*-

'''
Inventoryシステムから出力される辞書内容ファイル（rdf?）を
InventoryAPIで読める形式のJSONスタイルファイルに変換するプログラム
'''

import sys, os
import csv
import json
from analyze_inventory_json import *

class InventoryRdfOperator():
    '''
    Inventoryシステムから出力されるRDFファイルを読み込み辞書とJSONスタイルファイルを作成する。
    '''

    def __init__(self):
        '''
        コンストラクタ
        '''

    def ReadRDFFile(self, infilename):
        '''
        InventoryRDFファイルを読み込む
        '''

        infile = open(infilename, "r")
        lines = infile.read().split("\n")

        inventories = {"folders":[], "descriptors":[], "prediction-models":[], "software-tools":[]}
        inventory = {}
        inventory_item = None
        inventory_type = None
        for item in lines:
            if item == "":
                continue
            items = item.split()
            if items[0] == "@prefix":
                continue

            #item = item.replace('\t', '\\t')
            item = item.replace('\\n', '\r\n')
            items = csv.reader([item], delimiter=' ', quotechar='"')
            results = list(items)[0]
            url = results[0].split("/")

            if inventory_item != url[-1]:
                print("inventory type = %s / invetory_item = %s"%(inventory_type, inventory_item))
                #for item in inventory:
                #    print("key = %s / content = %s"%(item, inventory[item]))
                if inventory_type is not None:
                    inventories[inventory_type].append(inventory)
                inventory_item = url[-1]
                inventory = {}

            if url[-2] == "folders":
                inventory_type = "folders"
            elif url[-2] == "descriptors":
                inventory_type = "descriptors"
            elif url[-2] == "prediction-models":
                inventory_type = "prediction-models"
            elif url[-2] == "software-tools":
                inventory_type = "software-tools"
            else:
                continue

            #for inventory_item in results:
            #    print inventory_item
            #print("results[1] = %s / results[2] = %s"%(results[1], results[2]))
            contents = results[2]
            if 5 <= len(results):
                for i in range(3, len(results)):
                    if results[i] == ".":
                        continue
                    contents += results[i]
            #if results[1] == "mi:inputDescriptor":
            #    print contents
            inventory[results[1]] = contents
            if ("descriptor_id" in inventory) is not True:
                inventory["descriptor_id"] = results[0].strip('<>')

        print("inventory type = %s / invetory_item = %s"%(inventory_type, inventory_item))
        if len(inventory) != 0:
            print(inventory)
            inventories[inventory_type].append(inventory)

        #print inventories
        #for key in inventories:
        #    print("type = %s"%key)
        #    for item1 in inventories[key]:
        #        print("--------------------------------------------------------------------------------")
        #        for inventory_item in item1:
        #            print("key = %s / content = %s"%(inventory_item, item1[inventory_item]))

        self.dicttoJson(inventories)

    def dicttoJson(self, inventory_dict):
        '''
        辞書からJSONファイルの作成
        キーが微妙にInventory登録用のキーと違うので、変換アリ
        '''

        descriptors = {}
        descriptors["descriptors"] = []
        prediction_models = {}
        prediction_models["prediction_models"] = []
        software_tools = {}
        software_tools["software_tools"] = []
        folders = {}
        folders["folders"] = []
        inventory = {}
        current_inventory_type = None
        for inventory_type in inventory_dict:
            for items in inventory_dict[inventory_type]:
                #print items
                if len(inventory) != 0:
                    if current_inventory_type == "folders":
                        folders["folders"].append(inventory)
                    elif current_inventory_type == "descriptors":
                        descriptors["descriptors"].append(inventory)
                    elif current_inventory_type == "prediction-models":
                        prediction_models["prediction_models"].append(inventory)
                    elif current_inventory_type == "software-tools":
                        software_tools["software_tools"].append(inventory)
                inventory = {}
                for key in items:
                    label = key
                    if key == "rdfs:label":
                        if inventory_type == "folders":
                            label = "folder_names"
                        elif inventory_type == "descriptors":
                            label = "descriptor_names"
                        elif inventory_type == "prediction-models":
                            label = "prediction_model_names"
                        elif inventory_type == "software-tools":
                            label = "name"
                    elif key == "rdfs:comment":
                        label = "description"
                    elif key == "mi:revision":
                        continue
                    elif key == "skos:prefLabel":
                        label = "preferred_name"
                    elif key == "qudt:dimensionSymbol":
                        label = key.split(":")[1]
                    elif key == "qudt:unit":
                        label = "unit_symbol"
                    elif key == "mi:approved":
                        label = "approval_status"
                    elif key == "dc:creator":
                        label = "created_by"
                    elif key == "dc:date":
                        label = "creation_time"
                    elif key == "mi:descriptor":
                        label = "descriptors"
                    elif key == "mi:inputDescriptor":
                        #label = "input_descriptors"
                        label = "input_ports"
                    elif key == "mi:outputDescriptor":
                        #label = "output_descriptors"
                        label = "output_ports"
                    elif key == "dcterms:modified":
                        label = "modified_time"
                    elif key == "mi:predictionModel":
                        label = "prediction_models"
                    elif key == "mi:predictionModelType":
                        label = "prediction_model_type_name"
                    elif key == "mi:license":
                        label = "license"
                    elif key == "mi:platform":
                        label = "platform"
                    elif key == "mi:version":
                        label = "version"
                    elif key == "descriptor_id":
                        if inventory_type == "folders":
                            label = "folder_id"
                        elif inventory_type == "descriptors":
                            label = "descriptor_id"
                        elif inventory_type == "prediction-models":
                            label = "prediction_model_id"
                        elif inventory_type == "software-tools":
                            label = "software_tool_id"
                    elif key == "mi:parentFolder":
                        label = "parentFolder"

                    contents = items[key].split("@")
                    items0 = items1 = items[key]
                    if len(contents) == 2:
                        items0 = contents[0]
                        items1 = contents[1]
                    if label == "descriptor_names":
                        if (label in inventory) is False:
                            inventory[label] = []
                        inventory[label].append({"name":items0, "laguage":items1})
                    elif label == "prediction_model_names":
                        if (label in inventory) is False:
                            inventory[label] = []
                        inventory[label].append({"name":items0, "laguage":items1})
                    elif label == "name":
                        inventory[label] = items0
                        inventory["language"] = items1
                    elif label == "preferred_name":
                        inventory[label] = items0
                        inventory["preferred_name_language"] = items1
                    #elif label == "input_descriptors" or label == "output_descriptors":
                    elif label == "input_ports" or label == "output_ports":
                        if (label in inventory) is False:
                            inventory[label] = []
                        ids = items0.split(',')
                        for id_item in ids:
                            if id_item == ".":
                                continue
                            inventory[label].append(id_item.strip('<>,').split("/")[-1])
                    elif label == "descriptors":
                        inventory[label] = {}
                        for item in items1.split(","):
                            if item == "":
                                continue
                            descriptor_id = item.split("/")[-1].split(">")[0]
                            inventory[label][descriptor_id] = ""
                    elif label == "prediction_models":
                        inventory[label] = {}
                        for item in items1.split(","):
                            if item == "":
                                continue
                            prediction_model_id = item.split("/")[-1].split(">")[0]
                            inventory[label][prediction_model_id] = ""
                    elif label == "folder_id":
                        inventory[label] = items1.split("/")[-1].split(">")[0]
                    elif label == "parentFolder":
                        inventory[label] = items0.split("/")[-1].split(">")[0]
                    elif label == "descriptor_id":
                        inventory["id_not_uri"] = items1.split("/")[-1].split(">")[0]
                        inventory[label] = items1
                    elif label == "prediction_model_id":
                        inventory["id_not_uri"] = items1.split("/")[-1].split(">")[0]
                        inventory[label] = items1
                    else:
                        if label == "approval_status":
                            if items0 == "未承認":
                                items0 = "N"
                            else:
                                items0 = "Y"
                        if items0 == "":
                            items0 = "null"
                        inventory[label] = items0

                current_inventory_type = inventory_type
        # foldersにある、記述子、予測モデルのIDに名前を設定する
        for folder in folders["folders"]:
            if ("descriptors" in folder) is True:
                for descriptor_in_folder in folder["descriptors"]:
                    for descritor_in_descriptor in descriptors["descriptors"]:
                        if descriptor_in_folder == descritor_in_descriptor["id_not_uri"]:
                            folder["descriptors"][descriptor_in_folder] = descritor_in_descriptor["preferred_name"]
            if ("prediction_models" in folder) is True:
                for prediction_in_folder in folder["prediction_models"]:
                    for prediction_in_prediction in prediction_models["prediction_models"]:
                        if prediction_in_folder == prediction_in_prediction["id_not_uri"]:
                            folder["prediction_models"][prediction_in_folder] = prediction_in_prediction["preferred_name"]
        # prediction_modelsのinput_ports/output_portsのIDを、記述子の内容に置き換える
        for prediction in prediction_models["prediction_models"]:
            #for input_port in prediction["input_ports"]:
            for i in range(len(prediction["input_ports"])):
                input_port = prediction["input_ports"][i]
                for descriptor in descriptors["descriptors"]:
                    if input_port == descriptor["id_not_uri"]:
                        prediction["input_ports"][i] = {}
                        prediction["input_ports"][i]["descriptor_id"] = descriptor["descriptor_id"]
                        if ("tag_list" in descriptor) is True:
                            prediction["input_ports"][i]["tag_list"] = descriptor["tag_list"]
                        else:
                            prediction["input_ports"][i]["tag_list"] = []
                        if ("description" in descriptor) is True:
                            prediction["input_ports"][i]["description"] = descriptor["description"]
                        else:
                            prediction["input_ports"][i]["description"] = "null"
                        prediction["input_ports"][i]["preferred_name"] = descriptor["preferred_name"]
                        if ("metadata_list" in descriptor) is True:
                            prediction["input_ports"][i]["metadata_list"] = descriptor["metadata_list"]
                        else:
                            prediction["input_ports"][i]["metadata_list"] = []
                        if ("port_display_name_ja" in descriptor) is True:
                            prediction["input_ports"][i]["port_display_name_ja"] = descriptor["port_display_name_ja"]
                        if ("port_display_name_en" in descriptor) is True:
                            prediction["input_ports"][i]["port_display_name_en"] = descriptor["port_display_name_en"]
                        prediction["input_ports"][i]["port_name"] = descriptor["preferred_name"]
                        prediction["input_ports"][i]["preferred_name_language"] = descriptor["preferred_name_language"]
            #for output_port in prediction["output_ports"]:
            for i in range(len(prediction["output_ports"])):
                output_port = prediction["output_ports"][i]
                for descriptor in descriptors["descriptors"]:
                    if output_port == descriptor["id_not_uri"]:
                        prediction["output_ports"][i] = {}
                        prediction["output_ports"][i]["descriptor_id"] = descriptor["descriptor_id"]
                        if ("tag_list" in descriptor) is True:
                            prediction["output_ports"][i]["tag_list"] = descriptor["tag_list"]
                        else:
                            prediction["output_ports"][i]["tag_list"] = []
                        if ("description" in descriptor) is True:
                            prediction["output_ports"][i]["description"] = descriptor["description"]
                        else:
                            prediction["output_ports"][i]["description"] = "null"
                        prediction["output_ports"][i]["preferred_name"] = descriptor["preferred_name"]
                        if ("metadata_list" in descriptor) is True:
                            prediction["output_ports"][i]["metadata_list"] = descriptor["metadata_list"]
                        else:
                            prediction["output_ports"][i]["metadata_list"] = []
                        if ("port_display_name_ja" in descriptor) is True:
                            prediction["output_ports"][i]["port_display_name_ja"] = descriptor["port_display_name_ja"]
                        if ("port_display_name_en" in descriptor) is True:
                            prediction["output_ports"][i]["port_display_name_en"] = descriptor["port_display_name_en"]
                        prediction["output_ports"][i]["port_name"] = descriptor["preferred_name"]
                        prediction["output_ports"][i]["preferred_name_language"] = descriptor["preferred_name_language"]

        # 2021/02/16 出力を抑制する。
        #descout = open("kushida_descriptors.json", "w")
        #predict = open("kushida_prediction-models.json", "w")
        #software = open("kushida_software-tools.json", "w")
        folderout = open("folders.json", "w")
        #json.dump(descriptors, descout, indent=4, ensure_ascii=False)
        #json.dump(prediction_models, predict, indent=4, ensure_ascii=False)
        #json.dump(software_tools, software, indent=4, ensure_ascii=False)
        json.dump(folders, folderout, indent=4, ensure_ascii=False)
        #descout.close()
        #predict.close()
        #software.close()
        folderout.close()

        # 2021/02/16 以下は実行しない
        return

        descout = open("descriptors.json", "w")
        predict = open("prediction-models.json", "w")
        software = open("software-tools.json", "w")
        for item in descriptors:
            descout.write("{\n")
            descout.write('    "%s": [\n'%item)
            #for items in descriptors[item]:
            for i in range(len(descriptors[item])):
                items = descriptors[item][i]
                descout.write("        {\n")
                kitem_keys = items.keys()
                for k in range(len(kitem_keys)):
                    item_key = list(kitem_keys)[k]
                #for item_key in items:
                    #item_key = item_keys[i]
                    if item_key == "descriptor_names":
                        descout.write('            "%s": [\n'%item_key)
                        descout.write('                {\n')
                        for l in range(len(items[item_key])):
                            subitem_keys = items[item_key][l].keys()
                            for m in range(len(subitem_keys)):
                                subitem_key = list(subitem_keys)[m]
                                if m == len(subitem_keys) - 1:
                                    descout.write('                    "%s": "%s"\n'%(subitem_key, items[item_key][l][subitem_key]))
                                else:
                                    descout.write('                    "%s": "%s",\n'%(subitem_key, items[item_key][l][subitem_key]))
                        if l == len(items[item_key]) - 1:
                            descout.write('                }\n')
                        else:
                            descout.write('                },\n')
                        if k == len(items) - 1:
                            descout.write('            ]\n')
                        else:
                            descout.write('            ],\n')
                    else:
                        if k == len(items) - 1:
                            descout.write('            "%s": "%s"\n'%(item_key, items[item_key]))
                        else:
                            descout.write('            "%s": "%s",\n'%(item_key, items[item_key]))
                if i == len(descriptors[item]) - 1:
                    descout.write("        }\n")
                else:
                    descout.write("        },\n")
            descout.write("    ]\n")
        descout.write("}\n")
        for item in prediction_models:
            predict.write("{\n")
            predict.write('    "%s": [\n'%item)
            #for items in prediction_models[item]:
            for i in range(len(prediction_models[item])):
                items = prediction_models[item][i]
                predict.write("        {\n")
                item_keys = items.keys()
                for k in range(len(item_keys)):
                    item_key = list(item_keys)[k]
                #for item_key in items:
                    if item_key == "prediction_model_names":
                        predict.write('            "%s": [\n'%item_key)
                        predict.write('                {\n')
                        for l in range(len(items[item_key])):
                            subitem_keys = items[item_key][l].keys()
                            for m in range(len(subitem_keys)):
                                subitem_key = list(subitem_keys)[m]
                                if m == len(subitem_keys) - 1:
                                    predict.write('                    "%s": "%s"\n'%(subitem_key, items[item_key][l][subitem_key]))
                                else:
                                    predict.write('                    "%s": "%s",\n'%(subitem_key, items[item_key][l][subitem_key]))
                        if l == len(items[item_key]) - 1:
                            predict.write('                }\n')
                        else:
                            predict.write('                },\n')
                        #for subitem in items[key]:
                        #    for subkey in subitem:
                        #        predict.write('                    "%s": "%s"\n'%(subkey, subitem[subkey]))
                        #predict.write('                }\n')
                        if k == len(item_keys) - 1:
                            predict.write('            ]\n')
                        else:
                            predict.write('            ],\n')
                    elif item_key == "input_descriptors" or item_key == "output_descriptors":
                        predict.write('            "%s": [\n'%item_key)
                        for m in range(len(items[item_key])):
                        #for subitem in items[item_key]:
                            if m == len(items[item_key]) - 1:
                                predict.write('                    "%s"\n'%items[item_key][m])
                            else:
                                predict.write('                    "%s",\n'%items[item_key][m])
                        if k == len(item_keys) - 1:
                            predict.write('            ]\n')
                        else:
                            predict.write('            ],\n')
                    else:
                        if k == len(item_keys) - 1:
                            predict.write('            "%s": "%s"\n'%(item_key, items[item_key]))
                        else:
                            predict.write('            "%s": "%s",\n'%(item_key, items[item_key]))
                if i == len(prediction_models[item]) - 1:
                    predict.write("        }\n")
                else:
                    predict.write("        },\n")
            predict.write("    ]\n")
        predict.write("}\n")
        for item in software_tools:
            software.write("{\n")
            software.write('    "%s": [\n'%item)
            for i in range(len(software_tools[item])):
            #for items in software_tools[item]:
                items = software_tools[item][i]
                software.write("        {\n")
                item_keys = items.keys()
                for l in range(len(item_keys)):
                #for key in items:
                    key = item_keys[l]
                    if key == "software_tool_names":
                        software.write('            "%s": [\n'%key)
                        software.write('                {\n')
                        for subitem in items[key]:
                            for subkey in subitem:
                                software.write('                    "%s": "%s"\n'%(subkey, subitem[subkey]))
                        software.write('                }\n')
                        if l == len(item_keys) - 1:
                            software.write('            ]\n')
                        else:
                            software.write('            ],\n')
                    elif key == "input_descriptors" or key == "output_descriptors":
                        software.write('            "%s": [\n'%key)
                        for m in range(len(items[key])):
                        #for subitem in items[key]:
                            if m == len(items[key]) - 1:
                                software.write('                    "%s"\n'%items[key][m])
                            else:
                                software.write('                    "%s",\n'%items[key][m])
                        if l == len(item_keys) - 1:
                            software.write('            ]\n')
                        else:
                            software.write('            ],\n')
                    else:
                        if l == len(item_keys) - 1:
                            software.write('            "%s": "%s"\n'%(key, items[key]))
                        else:
                            software.write('            "%s": "%s",\n'%(key, items[key]))
                if i == len(software_tools[item]) - 1:
                    software.write("        }\n")
                else:
                    software.write("        },\n")
            software.write("}\n")
    
        descout.close()
        predict.close()
        software.close()

def main():
    '''
    デバッグ用開始点
    '''

    params_len = len(sys.argv)
#    if params_len < 4:
#       print "python param_operater.py <src> <width %> <number> [d type] [seed]"
#       print "    src : \u5143\u306b\u3057\u305f\u3044\u5024"
#       print "    width: \u4e71\u6570\u767a\u751f\u306e\u5e45\uff08\uff05\uff09"
#       print "    number: \u4e71\u6570\u767a\u751f\u3055\u305b\u308b\u6570(int)"
#       print "    d type: \u5206\u5e03\u30bf\u30a4\u30d7\uff08\u30c7\u30d5\u30a9\u30eb\u30c8\u306fnormal\uff09"
#       print "    seed: \u4e71\u6570\u306e\u7a2e"

#    app = wx.App(False)
    org = InventoryRdfOperator()
    org.ReadRDFFile(sys.argv[1])
#    org.Show()
    #analyze_inventory_json("kushida_descriptors.json", "kushida_prediction-models.json", "kushida_software-tools.json", "descriptors.conf", "prediction-models.conf", "software-tools.conf")
#    app.MainLoop()

if __name__ == '__main__':
    main()

