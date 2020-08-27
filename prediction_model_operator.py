#!python3.6
# -*- coding: utf-8 -*-

'''
予測モデル１こを取得する
'''

import requests
import sys, os
from openam_operator import openam_operator
from getpass import getpass
import json

def prediction_add_model_type_code(prediction, version=5):
    '''
    予測モデルモデルタイプコードの追加(API Version5まで)
    '''

    if version != 5:
        return prediction
    # copy to
    new_prediction = {}
    new_prediction["preferred_name"] = prediction["preferred_name"]
    new_prediction["preferred_name_language"] = prediction["preferred_name_lang"]
    new_prediction["prediction_model_alias_names"] = prediction["prediction_model_names"][1:]
    new_prediction["description"] = prediction["description"]
    if ("prediction_model_type_name" in prediction) is True:
        if prediction["prediction_model_type_name"] == "理論モデル":
            new_prediction["prediction_model_type_code"] = 10
        elif prediction["prediction_model_type_name"] == "経験モデル":
            new_prediction["prediction_model_type_code"] = 20
        else:
            new_prediction["prediction_model_type_code"] = 30
    new_prediction["input_ports"] = prediction["input_ports"]
    new_prediction["output_ports"] = prediction["output_ports"]
    new_prediction["metadata_list"] = prediction["metadata_list"]

    return new_prediction

def prediction_get(hostname, p_id):
    '''
    予測モデルの詳細を取得する
    @param hostname (string)
    @param p_id (string)
    @retval json 
    '''

    print("予測モデルを取得する側のログイン情報入力")
    if sys.version_info[0] <= 2:
        name = raw_input("ログインID: ")
    else:
        name = input("ログインID: ")
    password = getpass("パスワード: ")

    ret, uid, token = openam_operator.miauth(hostname, name, password)
    if ret is False:
        if uid.status_code == 401:
            print(uid.json()["message"])
        sys.exit(1)
    session = requests.Session()
    url = "https://%s:50443/inventory-api/v6/prediction-models/%s"%(hostname, p_id)
    app_format = 'application/json'
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': app_format,
               'Accept': app_format}


    ret = session.get(url, headers=headers)
    if ret.status_code != 500:
        print("%s の予測モデルの詳細情報を取得しました"%p_id)
        #print(json.dumps(ret.json(), indent=2))
        pass
    else:
        print(ret.text)
        sys.exit(1)

    prediction = ret.json()
    outfile = open("prediction-%s.json"%p_id, "w")
    json.dump(ret.json(), outfile, indent=2, ensure_ascii=False)
    outfile.close()

    return prediction, headers

def prediction_copy(prediction, hostname, headers):
    '''
    予測モデル複製
    '''

    new_prediction = prediction_add_model_type_code(prediction, version=6)
    
    session = requests.Session()
    url = "https://%s:50443/inventory-update-api/v6/prediction-models"%hostname
    #print(url)
    ret = session.post(url, headers=headers, json=new_prediction)
    if ret.status_code != 500:
        print(ret.json())

def prediction_add_discriptor(prediction, p_id, hostname, headers):
    '''
    記述子追加
    '''

    session = requests.Session()
    while True:
        print("追加する記述子IDの入力")
        if sys.version_info[0] <= 2:
            d_id = raw_input("記述子ID: ")
        else:
            d_id = input("記述子ID: ")
    
        if d_id == "":
            print("予測モデルを変更して終了します。")
            break
        if d_id == "end":
            print("予測モデルを変更せずに終了します。")
            return
    
        if d_id.startswith("D") is False:
            print("記述子のフォーマットが違います。Dxxxxxyyyyyyyyyy(%s)"%d_id)
            continue

        url = "https://%s:50443/inventory-api/v6/descriptors/%s"%(hostname, d_id)
        ret = session.get(url, headers=headers)
        if ret.status_code != 200:
            print("記述子取得失敗")
            print(ret.text)
            continue
        print("記述子名(%s):%s"%(d_id, ret.json()["preferred_name"]))
        if sys.version_info[0] <= 2:
            io = raw_input("to input(1) / to output(2): ")
        else:
            io = input("to input(1) / to output(2): ")
        if io != "1" and io != "2":
            continue

        new_port = {}
        new_port["port_name"] = ret.json()["preferred_name"]
        new_port["required"] = "true"
        new_port["descriptor_id"] = ret.json()["descriptor_id"]
        new_port["description"] = ret.json()["description"]
        new_port["tag_list"] = []
        new_port["metadata_list"] = []

        if io == "1":
            is_same = False
            for item in prediction["input_ports"]:
                if item["port_name"] == ret.json()["preferred_name"]:
                    is_same = True
            if is_same is True:
                print("ポート名(%s) はすでに入力ポートに登録があります。"%ret.json()["preferred_name"])
                continue
            prediction["input_ports"].append(new_port)
        else:
            is_same = False
            for item in prediction["output_ports"]:
                if item["port_name"] == ret.json()["preferred_name"]:
                    is_same = True
            if is_same is True:
                print("ポート名(%s) はすでに出力ポートに登録があります。"%ret.json()["preferred_name"])
                continue
            prediction["output_ports"].append(new_port)

    url = "https://%s:50443/inventory-update-api/v6/prediction-models/%s"%(hostname, p_id)
    ret = session.put(url, headers=headers, json=prediction)

    outfile = open("prediction-%s.json"%p_id, "w")
    json.dump(prediction, outfile, indent=2, ensure_ascii=False)
    outfile.close()

    if ret.status_code != 200 and ret.status_code != 201:
        print("変更に失敗しました。")
        print(ret.text)
        return
    else:
        print(ret.text)
        
def main():
    '''
    開始点
    '''

    if len(sys.argv) < 4:
        if len(sys.argv) == 2:
            print("予測モデルIDを指定してください。")
        elif len(sys.argv) == 1:
            print("サイトURL(from)を指定してください。")
        print("")
        print("予測モデル複製プログラム")
        print("Usage:")
        print("$ python3.6 %s <site_url> <prediction model id> <mode>"%(sys.argv[0]))
        sys.exit(1)

    hostname = sys.argv[1]
    p_id = sys.argv[2]
    mode = sys.argv[3]

    if mode == "copy":
        p_dict, h = prediction_get(hostname, p_id)
        prediction_copy(p_dict, hostname, h)
    elif mode == "get":
        p_dict, h = prediction_get(hostname, p_id)
    elif mode == "put_desc":
        p_dict, h = prediction_get(hostname, p_id)
        prediction_add_discriptor(p_dict, p_id, hostname, h)
        pass

if __name__ == '__main__':
    main()

