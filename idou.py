import csv
import discord
import requests

# 移動販売
IDOU_DIR_URL = "https://gh.hyouhyan.com/ait-info/idou/"

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
        print(file)
        reader = csv.reader(file)
        print(reader)

        # dayに相当する要素を検索
        for i in reader:
            print(i)
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