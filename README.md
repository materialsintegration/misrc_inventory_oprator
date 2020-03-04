# Inventory-Operatorマニュアル

## 概要
本マニュアルはInventoryAPIを利用して、サイト間の記述子、予測モデル、ソフトウェアツールを展開するためのソフトウェアのインストール、利用方法を記述します。

## システム要件
* python2.xおよびwxpython3.xが動作する、Linux/Windows/(MacOS)。
* python3.6以降およびwxpython4.0.6以降が動作する、Linux/Windows/(MacOS)
※ MacOSは未確認。（以前の経験上、動作は可能なはず）
* 追加のパッケージ
  + requests(security)
  + authentication-operator(SSO対応)
  + module_copy(Inventory操作本体)
  + MI-API(1.2.0以降)
  + webapi(misrc_webapi)

# 管理編
## wxPython
wxPythonのインストール方法。
### Windows
以下のURLから python2.7系をインストールしている場合は、wxPython3.0-win64-3.0.2.0-py27.exeを取得、python2.6系をインストールしている場合は wxPython3.0-win64-3.0.2.0-py26.exeを取得し、インストールする。
https://sourceforge.net/projects/wxpython/files/wxPython/3.0.2.0/

### CentOS6とpython2.7
Windowsと同じURLから wxPython-src-3.0.2.0.tar.bz2 を取得する。
適当な場所に展開し、以下を実施する。
```
# tar xfj wxPython-src-3.0.2.0.tar.bz2
# cd wxPython-src-3.0.2.0/wxPython
# python setup.py install
```
pythonはシステムデフォルトまたは別インストールしたpython2.7などを使用する。

### CentOS7とpython2.7
CentOS7では環境が新しいためか、安全なインストール方法がまだほとんどありません。（検索してもあまりヒットしない）。WindowsやCentOS6用のパッケージもインストールに失敗します。このためEPELの早期？バージョンなどを取得して、yumでEPELの依存ライブラリをインストールした後、本体インストールというやや変則的なインストールを行います。また、実行中もワーニングがたくさん出るので、あまりおすすめじゃないかもしれません。GUIも表示が

以下のURLから、wxPython-3.0.2.0-11.el7.centos.x86_64.rpmを取得する。

https://copr-be.cloud.fedoraproject.org/results/erp/wxpython-3.0.2/epel-7-x86_64/00605775-wxPython/

yumで依存ライブラリをインストールしておく。
```
# yum install epel-release -y
# yum install --enablerepo=epel wxGTK wxGTK3 wxGTK-devel wxGTK3-devel wxBase wxBase3 wxGTK-media wxGTK-gl wxGTK3-media wxGTK3-gl
```
本体をrpmコマンドでインストールする。
```
# rpm -ivh wxPython-3.0.2.0-11.el7.centos.x86_64.rpm
```

pythonはシステムデフォルト(2.7.5)を使用する。

### CentOS7とpython3.6以降
wxpython3.xはpython3では対応していないため使用不可である。しかしCentOS7とpython2.7のものより比較的簡単に構築が可能になっている。手順は以下のとおり。
* gtk3およびgtk3-develのインストール(yum)
* pathlib2のインストール(pip)
* wxpythonのインストール(pip)

※ gtk3は既にインストール済みかもしれないので、rpm -q -aなどで確認し、インストール済みならgtk3-develのみインストールするなど適宜対応を変えること。  
※ pathlib2とwxpythonのインストールは一緒にはできないので、別々に実施すること。

### 動作確認
pythonを実行し、wxライブラリをimportしてみる。
```
$ python
>>> import wx
>>>
```
なにも表示されなければインストールは正常。
以下のようなら、何かしら失敗している。
```
$ python
>>> import wx
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: No module named wx
>>> 
```
## インストールと実行
本体はgitで管理しています。以下のように適当な場所で、git cloneして実行してください。
```
$ git clone ssh://git@gitlab.mintsys.jp:50022/midev/inventory-operator.git
$ cd inventory-operator
$ python inventory-operator.py
```

## ユーザー情報
InventoryAPIはアクセスのために、必要な情報として、以下の３つがあります。
* URL
    * 操作対象のサイトへのURL（選択）
* ログインID
* ログインパスワード

