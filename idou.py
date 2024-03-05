import csv
import discord
import requests
import datetime

# 移動販売
IDOU_DIR_URL = "https://gh.hyouhyan.com/ait-info/idou/"

# 日付の整合性チェック
def checkDate(year, month, day):
    try:
        newDateStr = "%04d/%02d/%02d"%(year, month, day)
        newDate = datetime.datetime.strptime(newDateStr, "%Y/%m/%d")
        return True
    except:
        return False

def idou_ymd(year, month, day):
    
    # str型(表示用)
    tume_m = str(month)
    tume_d = str(day)

    if(len(tume_m) == 1):
        tume_m = "0" + tume_m
    if(len(tume_d) == 1):
        tume_d = "0" + tume_d
    
    try:
        # csvをリストに変換
        # エラーポイント1 オープン時のエラー
        # URLから取得
        file = requests.get(f"{IDOU_DIR_URL}{year}{tume_m}.csv").text.splitlines()
        # print(file)
        reader = csv.reader(file)
        # print(reader)

        # dayに相当する要素を検索
        for i in reader:
            # print(i)
            if(i[0] == str(day)):
                schedule = i
                break
        
        # エラーポイント2 該当曜日がなかった場合 schedule == None のためエラー
        embed = discord.Embed(title=f"{tume_m}月{tume_d}日 ({schedule[1]}) 移動販売スケジュール")
    
    except:
        embed = discord.Embed(title="エラー", description=f"該当データが存在しません", color=discord.Colour.red())
        embed.add_field(name="year", value = f"{year} {type(year)}")
        embed.add_field(name="month", value = f"{month} {type(month)}")
        embed.add_field(name="day", value = f"{day} {type(day)}")
        return embed
    
    else:
        spEmoji = ""
        # 1号館前
        ichigo = schedule[2]
        
        if(ichigo == ""):
            ichigo = "なし"
        
        if("ベイサデ" in ichigo):
            ichigo = "ベイザデケバブ"
        
        # セントラル
        central = schedule[3]
        
        if(central == ""):
            central = "なし"
        
        if("ベイサデ" in central):
            central = "ベイザデケバブ"
        

        # 自由が丘
        # value = schedule[4]

        # if(value != ""):
        #     embed.add_field(name="自由が丘", value=value)
        #     jiyugaoka = value

        # spEmoji
        if("ベイザデケバブ" in central or "ベイザデケバブ" in ichigo):
            spEmoji = "🥙"
        elif("178" in central or "178" in ichigo):
            spEmoji = "🍗"
        
        embed = discord.Embed(title=f"{spEmoji} {tume_m}月{tume_d}日 ({schedule[1]}) 移動販売スケジュール {spEmoji}")
        embed.add_field(name="1号館前", value=ichigo)
        embed.add_field(name="セントラル", value=central)
        

        embed.set_footer(text="Powered by hyouhyan.com")

        return embed


def idou_command(date: str = ""):
    # 日付取得
    dt_now = datetime.datetime.now()
    idou_y = (dt_now.year)
    idou_m = (dt_now.month)
    idou_d = (dt_now.day)

    if date == "":
        embed = idou_ymd(idou_y, idou_m, idou_d)
    
    elif(date == "next" or date == "n"):
        # 翌日
        idou_d += 1

        # 翌日が存在しない日だった場合
        if(not checkDate(idou_y, idou_m, idou_d)):
            idou_d = 1
            # さらに年末だった場合
            if(idou_m == 12):
                idou_m = 1
                idou_y += 1
            else:
                idou_m += 1
        
        embed = idou_ymd(idou_y, idou_m, idou_d)
    
    elif(date.isdigit()):
        if(len(date) == 2 or len(date) == 1):
            # 0詰めさせないためのint変換
            idou_d = int(date)
            embed = idou_ymd(idou_y, idou_m, idou_d)

        elif(len(date) == 4):
            result = list(date)
            idou_m = int(result[0] + result[1])
            idou_d = int(result[2] + result[3])
            embed = idou_ymd(idou_y, idou_m, idou_d)
        
        elif(len(date) == 8):
            result = list(date)
            idou_y = int(result[0] + result[1] + result[2] + result[3])
            idou_m = int(result[4] + result[5])
            idou_d = int(result[6] + result[7])
            embed = idou_ymd(idou_y, idou_m, idou_d)

        else:
            embed = discord.Embed(title="エラー", description=f"日時の指定方法が違います。", color=discord.Colour.red())
            embed.add_field(name="記述例", value=f"今月20日の場合\n`/idou 20`\n12月1日の場合\n`/idou 1201`\n2022年1月12日の場合\n`/idou 20220112`", inline=False)
            
            
    return embed
