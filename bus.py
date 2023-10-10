import json
import discord

# バス関係のやつ
BUS_DIAGRAM = {}
BUS_ABC = {}

BUS_DIAGRAM_PATH = "./data/ait/bus_diagram-R4.json"
BUS_ABC_PATH = "./data/ait/bus_ABC-R5.json"

BUS_LAST = 21
BUS_FIRST = 8

def load():
    global BUS_DIAGRAM, BUS_ABC
    file = open(BUS_DIAGRAM_PATH, 'r')
    BUS_DIAGRAM = json.load(file)
    file.close()

    file = open(BUS_ABC_PATH, 'r')
    BUS_ABC = json.load(file)
    file.close()


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
# バス関係ここまで