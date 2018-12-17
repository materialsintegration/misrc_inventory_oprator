# Inventory-Operatorマニュアル

## 概要
本マニュアルはInventoryAPIを利用して、サイト間の記述子、予測モデル、ソフトウェアツールを展開するためのソフトウェアのインストール、利用方法を記述します。

## システム要件
* python2.xおよびwxpython3.xが動作する、Linux/Windows/(MacOS)。
※MacOSは未確認。（以前の経験上、動作は可能なはず）
* 追加のパッケージ
    * requests[security]

# 管理編
## wxPython
wxPythonのインストール方法。
### Windows
以下のURLから python2.7系をインストールしている場合は、wxPython3.0-win64-3.0.2.0-py27.exeを取得、python2.6系をインストールしている場合は wxPython3.0-win64-3.0.2.0-py26.exeを取得し、インストールする。
https://sourceforge.net/projects/wxpython/files/wxPython/3.0.2.0/

### CentOS6
Windowsと同じURLから wxPython-src-3.0.2.0.tar.bz2 を取得する。
適当な場所に展開し、以下を実施する。
```
# tar xfj wxPython-src-3.0.2.0.tar.bz2
# cd wxPython-src-3.0.2.0/wxPython
# python setup.py install
```
pythonはシステムデフォルトまたは別インストールしたpython2.7などを使用する。

### CentOS7
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
    * 操作対象のサイトへのURL
* ユーザID
* ユーザーのアクセストークン

Inventory-APIへのアクセスキーとして各ユーザー毎のトークンを使用しています。このトークンはユーザープロファイルのページかMI管理者に問い合わせて知ることができます。本プログラムではあらかじめinventory-operator.iniファイルにサイトに紐づくユーザーIDとトークンの組み合わせを保存してあります。このためユーザーのトークンが変更された場合は速やかにこのファイルの内容を変更する必要があります。

## configファイル
プログラムの動作上、必要な設定値、保存値などはInventory.confファイルとinventory-operator.iniにiniファイル形式で保存されています。記述子、予測モデル、ソフトウェア・ツールを取得した内容は、ファイルに保存されます。また登録の際に利用される記述子、予測モデル、ソフトウェア・ツールの内容もファイルに格納して使用されます。そのファイル名を格納しています。  
※ファイルはiniファイルのフォーマットで記述されます。  
※存在しない場合、プログラムが自動的に作成します。  
※現在格納される各ファイル名は固定値です。

### 保存値関連
* Updateセクション
更新タブでの保存値
    * urlキー：サーバー名を保存している
    * conffile：ワーキングディレクトリの場所
    * token：使用したトークン
    * userid：使用したユーザー名
* Referenceセクション
参照タブでの保存値。保存内容の詳細はUpdateセクションと同一。

### 設定値関連
* Inventory.confファイル
    * authorizeセクション
        * user_id：GUIで選択したユーザー名のID。プログラムが自動的に記入します。
        * token：GUIで選択したユーザー名のトークン。プログラムが自動的に記入します。
    * resourceセクション
        * url：GUIで選択した取得または登録先のサイトURL。プログラムが自動的に記入します。
        * query：API用のクエリ文字列。今バージョンでは使用しません。
    * fileセクション
        * 基本的にそのままとします。プログラムが自動的に作成します。
        * object：取得、登録用エンドポイントパス名
        * inputfile：登録したい記述子、予測モデル、ソフトウェア・ツールの格納ファイル名。
        * outputfile：取得した記述子、予測モデル、ソフトウェア・ツールの格納ファイル名。
        * modules.xml：登録時、登録内容に沿って変更したいモジュールをmodules.xmlから抜粋した部分。 

* inventory-operator.iniファイル
    * Updateセクション
        * インベントリ情報の移動先サーバーの情報などを以下のセットで保存している。
        * url
        * conffile
    * Referenceセクション
        * インベントリ情報の取得先サーバーの情報などを以下のセットで保存している。
        * url
        * conffile
    * Serversセクション  
        * 管理しているサイトのサーバー名をserversキーの値として記述します。
        * 列挙は改行後、タブコードに続いて次の項目を登録する形です。
    * 各URL名のセクション  
        * version：APIバージョンの番号(たぶん整数表記。実際のURLのV?に合わせる)

### 設定値の固定名について
Inventory.confのfileセクション内の文字列について、現在は固定値です。変更できるようにする予定はありますが、時期は未定です。以下に固定値の内容を記述します。
* fileセクション inputfileキー
    * 記述子用：kushida_descriptors.json
    * 予測モデル用：kushida_prediction-models.json
    * ソフトウェアツール用：kushida_software-tools.json
* fileセクション outputfileキー
    * 記述子用：kushida_descriptors.json
    * 予測モデル用：kushida_prediction-models.json
    * ソフトウェアツール用：kushida_software-tools.json
* fileセクション modules.xmlキー
    * modules-zeisei.xml

# 利用者編

## 使用方法
このツールは記述子、予測モデル、ソフトウェア・ツールを元になるサイトの辞書から取得して、
展開先のサイトの辞書へ登録するスタイルです。辞書から辞書へです。
そのため、細かな記述子、予測モデル、ソフトウェア・ツールの個別選択はできません。

### サイト間展開
* まずは記述子の取得
![inventory-get.png](http://192.168.1.34:3000/files/5b85222d4943485079c50f43)

1. インベントリから取得タブをクリック
1. ユーザー情報（取得用）を選択
　※Reference URLを変えるとUserNameとかTokenは選択可能なものに切り替わります。
1. 辞書・フォルダー一覧をクリック
1. 希望の辞書をクリック
1. Inventory取得ボタンをクリック
　※作業ディレクトリは/home/misystem/inventory-operator-0.0.1ならそのまま。

* 取得できたら、登録
![inventory-post.png](http://192.168.1.34:3000/files/5b8522504943485079c50f44)

1. インベントリへの投入または削除タブをクリック
1. ユーザー情報（投入または削除用）を選択
1. 辞書・フォルダ一覧をクリック
1. 希望の辞書をクリック
1. Inventory Putボタンをクリック

※１、展開先の辞書は予め作成しておいてください。
※２、削除ボタンは作成中で機能しません。
※３、ユーザー情報、作業ディレクトリはiniファイルに保存されます。
※４、URLがNIMSのものはUserNameなど入っていません。
※５、URLが旧環境のものは動作しません（削除予定です）
※６、取得した記述子は実行したシェルにログとして表示されます。

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

 
