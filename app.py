from flask import Flask, make_response,render_template , request
import json

app = Flask(__name__)

#####################################
# 変換判定機 コード204を送るための判定機
#####################################
def number2kanji_checker(number):
    # 数字が漢字に変換できる条件を満たしているかを判定
    # 条件1:入力が数値である
    # 条件2:仕様通り、0以上1京(1e16)未満の整数である
    if number.isdecimal():#条件：数値であること
        int_number=int(number)
        if 0<=int_number and int_number < 1e16:
            return True
    else:
        return False

def kanji2number_checker(number):
    # 漢字が数字に変換できる条件を満たしているかを判定
    # 条件1: 最上位が10進漢字である
    # 条件2:入力が桁と10進漢字の交互である。ただし4組の桁"千""百""拾"から万進桁"万""億""兆"の連続はok
    # 条件3:万進桁は1回ずつ使われる。
    # 条件4:桁は順番に使われている
    # 条件5:4組の桁は万進桁がくるまでに2回使われていない
    kansuuji_list=["零","壱","弐","参","四","五","六","七",
                   "八","九","拾","百","千","万","億","兆"]
    decimal_list=["零","壱","弐","参","四",
                      "五","六","七","八","九"]
    keta_list=["拾","百","千"]
    keta_count=[0,0,0]
    mansin_list=["万","億","兆"]
    mansin_count=[0,0,0]
    mansin_useind=[-1,-1,-1]
    cross_flag=None #条件2の判定 10進漢字ならFalse,桁ならTrueに。
    continue_flag=False # 条件2の例外判定 千万などは連続してよい
    for ind,kanji in enumerate(list(number)):
        if cross_flag is None: #条件1 一番初めは10進漢字であるはず
            if kanji in decimal_list:
                cross_flag=False#
            else: 
                return False    
        else:
            if cross_flag==True:#次は10進漢字
                if kanji in decimal_list:
                    cross_flag=False
                    continue_flag=False
                elif continue_flag==True and kanji in mansin_list:
                    continue_flag=False
                    mansin_count[mansin_list.index(kanji)]+=1
                    mansin_useind[mansin_list.index(kanji)]=ind
                    keta_count=[0,0,0]
                else:
                    return False#連続で10進漢字
            elif cross_flag==False:#次は桁
                if kanji in keta_list:
                    keta_count[keta_list.index(kanji)]+=1
                    cross_flag=True
                    continue_flag=True # 万進桁なら連続してもよい
                elif kanji in mansin_list:
                    mansin_count[mansin_list.index(kanji)]+=1
                    mansin_useind[mansin_list.index(kanji)]=ind
                    keta_count=[0,0,0]
                    cross_flag=True
                    continue_flag=False
                else:
                    return False# 連続で桁
        if max(keta_count)>1:# 条件5
            print(keta_count)
            return False
    
    if max(mansin_count) >1:#条件3:万進桁は1回ずつ使われる。
        return False
    
    #条件4:桁は順番に使われている
    if mansin_useind[0] != -1:
        if mansin_useind[0]-mansin_useind[1]<=0 or mansin_useind[0]-mansin_useind[2]<=0:
            return False
    if mansin_useind[1] != -1:
        if mansin_useind[1]-mansin_useind[2]<=0:
            return False
    #/条件4
    return True

# /判定機
#####################################


#####################################
# 変換器 漢字2数字,数字2漢字に変換
#####################################

