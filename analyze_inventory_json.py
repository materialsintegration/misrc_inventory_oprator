#!/usr/local/python2.7/bin/python
# -*- coding: utf-8 -*-

'''
インベントリーAPI出力のJSONを分解する。
'''
import os, sys
if sys.version_info[0] <= 2:
    import ConfigParser
else:
    import configparser
import json
    
def analyze_inventory_json(descriptor_ref_json, prediction_ref_json, software_tool_ref_json, descriptor_upd_conf, prediction_upd_conf, software_tool_upd_conf):
    '''
    APIが出力したJSONファイルを登録用プログラムが扱える形式に分解する。
    '''
    
    if sys.version_info[0] <= 2:
        descriptor_parser = ConfigParser.SafeConfigParser()
        prediction_parser = ConfigParser.SafeConfigParser()
        software_tool_parser = ConfigParser.SafeConfigParser()
    else:
        descriptor_parser = configparser.ConfigParser()
        prediction_parser = configparser.ConfigParser()
        software_tool_parser = configparser.ConfigParser()
    
    # 記述子用
    descriptor_parser.add_section("authorize")
    descriptor_parser.set("authorize", "user_id", "")
    descriptor_parser.set("authorize", "token", "")
    descriptor_parser.add_section("object")
    descriptor_parser.set("object", "object", "descriptors")
    descriptor_parser.add_section("resource")
    descriptor_parser.set("resource", "url", "descriptors")
    descriptor_parser.set("resource", "query", "")
    descriptor_parser.set("resource", "action", "post")
    descriptor_parser.add_section("output")
    descriptor_parser.set("output", "ftype", "json")
    # 予測モデル用
    prediction_parser.add_section("authorize")
    prediction_parser.set("authorize", "user_id", "")
    prediction_parser.set("authorize", "token", "")
    prediction_parser.add_section("object")
    prediction_parser.set("object", "object", "prediction_models")
    prediction_parser.add_section("resource")
    prediction_parser.set("resource", "url", "prediction-models")
    prediction_parser.set("resource", "query", "")
    prediction_parser.set("resource", "action", "post")
    prediction_parser.add_section("output")
    prediction_parser.set("output", "ftype", "json")
    # software_tool
    software_tool_parser.add_section("authorize")
    software_tool_parser.set("authorize", "user_id", "")
    software_tool_parser.set("authorize", "token", "")
    software_tool_parser.add_section("object")
    software_tool_parser.set("object", "object", "software_tools")
    software_tool_parser.add_section("resource")
    software_tool_parser.set("resource", "url", "software_tools")
    software_tool_parser.set("resource", "query", "")
    software_tool_parser.set("resource", "action", "post")
    software_tool_parser.add_section("output")
    software_tool_parser.set("output", "ftype", "json")
    
    # 分解-記述子
    infile = open(descriptor_ref_json)
    descriptors = json.load(infile)
    infile.close()
    descriptor_parser.add_section("file")
    descriptor_jsons = ""
    for item in descriptors["descriptors"]:
        did = item["descriptor_id"].split("/")[-1]
        filename = "inventory_%s.json"%did
        outfile = open(filename, "w")
        print("processing %s..."%filename)
        json.dump(item, outfile, indent=2, ensure_ascii=False)
        outfile.close()
        if descriptor_jsons == "":
            descriptor_jsons += "%s\n"%filename
        else:
            descriptor_jsons += "           %s\n"%filename
    descriptor_parser.set("file", "inputfile", descriptor_jsons)
    outfile = open(descriptor_upd_conf, "w")
    descriptor_parser.write(outfile)
    outfile.close()
    # 分解-予測モデル
    infile = open(prediction_ref_json)
    predictions = json.load(infile)
    infile.close()
    prediction_parser.add_section("file")
    prediction_jsons = ""
    for item in predictions["prediction_models"]:
        mid = item["prediction_model_id"].split("/")[-1]
        filename = "inventory_%s.json"%mid
        outfile = open(filename, "w")
        json.dump(item, outfile, indent=2, ensure_ascii=False)
        outfile.close()
        if prediction_jsons == "":
            prediction_jsons += "%s\n"%filename
        else:
            prediction_jsons += "           %s\n"%filename
    prediction_parser.set("file", "inputfile", prediction_jsons)
    outfile = open(prediction_upd_conf, "w")
    prediction_parser.write(outfile)
    outfile.close()
    # 分解-ソフトウェアツール
    infile = open(software_tool_ref_json)
    software_tools = json.load(infile)
    infile.close()
    software_tool_parser.add_section("file")
    software_tool_jsons = ""
    for item in software_tools["software_tools"]:
        mid = item["software_tool_id"].split("/")[-1]
        filename = "inventory_%s.json"%mid
        outfile = open(filename, "w")
        json.dump(item, outfile, indent=2, ensure_ascii=False)
        outfile.close()
        if software_tool_jsons == "":
            software_tool_jsons += "%s\n"%filename
        else:
            software_tool_jsons += "           %s\n"%filename
    software_tool_parser.set("file", "inputfile", software_tool_jsons)
    outfile = open(software_tool_upd_conf, "w")
    software_tool_parser.write(outfile)
    outfile.close()

