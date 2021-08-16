# FlashText
RSVPっぽいやつ

## 概要
RSVP（Rapid Serial Visual Presentation）っぽいもの  
文章を区切って，短い単位で高速に表示することで，目を動かさなくても文章を読むことができるもの  

## 前提ライブラリ
- MeCab
    - MeCab
    - subprocessを使ってMeCabに処理を渡しているので，Python用のライブラリは利用していない．
- PySimpleGUI 
    - GUI表示用
    - `pip install pysimplegui`
    - Tkinterが前提として必要(Pythonインストール時に設定するなど)

## 使い方
`python flashtext.py {Filename} {Interval millsec} [Line] [Phrase]`
Filename: 読みたい文書のテキストファイルを指定する  
Intreval time: 区切りごとの表示時間を設定する（ミリ秒指定）  
Line: 任意引数 指定行から開始できる  
Phrase: 任意引数 行が指定されているとき，その行の何区切り目かを指定できる．  

起動すると，ファイル名が表示されているので，左のStartを押すと開始する．  
Startボタンは，押されると自動的にPauesボタンになり以降，Pause/Resumeボタンとして利用される．  
Exitボタンを押すと終了する．終了時に読了した行と区切りの数をコンソール側に出力する．続きから読むときはこの値を指定して起動する  

## 追加実装メモ
- 文字列長に合わせて時間の比率を変更
    - 漢字を含む場合はより長く？
    - パラメータの例が無いので，適当に設定
- コマンドライン引数の解析が適当なのでパーサーを使う
- regex
- 句読点が末尾に来る場合は，全体的に文字の位置を右にズラしたほうが見やすそう