Inventory-APIへのアクセスキーとして各ユーザー毎のトークンを使用するが、本スクリプトではログインIDとパスワードからMIntシステムが用意しているSSOの機能を利用して取得する。URLは操作対象のMIntシステムを指定するものである。この値は保存されるが、ログインIDとログインパスワードは保存されない。

## configファイル
プログラムの動作上、必要な設定値、保存値などはinventory-operator.iniにiniファイル形式で保存される。記述子、予測モデル、ソフトウェア・ツールを取得した内容は、このファイルで指定したディレクトリのそれぞれのファイルに保存される。

※ ファイルはiniファイルのフォーマットで記述されます。  
※ 存在しない場合、プログラムが自動的に作成します。  
※ プログラムの最初の起動後、一旦終了し、iniファイルの内容を見直し、必要なら設定し直しを行うこと。  

### ファイル内容
見直すべき項目など記述する。

* Systemセクション
    + インベントリ登録に使用するサブモジュールの場所を指定する。
* Referenceセクション
    + 参照タブでの保存値。
    + urlキー：サーバー名を保存している
    + conffile：ワーキングディレクトリの場所
    + descriptor_conf : 記述子用構成ファイルの名前
    + prediction_conf : 予測モデル用構成ファイルの名前
    + software_took_conf : ソフトウェアツール用構成ファイルの名前
* Updateセクション
    + 更新タブでの保存値。保存内容の詳細はReferenceセクションと以下を除き同一。
    + folder_info : 登録プログラムが使用するインベントリ辞書・フォルダの構成ファイル
    + modules_xml_info : インベントリ登録後に作成される新旧対応表を使用して作成するインポート用modules.xmlの元のファイル名。
* Serversセクション
    + 操作対象のサーバーURLを書き連ねる。
    + このURLがセクション名となり、サーバー毎の情報を設定する。
* サーバー名セクション
    + 各サーバー毎の設定値
    + version : APIのバージョン番号

### その他の設定ファイル
* Inventory.confファイル
    + ワーキングディレクトリ中に作成される。
    + 主にインベントリ取得時の動作設定が記述される。
    + authorizeセクション
        - user_id：GUIで選択したユーザー名のID。プログラムが自動的に記入します。
        - token：GUIで選択したユーザー名のトークン。プログラムが自動的に記入します。
    + resourceセクション
        - url：GUIで選択した取得または登録先のサイトURL。プログラムが自動的に記入します。
        - query：API用のクエリ文字列。今バージョンでは使用しません。
    + fileセクション
        - 基本的にそのままとします。プログラムが自動的に作成します。
        - object：取得、登録用エンドポイントパス名
        - inputfile：登録したい記述子、予測モデル、ソフトウェア・ツールの格納ファイル名。
        - outputfile：取得した記述子、予測モデル、ソフトウェア・ツールの格納ファイル名。
        - modules.xml：登録時、登録内容に沿って変更したいモジュールをmodules.xmlから抜粋した部分。 

* インベントリ用構成ファイル
  + inventory-operator.iniのReference/Updateセクションの```*_conf```ファイル
  + 取得では使用されない
  + 登録で登録用プログラムが使用する。
  + 内容は取得時作成される。

# 利用者編

## 使用方法(GUI編)
このツールは記述子、予測モデル、ソフトウェア・ツールを元になるサイトの辞書から取得して、
展開先のサイトの辞書へ登録するスタイルです。辞書から辞書へです。
そのため、細かな記述子、予測モデル、ソフトウェア・ツールの個別選択はできません。

### サイト間展開
* まずは記述子の取得  
![inventory-get.png](images/reference.png)

1. 「インベントリから取得」タブをクリック
1. 作業ディレクトリを指定する
1. サーバー設定（取得用）を設定する
1. 辞書・フォルダー一覧をクリック
1. 希望の辞書をクリック
1. Inventory取得ボタンをクリック

* 取得できたら、登録  
![inventory-post.png](images/update.png)

1. インベントリへの投入または削除タブをクリック
1. 作業ディレクトリを指定する（取得時のディレクトリなど）
1. modules.xmlを指定する
1. サーバー設定（投入または削除用）を指定する。
1. 投入（辞書・フォルダー作成）をクリック