def number2kanji_function(number):
    """
    アラビア数字から漢字に変換する
    
        仕様より
            1.初めに下位から4桁ずつ区切り、"万","億","兆"の単位をつける
            2.上位から読み、4桁の組の中で"千","百","拾"を単位として区切り上位から読む
        
    """
    result_list=[]#結果を代入
    
    mansin_list=["","万","億","兆"]
    keta_list=["千","百","拾",""]
    number2kanji_dict={"0":"零","1":"壱","2":"弐","3":"参","4":"四",
                       "5":"五","6":"六","7":"七","8":"八","9":"九"}
    # 仕様1:下位から4桁ずつ区切り、「万」「億」「兆」の単位をつける
    reverse_number_list=list(str(int(number)))#整数値からstringのリストに変換
    reverse_number_list.reverse()#数値は下位から読む
    mansin_ind=0
    mansin_insert_flag=False
    for number_ind in range(0,len(reverse_number_list),4):#4桁区切りに「万」「億」「兆」の単位をつける
        reverse_number_list.insert(number_ind+mansin_ind,mansin_list[mansin_ind])
        mansin_ind+=1
    #/仕様1－1
    
    
    reverse_number_list.reverse()#上位に並び変え
    
    #仕様2　
    keta_ind=0-reverse_number_list.index(mansin_list[mansin_ind-1])%4#数字の個数によって、最上位の4桁の組の単位"千","百","拾"が決定
    
    reverse_number_list.remove("")
    for chenge_number in reverse_number_list:#上位から1つずつ読む
        if chenge_number in mansin_list:
            if mansin_insert_flag:
                result_list.append(chenge_number)
            mansin_insert_flag=False
            continue
        if chenge_number!="0":#基本、零は大字表記に使われない
            mansin_insert_flag=True
            result_list.append(number2kanji_dict[chenge_number])
            result_list.append(keta_list[keta_ind%4])#4組の桁は順にループすればよい
        keta_ind+=1
    
    if len(result_list)==0:#number=0のときのみlistに零を追加
        result_list.append(number2kanji_dict[chenge_number])

    while("" in result_list):#プログラム便宜上使用された""を排除
        result_list.remove("")
    
    return "".join(result_list)
    
def kanji2number_function(number):
    """大字表記から数字に変換する

    Args:
        number (string): 大字表記のstring

    Returns:
        result_list (list): 数字に変換した結果リスト
    
    逆から読むと、桁とばされ時の把握が容易である。
    逆から1文字ずつ読み、漢字はdictを使って変換する
    """
    kanji2number_dict={"零":"0","壱":"1","弐":"2","参":"3","四":"4",
                      "五":"5","六":"6","七":"7","八":"8","九":"9",
                      "拾":"a","百":"b","千":"c",
                      "万":"A","億":"B","兆":"C"}
    
    result_list=[]
    keman_list=["","拾","百","千",
                "万","拾","百","千",
                "億","拾","百","千",
                "兆","拾","百","千",""]
    number_list=list(number)
    
    number_list.reverse()#逆から読む
    add_number_flag=kanji2number_dict[number_list[0]].isdecimal()#一番後ろが桁か数字を把握
    mansin_exp_ind=0
    
    for number_kanji in number_list:#1字ずつ読む
        dict_result=kanji2number_dict[number_kanji]#漢字2数字変換
        
        if dict_result.isdecimal():#取得した値が数値
            if add_number_flag:#数値の追加が予期されている
                result_list.append(dict_result)#数字を追加
                mansin_exp_ind+=1#桁を進める
            add_number_flag=False
        else:#桁が来た
            while(keman_list[mansin_exp_ind]!=number_kanji):
                result_list.append("0")
                mansin_exp_ind+=1
                if mansin_exp_ind==16:
                    response = make_response('', 204)
                    return response                        
            add_number_flag=True        
          
    result_list.reverse()
    return int("".join(result_list))

#####################################

#####################################
# 漢字2数字,数字2漢字の本体
#####################################
@app.route("/v1/kanji2number/<number>", methods=["GET","POST"])
def kanji2number(number):
    if request.method=="GET":
        if kanji2number_checker(number):
            number= kanji2number_function(number)
        else:
            response = make_response('', 204)
            return response
    else:
        return response
    response = dict()
    response['result'] = number
    response_json = json.dumps(response)
    return response_json


@app.route("/v1/number2kanji/<number>", methods=["GET"])
def number2kanji(number):
    if number2kanji_checker(number):
        number= number2kanji_function(number)
    else:
        response = make_response('', 204)
        return response
    print(number)
    response = dict()
    response['result'] = number
    response_json = json.dumps(response,ensure_ascii=False)
    return response_json


#####################################


#####################################
# html制御 
#####################################
@app.route("/v1/number2kanji/")#number2kanjiに何も入力しなかった
def noform():
    return render_template('number2kanji.html')

@app.route("/v1/kanji2number/")#kanji2numberに何も入力しなかった
def noform2():
    return render_template('kanji2number.html')


@app.route('/', methods = ["GET" , "POST"])# ホスト
def sample_form():
    return render_template('index.html')

# 〜/index にアクセスがあった場合、index.htmlを描写する
@app.route('/index')
def post():
    return render_template('index.html')