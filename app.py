from flask import Flask, make_response,render_template
import json

app = Flask(__name__)

def number2kanji_checker(number):
    
    if number.isdecimal():#条件：数値であること
        int_number=int(number)
        if 0<=int_number and int_number < 1e16:
            return True
    else:
        return False

def kanji2number_checker(number):
    kansuuji_list=["零","壱","弐","参","四","五","六","七",
                   "八","九","拾","百","千","万","億","兆"]
    
    return all(map(kansuuji_list.__contains__,list(number)))

def number2kanji_function(number):
    """
    アラビア数字から漢字に変換する
    
        アラビア数字は下から読み、数字に応じて漢字に変換
        桁数に応じて桁を追加
    """
    
    mansin_list=["","万","億","兆"]
    keta_list=["千","百","拾",""]
    number2kanji_dict={"0":"零","1":"壱","2":"弐","3":"参","4":"四",
                       "5":"五","6":"六","7":"七","8":"八","9":"九"}
    # 仕様1－1:下位から4桁ずつ区切り、「万」「億」「兆」の単位をつける
    reverse_number_list=list(str(int(number)))#整数値からstringのリストに変換
    reverse_number_list.reverse()#数値は下位から読む
    mansin_ind=0
    mansin_insert_flag=False
    for number_ind in range(0,len(reverse_number_list),4):#4桁区切りに「万」「億」「兆」の単位をつける
        reverse_number_list.insert(number_ind+mansin_ind,mansin_list[mansin_ind])
        mansin_ind+=1
    #/仕様1－1
    
    result_list=[]
    reverse_number_list.reverse()#
    
    keta_ind=0-reverse_number_list.index(mansin_list[mansin_ind-1])%4
    
    reverse_number_list.remove("")
    for chenge_number in reverse_number_list:
        if chenge_number in mansin_list:
            if mansin_insert_flag:
                result_list.append(chenge_number)
            mansin_insert_flag=False
            continue
        if chenge_number!="0":
            mansin_insert_flag=True
            result_list.append(number2kanji_dict[chenge_number])
            result_list.append(keta_list[keta_ind%4])
        keta_ind+=1
    
    if len(result_list)==0:
        result_list.append(number2kanji_dict[chenge_number])
    print(result_list)
    print("".join(result_list))
    return result_list
    
    
    
    
    # number2kanji_dict={"0":"零","1":"壱","2":"弐","3":"参","4":"四",
    #                   "5":"五","6":"六","7":"七","8":"八","9":"九"}
    # keta_dict={0:"",1:"拾",2:"百",3:"千"}
    # mansin_dict={0:"",1:"万",2:"億",3:"兆"}
    
    # reverse_str_number=list(str(int(number)))#整数値からstringのリストに変換
    # reverse_str_number.reverse()#数値は逆から読む
    # result_list=[]
    
    # mansin_count=0
    # mansin_flag=False#万進の桁は1つでもあれば追加
    # for number_ind in range(len(reverse_str_number)):
    #     change_number=reverse_str_number[number_ind]#変えたい数字
    #     keta_ind=int(number_ind%4)#4桁区切りで桁を付ける
        
    #     if keta_ind==0:#区切り
    #         if mansin_flag==True:#mansinの桁が1回以上使われる
    #             result_list.insert(0,mansin_dict[mansin_count])#"","万","億","兆"の呼び出し
    #         mansin_count+=1
    #         mansin_flag=False
    #     if change_number !="0":#
    #         mansin_flag=True
    #         result_list.insert(0,keta_dict[keta_ind])#千百拾
    #         result_list.insert(0,number2kanji_dict[change_number])
    # if len(result_list)==0:#なにもないなら0
    #     result_list.insert(0,number2kanji_dict[change_number])  
    # print(list(filter(None, result_list)))
    # return result_list

def kanji2number_function(number):
    kanji2number_dict={"零":"0","壱":"1","弐":"2","参":"3","四":"4",
                      "五":"5","六":"6","七":"7","八":"8","九":"9",
                      "拾":"a","百":"b","千":"c",
                      "万":"A","億":"B","兆":"C"}
    keta_dict={"c":"拾","b":"百","a":"千"}
    mansin_dict={"":1,"万":2,"億":3,"兆":4}
    result_list=[]
    mansin_list=["兆","億","万"]
    keta_list=["","拾","百","千"]
    keman_list=["","拾","百","千",
                "万","拾","百","千",
                "億","拾","百","千",
                "兆","拾","百","千",""]
    start_mansin=""
    number_list=list(number)
    number_list.reverse()#逆から読む
    add_number_flag=kanji2number_dict[number_list[0]].isdecimal()
    keta_exp_ind=0
    mansin_exp_ind=0
    print(number_list)
    for number_kanji in number_list:
        print(f"check漢字{number_kanji}")
        print(f"now:{result_list}")
        print(f"addflag:{add_number_flag}")
        print(f"keman:{keman_list[mansin_exp_ind]}")
        dict_result=kanji2number_dict[number_kanji]
        #print(dict_result)
        if dict_result.isdecimal():#取得した値が数値
            if add_number_flag:#数値を追加すべきである。
                result_list.append(dict_result)
                mansin_exp_ind+=1
            add_number_flag=False
        else:#桁が来た
            if add_number_flag:#数字が入るはず
                if number_kanji in keta_list:
                    for _ in range(keta_list.index(number_kanji)):
                        result_list.append("0")
                    
                    #print(keta_list.index(number_kanji))
                if number_kanji in mansin_list:
                    print(number_kanji)
            else:#確かに桁が入っているがどっか飛んでないか
                
                while(keman_list[mansin_exp_ind]!=number_kanji):
                    result_list.append("0")
                    
                    mansin_exp_ind+=1
                add_number_flag=True        
        print(f"result:{result_list}")
          

    result_list.reverse()
    print(result_list)
    #int(result_list)
    return int("".join(result_list))


#http://127.0.0.1:5000/v1/number2kanji/5
@app.route("/v1/number2kanji/<number>", methods=["GET"])
def number2kanji(number):
    if number2kanji_checker(number):
        number= number2kanji_function(number)
    else:
        response = make_response('', 204)
        return response

    response = dict()
    response['result'] = number
    response_json = json.dumps(response)
    return response_json

@app.route("/v1/kanji2number/<number>", methods=["GET"])
def kanji2number(number):
    if kanji2number_checker(number):
        number= kanji2number_function(number)
    else:
        response = make_response('', 204)
        return response

    response = dict()
    response['result'] = number
    response_json = json.dumps(response)
    return response_json

@app.route('/')
def index():
    return 'Hello World'



if __name__ == 'main':
    app.debug = True
    app.run(host='127.0.0.1', port=80)