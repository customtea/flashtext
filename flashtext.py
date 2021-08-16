import time
import sys
import subprocess
import PySimpleGUI as sg
import re
import os

re_hira = re.compile('[\u3041-\u309F]+') #ひらがなリスト
re_kata_zen = re.compile('[\u30A1-\u30FF]+') #全角カタカナ
re_kata_han = re.compile('[\uFF66-\uFF9F]+') #半角カタカナ
re_kanji = re.compile('[\u2E80-\u2FDF\u3005-\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\U00020000-\U0002EBEF]+') #漢字リスト

"""
#regexが使える場合
import regex
rex_hirakataascii = regex.compile(r'[\p{Script=Hiragana}\p{Script=Katakana}ーa-z]+')
rex_hira = regex.compile(r'\p{Script=Hiragana}+')
rex_kata = regex.compile(r'\p{Script=Katakana}+')
rex_kanji = regex.compile(r'\p{Script_Extensions=Han}+')
"""


def windowloop(allcontents, interval, in_countline, in_countphrase, filename):
    # Layout
    sg.theme("Material1")
    layout = [
        [sg.Text(filename,key="content",size=(25,1),font=("HGS教科書体",72), text_color="#000000", justification='center')],
        [sg.Button("Start",key="parbt", focus=True, size=(15,2)),sg.Text("",key="lineword",size=(15,2), font=("F5.6",20), justification='center', pad=((0,0),(20,0))),sg.Button("Exit",key="exit", size=(15,2))],
        ]
    window = sg.Window("Flash Text", layout, element_justification='center')
    
    # control flag veriable
    ptime = time.time()
    is_pause = True
    all_content_len = len(allcontents)
    count_line = in_countline
    count_line_word = in_countphrase
    ajs_interval = interval

    #Resume from argument
    if (in_countline > 0 or in_countphrase > 0):
        line = allcontents[in_countline]
    else:
        line = []

    #main loop
    while(True):
        # event switch
        event,value = window.read(timeout=20)
        if event in (None, sg.WIN_CLOSED, 'exit'):
            break
        if event == "parbt":
            if not is_pause:
                window["parbt"].update("Resume")
                is_pause = True
            else:
                window["parbt"].update("Pause")
                is_pause = False
        elif event == sg.TIMEOUT_KEY:
            # updating
            if not is_pause and time.time() - ptime >= ajs_interval:
                if count_line_word >= len(line):
                    if all_content_len == count_line:
                        window['content'].update("END")
                        break
                    line =  allcontents[count_line]
                    count_line += 1
                    count_line_word = 0
                    if not line: # 空行対策
                        line.append("")

                word = line[count_line_word]
                t = "L:{} W:{}".format(count_line+1, count_line_word+1)
                #print("DEBUG>>>L:{} W:{} => {}".format(count_line, count_line_word, word))
                window['content'].update(word)
                window['lineword'].update(t)
                count_line_word += 1
                ptime = time.time()
                
                # 表示する文節の文字数と，漢字の比率を計算し，次のインターバルタイムを調整する機能
                ## パラメータを考える必要があるが，ほぼ調整できていない
                c_phrase = len(word)
                if c_phrase != 0:
                    c_hira = len(''.join(re_hira.findall(word)))
                    c_kata = len(''.join(re_kata_zen.findall(word)))
                    c_kata += len(''.join(re_kata_han.findall(word)))
                    c_kanji = len(''.join(re_kanji.findall(word)))
                    r_kanji = c_kanji / c_phrase
                    #print("KanjiRatio:{}".format(r_kanji))
                    ajs_interval = interval + 0.5*r_kanji*100/1000 + c_phrase/100
                    #print("{} wait:{}".format(word,ajs_interval))
                else:
                    ajs_interval = interval

    print("end")
    print("ReadPoint Line:{} Phrase:{}".format(count_line, count_line_word))
    window.close()


def main(filename, interval, in_countline, in_countphrase):
    print("Mecab Processing ...")
    cmd  = "mecab " + filename 
    cmdres = subprocess.run(cmd, encoding='utf-8', shell=True, check=True, stdout=subprocess.PIPE)
    print("String concatnateing ...")
    cmdresdata = cmdres.stdout.splitlines()
    # 文節分かち書きのコードへ渡すための成形作業
    content = []
    tmpl = []
    for line in cmdresdata:
        #print(line)
        tmpl.append(line)
        if line == "EOS":
            content.append(tmpl)
            tmpl = []
    allcontent = []
    for sentence in content:
        wakatires = bunsetsuwakachi(sentence)
        #print(wakatires)
        allcontent.append(wakatires)
    windowloop(allcontent, interval, in_countline, in_countphrase, os.path.basename(filename))


def bunsetsuwakachi(text):
    m_result = text
    m_result = m_result[:-1] #最後の1行(EOS)は不要な行なので除く
    break_pos = ['名詞','動詞','接頭詞','副詞','感動詞','形容詞','形容動詞','連体詞'] #文節の切れ目を検出するための品詞リスト
    wakachi = [''] #分かち書きのリスト
    afterprepos = False #接頭詞の直後かどうかのフラグ
    aftersahennoun = False #サ変接続名詞の直後かどうかのフラグ
    afterkagikakko = False #括弧開の直後かどうかのフラグ
    for v in m_result:
        #print(v)
        if '\t' not in v: continue
        if '\u3000' in v: continue #全角空白をスキップ
        surface = v.split('\t')[0] #表層系（単語そのもの）
        pos = v.split('\t')[1].split(',') #品詞など
        pos_detail = ','.join(pos[1:4]) #品詞細分類（各要素の内部がさらに'/'で区切られていることがあるので、','でjoinして、inで判定する)
        #この単語が文節の切れ目とならないかどうかの判定
        nobreak = pos[0] not in break_pos #リストに入っているものは切れる
        nobreak = nobreak or '接尾' in pos_detail #接尾でないなら切れない
        nobreak = nobreak or (pos[0]=='動詞' and 'サ変接続' in pos_detail) #動詞かつサ変接続なら切れない
        nobreak = nobreak or '非自立' in pos_detail #非自立なら切れない
        nobreak = nobreak or afterprepos #接頭詞のあとなら切れない
        nobreak = nobreak or (aftersahennoun and pos[0]=='動詞' and pos[4]=='サ変・スル') #サ変接続名詞の後で勝つ動詞で，サ変スル活用なら切れない
        nobreak = nobreak or afterkagikakko #括弧開の直後なら切れない
        if nobreak == False or (len(wakachi[-1]) + len(surface)) > 5 and len(surface) >= 2: #ここが成立すると次の文節として登録 #全体が5文字以上になるときは結合しない
            wakachi.append("")
        wakachi[-1] += surface
        afterprepos = pos[0]=='接頭詞'
        aftersahennoun = 'サ変接続' in pos_detail
        afterkagikakko = '括弧開' in pos_detail
    if wakachi[0] == '': wakachi = wakachi[1:] #最初が空文字のとき削除する
    return wakachi


if __name__ == "__main__":
    argv = sys.argv
    count_line = 0
    count_phrase = 0
    argc =len(argv)
    if argc < 3 or argc > 5:
        print("{} FileName Interval(millsec) Line Phrase".format(argv[0]))
    else:
        filename = argv[1]
        interval = int(argv[2])/1000
        if argc == 4:
            count_line = int(argv[3])
        if argc == 5:
            count_line = int(argv[3])
            count_phrase = int(argv[4])

    main(filename, interval, count_line, count_phrase)