※上記以外の設定項目はそのままでよい

* 登録情報が旧バージョンの辞書to辞書用のデータの場合
1. 作業ディレクトリを指定する（取得時のディレクトリなど）
1. サーバー設定（投入または削除用）を指定する。
1. 辞書・フォルダ一覧をクリック
1. 希望の辞書をクリック
1. 辞書へ投入をクリック
 
※１、辞書to辞書のコピーを行う場合は展開先の辞書は予め作成しておいてください。
※２、作業ディレクトリはiniファイルに保存されます。
※３、取得した記述子は実行したシェルにログとして表示されます。

### 削除
同じように辞書単位での削除です。
![delete-dialog.png](http://192.168.1.34:3000/files/5b8521cd4943485079c50f42)

1. イベントリへの投入または削除タブをクリック
1. ユーザー情報（投入または削除用）を選択
1. 辞書・フォルダ一覧をクリック
1. 希望の辞書をクリック
1. 削除ボタンをクリック
1. 一覧に表示された記述子、予測モデル、ソフトウェア・ツールのうち、削除したいものの左にあるチェックボックスにチェックを入れてOKボタンをクリックします

※１、一番上のカラムの「check」「uncheck」をクリックすると、全項目のチェックをon/offできます。
※２、赤い記述子、予測モデル、ソフトウェア・ツールはそれ自体は削除済みですが、辞書のエントリから削除されていないものと推測されます。今の所これを削除する方法は不明です。仕様を変更して赤くなる記述子、予測モデル、ソフトウェア・ツールは表示しないようにするかもしれません。

## 使用方法（非GUI編）
このツールは記述子、予測モデル、ソフトウェアツールをinventory APIにより取り出したJSONファイルがそれぞれ存在していれば、限定的であるがGUIを使用しなくても記述子、予測モデル、ソフトウェアツールを追加することが可能である。その場合の方法を記述する。
### 設定
Inventory.confファイルに下記の用に設定を実施する。
* ログイン情報（トークンなど）  
  authorizeセクションのuser_idに自身のUSER IDを、tokenに自身のAPI アクセストークンを指定する。
* 追加先の辞書の情報  
  resourceセクションのurlに追加先の辞書IDを指定する。
* 記述子、予測モデル、ソフトウェアツールの各ファイル名  
  fileセクションのinputfileに3行にわけて、記述子、予測モデル、ソフトウェアツールの各ファイル名を指定する。
* 予測モジュール定義ファイルのファイル名  
  fileセクションのmodules.xmlに予測モジュール定義ファイルを指定する。

※ 辞書情報は、inventory画面において、inventoryを追加したい辞書を開いた状態で、ブラウザのURL欄の  
```
https://dev-u-tokyo.mintsys.jp/inventory/users/200000100000001/dictionaries/20000000818/folders/20000026418?sortOrder=asc&sortColumn=1&startPage=0&length=100&search=&type=&dispAccept=
```
のうち、  
```
users/200000100000001/dictionaries/20000000818/folders/20000026418
```
を辞書IDは接頭辞"D"と共に企業ID5桁（0前詰め）＋辞書ID10桁の15桁に、フォルダーIDも接頭辞"F"をと共に企業ID5桁（0前詰め）＋フォルダID10桁の15桁にして指定します。
```
users/200000100000001/dictionaries/D000020000000818/folders/F000020000026418
```


出来上がりの例(開発環境宛の設定例)
```
[authorize]
user_id = 200000100000001
token = 13bedfd69583faa62be240fcbcd0c0c0b542bc92e1352070f150f8a309f441ed

[resource]
url = users/200000100000001/dictionaries/D000020000000818/folders/F000020000026418
query = 

[file]
object = descriptor
           prediction-model
           software-tool
inputfile = dst_descriptors.json
               dst_prediction-models.json
               dst_software-tools.json
outputfile = src_descriptor.json
              src_prediction.json
              src_software_tool.json
modules.xml = modules.xml
```

### 実行
pythonプログラムを実行する。
* 使用方法
```
usage : python postInventory4.py <API URL>
```
* 実際の使用例
```
$ python3.6 postInventory4.py https://nims.mintsys.jp:50443/inventory-api/v5
```
