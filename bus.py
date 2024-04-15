import json
import discord
import requests
import datetime

# バス関係のやつ
BUS_DIAGRAM = {}
BUS_ABC = {}

BUS_DIAGRAM_URL = "https://gh.hyouhyan.com/ait-info/bus/bus_diagram-R6.json"
BUS_ABC_URL = "https://gh.hyouhyan.com/ait-info/bus/bus_ABC-R6.json"

BUS_LAST = 21
BUS_FIRST = 8

# 日付の整合性チェック
def checkDate(year, month, day):
    try:
        newDateStr = "%04d/%02d/%02d"%(year, month, day)
        newDate = datetime.datetime.strptime(newDateStr, "%Y/%m/%d")
        return True
    except:
        return False

def load():
    global BUS_DIAGRAM, BUS_ABC
    BUS_DIAGRAM = requests.get(BUS_DIAGRAM_URL).json()
    BUS_ABC = requests.get(BUS_ABC_URL).json()


def bus_mdh(bus_m, bus_d, bus_h):
    load()
    # int型だったらstrに変換
    if(type(bus_m) is int):
        bus_m = str(bus_m)
    if(type(bus_d) is int):
        bus_d = str(bus_d)
    if(type(bus_h) is int):
        bus_h = str(bus_h)

    tume_m = bus_m
    tume_d = bus_d

    if(len(tume_m) == 1):
        tume_m = "0" + tume_m
    if(len(tume_d) == 1):
        tume_d = "0" + tume_d
    
    if(int(bus_h) < BUS_FIRST):
        embed = discord.Embed(title="エラー", description=f"バスの運行開始は{BUS_FIRST}時台です。", color=discord.Colour.red())
        return embed
    elif(int(bus_h) > BUS_LAST):
        embed = discord.Embed(title="エラー", description=f"バスの最終運行は{BUS_LAST}時台です。", color=discord.Colour.red())
        return embed

    # ABCダイヤ取得
    try:
        today_ABC = BUS_ABC[bus_m][bus_d]
        if today_ABC is None:
            embed = discord.Embed(title=f"今日は運休です", description="本日の運行はありません")
        else:
            embed = discord.Embed(title=f"{tume_m}月{tume_d}日 {today_ABC}ダイヤ {bus_h}時台")
            try:
                today_dia = BUS_DIAGRAM[today_ABC]

                # 初期化
                value = ""

                for i in today_dia["yakusa"][bus_h]:
                    i = str(i)

                    if(len(i) == 1):
                        i = "0" + i
                    if(len(bus_h) == 1):
                        i = f"0{bus_h}:{i}"
                    else:
                        i = f"{bus_h}:{i}"

                    value += f"{i}\n"
                embed.add_field(name="八草 → 愛工大", value=value)
                

                # 初期化
                value = ""

                for i in today_dia["ait"][bus_h]:
                    i = str(i)

                    if(len(i) == 1):
                        i = "0" + i
                    if(len(bus_h) == 1):
                        i = f"0{bus_h}:{i}"
                    else:
                        i = f"{bus_h}:{i}"
                    
                    value += f"{i}\n"
                embed.add_field(name="愛工大 → 八草", value=value)

                embed.set_footer(text="Powered by hyouhyan.com")

            except:
                embed = discord.Embed(title="エラー", description=f"原因不明、開発者に連絡をお願いします", color=discord.Colour.red())
                embed.add_field(name="bus_m", value = f"{bus_m} {type(bus_m)}")
                embed.add_field(name="bus_d", value = f"{bus_d} {type(bus_d)}")
                embed.add_field(name="bus_h", value = f"{bus_h} {type(bus_h)}")
                embed.add_field(name="today_ABC", value = f"{today_ABC} {type(today_ABC)}")
    except:
        embed = discord.Embed(title="エラー", description=f"{tume_m}月{tume_d}日は対応外です", color=discord.Colour.red())
    
    return embed


def bus_command(time: str = ""):
    # 日付取得
    dt_now = datetime.datetime.now()
    bus_y = (dt_now.year)
    bus_m = (dt_now.month)
    bus_d = (dt_now.day)
    bus_h = (dt_now.hour)

    if(bus_h < 8):
        bus_h = 8
    if(bus_h > 21):
        bus_h = 8
        bus_d += 1

        if(not checkDate(bus_y, bus_m, bus_d)):
            bus_d = 1
            if(bus_m == 12):
                bus_m = 1
            else:
                bus_m += 1

    if time == "":
        embed = bus_mdh(bus_m, bus_d, bus_h)
    else:
        if(time == "next" or time == "n"):
            bus_h = int(bus_h) + 1
            if(bus_h > BUS_LAST):
                bus_h = BUS_FIRST
            embed = bus_mdh(bus_m, bus_d, bus_h)
        
        elif(time.isdigit()):
            if(len(time) == 2 or len(time) == 1):
                # timeは時間帯
                # 0詰めさせないためのint変換
                bus_h = int(time)
                embed = bus_mdh(bus_m, bus_d, bus_h)
                
            elif(len(time) == 6):
                result = list(time)
                bus_m = int(result[0] + result[1])
                bus_d = int(result[2] + result[3])
                bus_h = int(result[4] + result[5])

                embed = bus_mdh(bus_m, bus_d, bus_h)

            else:
                embed = discord.Embed(title="エラー", description=f"日時の指定方法が違います。", color=discord.Colour.red())
                embed.add_field(name="記述例", value=f"12月1日20時台の場合\n`/bus 120120`\n本日20時台の場合\n`/bus 20`", inline=False)

        else:
            embed = discord.Embed(title="エラー", description=f"指定された引数「{time}」は無効です。", color=discord.Colour.red())
            
    return embed
