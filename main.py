import discord
import json
import datetime
import simplenote
import re
import requests
import os
import qrcode
import csv

intents = discord.Intents.all()

client = discord.Client(intents = intents)

# URLパターン
url_pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

# 給料のURL from gas
# SalaryURL = "https://script.google.com/macros/s/AKfycbxLTAbpLHqmmUOBv98STGoYTAHzubswlqq6tqKfVlrs1tx22rl6YHCIOF6GweVmv39ibA/exec"

# グローバル(全部共通の)設定
GLOBAL_SETTINGS_PATH = "./data/global_settings.json"
GLOBAL_SETTINGS = {
    "TOKEN": "OTkxMTU2NTA4NzgxOTY5NDM4.G2V5Wo.lgUAo5LU6rJS1mgXKHhIAvvl_-aKA8QuPyBb64",
    "PLAYING":"人生",
    "SN":{
        "USER":"",
        "PASS":""
    }
}

# ローカル(サーバーごとの)設定
LOCAL_SETTINGS_PATH = "./data/local_settings.json"
LOCAL_SETTINGS = {
    "":{
        "PREFIX":"=="
    }
}

# ユーザー情報
USERS_PATH = "./data/users.json"
USERS = {
    "OWNER":[349369324244434955],
    "MOD":[]
}

HELP_PATH = "./data/help.txt"
HELPALL_PATH = "./data/help_other.txt"

# 参加してるサーバー一覧
GUILDS_PATH = "./data/guilds.json"
GUILDS = {}

# メモ関係のやつ
memo_flg = False
memo_value = ""


# バス関係のやつ
BUS_DIAGRAM = {}
BUS_ABC = {}

BUS_DIAGRAM_PATH = "./data/ait/bus_diagram-R4.json"
BUS_ABC_PATH = "./data/ait/bus_ABC-R4.json"

BUS_LAST = 21
BUS_FIRST = 8

def bus_mdh(bus_m, bus_d, bus_h):
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

# 移動販売
IDOU_DIR_PATH = "./data/ait/idou/"
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
        file = open(f"{IDOU_DIR_PATH}{year}{tume_m}.csv")
        reader = csv.reader(file)

        # dayに相当する要素を検索
        for i in reader:
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


# 日付の整合性チェック
def checkDate(year, month, day):
    try:
        newDateStr = "%04d/%02d/%02d"%(year, month, day)
        newDate = datetime.datetime.strptime(newDateStr, "%Y/%m/%d")
        return True
    except:
        return False

#jsonファイルへの書き出し
class save:
    def global_settings():
        file = open(GLOBAL_SETTINGS_PATH, 'w')
        json.dump(GLOBAL_SETTINGS, file)
        file.close()

    def local_settings():
        file = open(LOCAL_SETTINGS_PATH, 'w')
        json.dump(LOCAL_SETTINGS, file)
        file.close()

    def users():
        file = open(USERS_PATH, 'w')
        json.dump(USERS, file)
        file.close()

    def guilds():
        file = open(GUILDS_PATH, 'w')
        json.dump(GUILDS, file)
        file.close()

def save_all():
    save.global_settings()
    save.local_settings()
    save.users()
    save.guilds()

#jsonファイルの読み込み
def load():
    global GLOBAL_SETTINGS, BUS_DIAGRAM, BUS_ABC, LOCAL_SETTINGS, USERS, TIMETABLE_ID_NAME

    file = open(GLOBAL_SETTINGS_PATH, 'r')
    GLOBAL_SETTINGS = json.load(file)
    file.close()

    file = open(LOCAL_SETTINGS_PATH, 'r')
    LOCAL_SETTINGS = json.load(file)
    file.close()

    file = open(USERS_PATH, 'r')
    USERS = json.load(file)
    file.close()

    file = open(BUS_DIAGRAM_PATH, 'r')
    BUS_DIAGRAM = json.load(file)
    file.close()

    file = open(BUS_ABC_PATH, 'r')
    BUS_ABC = json.load(file)
    file.close()

    file = open(f"{TIMETABLE_DIR}id_name.json", 'r')
    TIMETABLE_ID_NAME = json.load(file)
    file.close()
    

#removeprefixのやつ
def rmprefix(content, prefix):
    content = content.removeprefix(prefix)
    content = content.removeprefix(' ')
    return content

#初参加サーバーに初期設定を適用
def initialize():
    global LOCAL_SETTINGS
    for i in GUILDS:
        if not i in LOCAL_SETTINGS:
            LOCAL_SETTINGS[i] = {}
            LOCAL_SETTINGS[i]["PREFIX"] = "=="
    print("初期化完了")
    save.local_settings()
    save.guilds()

#サーバー辞書のアップデート
def update_guilds():
    global GUILDS
    for guilds in client.guilds:
        GUILDS[str(guilds.id)] = guilds.name
    save.guilds()
    print("サーバー辞書更新")


# 時間割
TIMETABLE_DIR = "./data/ait/timetable/"
TIMETABLE_ID_NAME = {}

def timetable(name):
    dt_now = datetime.datetime.now()

    if os.path.exists(f"{TIMETABLE_DIR}{name}.json"):
        embed = discord.Embed(title="本日の時間割")
        file = open(f"{TIMETABLE_DIR}{name}.json", 'r')
        reader = json.load(file)
        file.close()

        if reader[dt_now.strftime('%a')] is None:
            embed = discord.Embed(title="本日の予定", description=f"今日は全休です")
        else:
            for i in range(1, 5):
                try:
                    reader[dt_now.strftime('%a')][str(i)]
                except:
                    value = "なし"
                    title = ""
                else:
                    title = reader[dt_now.strftime('%a')][str(i)]['title']
                    value = f"{reader[dt_now.strftime('%a')][str(i)]['teacher']}\n{reader[dt_now.strftime('%a')][str(i)]['room']}"
                
                embed.add_field(name=f"{i}限 {title}", value=value, inline=False)

    else:
        embed = discord.Embed(title="エラー", description=f"該当ユーザー`{name}`の時間割はありません", color=discord.Color.red())
    
    return embed

# morning
def morning(name):
    dt_now = datetime.datetime.now()

    embed = discord.Embed(title="おはようございます")

    # 時間割
    if os.path.exists(f"{TIMETABLE_DIR}{name}.json"):
        file = open(f"{TIMETABLE_DIR}{name}.json", 'r')
        reader = json.load(file)
        file.close()

        if reader[dt_now.strftime('%a')] is None:
            Value = "本日は全休です"
        else:
            for i in range(1, 5):
                value += f"{i}限 "
                try:
                    reader[dt_now.strftime('%a')][str(i)]
                except:
                    value += "なし"
                else:
                    value += reader[dt_now.strftime('%a')][str(i)]['title']
                    value += f"({reader[dt_now.strftime('%a')][str(i)]['room']})"
                
                value += "\n"

        embed.add_field(name=f"時間割", value=value)

    else:
        embed = discord.Embed(title="エラー", description=f"該当ユーザー`{name}`の時間割はありません", color=discord.Color.red())
    
    return embed

# ここから本編
load()

# Simplenote用意
sn = simplenote.Simplenote(GLOBAL_SETTINGS["SN"]["USER"], GLOBAL_SETTINGS["SN"]["PASS"])

@client.event
async def on_ready():
    print("ログイン成功")
    update_guilds()
    initialize()
    await client.change_presence(activity = discord.Activity(name=str(GLOBAL_SETTINGS["PLAYING"]), type=discord.ActivityType.playing))

@client.event
async def on_message(message):
    global GLOBAL_SETTINGS, LOCAL_SETTINGS, GUILDS, USERS, memo_flg, memo_value

    # botからのメッセージは無視する
    if message.author.bot:
        return

    print(f"{message.channel.id} {message.channel}メッセージ検知")
    print(f"\t{message.content}")

    logRoom = client.get_channel(1035225346431275138)
    embed = discord.Embed(title = message.content)
    try:
        embed.add_field(name = "送信先", value = f"{message.guild.name} {message.channel.name}")
    except:
        embed.add_field(name = "送信先", value = f"DM")
    embed.set_author(name = message.author.name,icon_url = message.author.avatar.url)
    embed.set_footer(text = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
    await logRoom.send(embed = embed)
    
    # ユーザーレベルの特定
    if message.author.id in USERS["OWNER"]:
        userLevel = 10
    elif message.author.id in USERS["MOD"]:
        userLevel = 9
    else:
        userLevel = 0
    
    # もしDMだったら
    if message.guild is None:
        # チャンネルIDをギルドIDとして扱う
        guild_id = message.channel.id
        if str(guild_id) not in GUILDS:
            GUILDS[str(message.channel.id)] = f"DM with {message.author.id}"
            initialize()
        # サーバー管理者限定コマンドを使えるようにする
        if(userLevel < 5):
            userLevel = 5
    else:
        guild_id = message.guild.id
    
    
    content = message.content

    if memo_flg and userLevel >= 10:
        if content == f"{LOCAL_SETTINGS[str(guild_id)]['PREFIX']}end":
            sn.add_note(memo_value)
            await message.channel.send(f'記録終了、保存しました')
            # 後片付け
            memo_flg = False
            memo_value = ""
            return
        elif content == f"{LOCAL_SETTINGS[str(guild_id)]['PREFIX']}n":
            memo_value += '\n'
            await message.channel.send('改行しました')
            return
        else:
            memo_value += (content + '\n')
            return

    # prefixで始まってたら
    if content.startswith(LOCAL_SETTINGS[str(guild_id)]["PREFIX"]):
        content = rmprefix(content, LOCAL_SETTINGS[str(guild_id)]["PREFIX"])

        if content == '':
            if userLevel >= 10:
                await message.channel.send("ようこそ、オーナー様。")
            elif userLevel >= 9:
                await message.channel.send("ようこそ、モデレーター様。")
            elif userLevel >= 5:
                await message.channel.send("ようこそ、サーバー管理者様。")
            else:
                await message.channel.send("オーナー様ではありませんね、お帰りください。")
        
        # モデレーター追加
        if content.startswith("useradd"):
            content = rmprefix(content, "useradd")
            if userLevel >= 10:
                if content.startswith("owner"):
                    content = rmprefix(content, "owner")
                    if(content == "" or not content.isdigit()):
                        await message.channel.send('オーナーにするユーザーのIDを入力してください')
                    else:
                        user_id = int(content)
                        user = await client.fetch_user(user_id)
                    
                        if(user is None):
                            await message.channel.send(f'ユーザーは存在しません')
                        elif(user_id in USERS["OWNER"]):
                            await message.channel.send(f'下記ユーザーはすでにオーナーです\n`{user.name} ID:{user_id}`')
                        else:
                            USERS["OWNER"].append(user_id)
                            await message.channel.send(f'下記ユーザーをオーナーに追加しました\n`{user.name} ID:{user_id}`')
                            save.users()

            if userLevel >= 9:
                if content.startswith("mod"):
                    content = rmprefix(content, "mod")
                    if(content == "" or not content.isdigit()):
                        await message.channel.send('モデレーターにするユーザーのIDを入力してください')
                    else:
                        user_id = int(content)
                        user = await client.fetch_user(user_id)
                    
                        if(user is None):
                            await message.channel.send(f'ユーザーは存在しません')
                        elif(user_id in USERS["MOD"]):
                            await message.channel.send(f'下記ユーザーはすでにモデレーターです\n`{user.name} ID:{user_id}`')
                        else:
                            USERS["MOD"].append(user_id)
                            await message.channel.send(f'下記ユーザーをモデレーターに追加しました\n`{user.name} ID:{user_id}`')
                            save.users()
        
        # モデレーター削除
        if content.startswith("userdel"):
            content = rmprefix(content, "userdel")
            if userLevel >= 10:
                if content.startswith("owner"):
                    content = rmprefix(content, "owner")
                    if(content == "" or not content.isdigit()):
                        await message.channel.send('削除するユーザーのIDを入力してください')
                    else:
                        user_id = int(content)
                        user = await client.fetch_user(user_id)

                        if(user is None):
                            await message.channel.send(f'ユーザーは存在しません')
                        elif(not user_id in USERS["OWNER"]):
                            await message.channel.send(f'下記ユーザーはオーナーではありません\n`{user.name} ID:{user_id}`')
                        else:
                            USERS["OWNER"].remove(user_id)
                            await message.channel.send(f'下記ユーザーを削除しました\n`{user.name} ID:{user_id}`')
                        save.users()

            if userLevel >= 9:
                if content.startswith("mod"):
                    content = rmprefix(content, "mod")
                    if(content == "" or not content.isdigit()):
                        await message.channel.send('削除するユーザーのIDを入力してください')
                    else:
                        user_id = int(content)
                        user = await client.fetch_user(user_id)

                        if(user is None):
                            await message.channel.send(f'ユーザーは存在しません')
                        elif(not user_id in USERS["MOD"]):
                            await message.channel.send(f'下記ユーザーはモデレーターではありません\n`{user.name} ID:{user_id}`')
                        else:
                            USERS["MOD"].remove(user_id)
                            await message.channel.send(f'下記ユーザーを削除しました\n`{user.name} ID:{user_id}`')
                        save.users()

        
        if userLevel >= 10:
            #オーナー限定コマンド
            if content.startswith("shutdown"):
                await message.channel.send("シャットダウンしています")
                save_all()
                await client.change_presence(activity=discord.Game(name=f"シャットダウン中"), status=discord.Status.offline)
                exit()
            
            if content.startswith("memo"):
                content = rmprefix(content, "memo")

                # memo_flgをTrueにする
                memo_flg = True

                await message.channel.send(f'記録開始。`{LOCAL_SETTINGS[str(guild_id)]["PREFIX"]}end`で終了')
                # 一応初期化
                memo_value = ''
            
            if content.startswith("pocket"):
                content = rmprefix(content, "pocket")
                if re.match(url_pattern, content):
                    payload = {'consumer_key':GLOBAL_SETTINGS["POCKET"]["consumer_key"],'access_token':GLOBAL_SETTINGS["POCKET"]["access_token"],'url':content}
                    r = requests.post('https://getpocket.com/v3/add', data = payload)
                    await message.channel.send(f"`{content}`をpocketに追加しました")
                else:
                    await message.channel.send(f'URLを引数として渡してください。\n例) `{LOCAL_SETTINGS[str(guild_id)]["PREFIX"]}pocket https://hyouhyan.com`')
            
            # if content.startswith("salary"):
            #     content = rmprefix(content, "salary")
            #     if(content == ""):
            #         r = requests.get(SalaryURL)
            #         await message.channel.send(f"今月の給料 {r}円")
            #     else:
            #         content = content.split(' ')
            #         r = requests.get(f"{SalaryURL}?year={content[0]}&month={int(content[1]) + 1}")
            #         await message.channel.send(f"{content[0]}年{content[1]}月の給料 {r}円")
                
            

        if userLevel >= 9:
            #モデレーター限定コマンド
            #招待リンク
            if content.startswith("invite"):
                await message.channel.send("https://discord.com/api/oauth2/authorize?client_id=991156508781969438&permissions=8&scope=bot%20applications.commands")
            
            #ステータス変更
            if content.startswith('suteme'):
                content = rmprefix(content, "suteme")
                GLOBAL_SETTINGS["PLAYING"] = content
                await client.change_presence(activity = discord.Activity(name=str(GLOBAL_SETTINGS["PLAYING"]), type=discord.ActivityType.playing))
                await message.channel.send(f'ステータスを`{GLOBAL_SETTINGS["PLAYING"]}`に変更しました')
                save.global_settings()
                return
            
            #メッセージ送信
            if content.startswith("send"):
                content = rmprefix(content, "send")
                if content == '':
                    await message.channel.send(f'{LOCAL_SETTINGS[str(guild_id)]["PREFIX"]} send `id` `送信する内容`')
                    return

                content = content.split(' ')
                id = int(content[0])
                content.pop(0)

                botRoom = client.get_channel(id)
                for i in content:
                    new_content = i + ' '

                await botRoom.send(new_content)
                await message.channel.send(f'<#{id}>に送信しました。以下送信内容\n`{new_content}`')
                return
        

        if userLevel >= 5:
            #サーバー内での管理者
            #prefix変更
            if content.startswith("prefix"):
                content = rmprefix(content, "prefix")
                if content == '':
                    LOCAL_SETTINGS[str(guild_id)]["PREFIX"] = ""
                    await message.channel.send(f'接頭語をなくしました')
                    save.local_settings()
                    return
                LOCAL_SETTINGS[str(guild_id)]["PREFIX"] = content
                await message.channel.send(f'接頭語を{LOCAL_SETTINGS[str(guild_id)]["PREFIX"]}に変更しました')
                save.local_settings()
                return
                

        if userLevel >= 0:
            #だれでもいけるコマンド
            if content.startswith("yummy"):
                await message.channel.send('美味しいヤミー❗️✨🤟😁👍✨⚡️感謝❗️🙌✨感謝❗️🙌✨またいっぱい食べたいな❗️🥓🥩🍗🍖😋🍴✨デリシャッ‼️🙏✨ｼｬ‼️🙏✨ ｼｬ‼️🙏✨ ｼｬ‼️🙏✨ ｼｬ‼️🙏✨ ｼｬ‼️🙏✨ ｼｬｯｯ‼😁🙏✨ハッピー🌟スマイル❗️❗️💥✨👉😁👈⭐️')
                return
            
            if content.startswith("shanks"):
                await message.channel.send('美味しいヤミー❗️✨🤟😁👍✨⚡️感謝❗️🙌✨感謝❗️🙌✨またいっぱい食べたいな❗️🥓🥩🍗🍖😋🍴✨デリシャッ‼️🙏✨ｼｬ‼️🙏✨ ｼｬ‼️🙏✨ ｼｬ‼️🙏✨ ｼｬ‼️🙏✨ ｼｬンクスが黙ってるわけねえだろ‼️いくぞ‼️めざましジャンケン、じゃんけんポン‼️✋俺はパーをだしたぞ❓😁失せろ')
                return
            
            if content.startswith("suumo"):
                await message.channel.send('あ❗️ スーモ❗️🌚ダン💥ダン💥ダン💥シャーン🎶スモ🌝スモ🌚スモ🌝スモ🌚スモ🌝スモ🌚ス〜〜〜モ⤴スモ🌚スモ🌝スモ🌚スモ🌝スモ🌚スモ🌝ス～～～モ⤵🌞')
                return
            
            if content.startswith("paku"):
                await message.channel.send('ピピーッ❗️🔔⚡️パクツイ警察です❗️👊👮❗️アナタのツイート💕は❌パクツイ禁止法❌第114514条🙋「他人の面白そうなツイートをツイート💕してゎイケナイ❗️」に違反しています😡今スグ消しなｻｲ❗️❗️❗️❗️✌️👮🔫')
                return
        
            # bus
            if content.startswith("bus"):
                content = rmprefix(content, "bus")

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

                # 日付取得ここまで
                
                if content == "":
                    embed = bus_mdh(bus_m, bus_d, bus_h)
                else:
                    if(content == "next"):
                        bus_h = int(bus_h) + 1
                        if(bus_h > BUS_LAST):
                            bus_h = BUS_FIRST
                        embed = bus_mdh(bus_m, bus_d, bus_h)
                    
                    elif(content.isdigit()):
                        if(len(content) == 2 or len(content) == 1):
                            # contentは時間帯
                            # 0詰めさせないためのint変換
                            bus_h = int(content)
                            embed = bus_mdh(bus_m, bus_d, bus_h)
                            
                        elif(len(content) == 6):
                            result = list(content)
                            bus_m = int(result[0] + result[1])
                            bus_d = int(result[2] + result[3])
                            bus_h = int(result[4] + result[5])

                            embed = bus_mdh(bus_m, bus_d, bus_h)

                        else:
                            embed = discord.Embed(title="エラー", description=f"日時の指定方法が違います。", color=discord.Colour.red())
                            embed.add_field(name="記述例", value=f"12月1日20時台の場合\n`{LOCAL_SETTINGS[str(guild_id)]['PREFIX']}bus 120120`\n本日20時台の場合\n`{LOCAL_SETTINGS[str(guild_id)]['PREFIX']}bus 20`", inline=False)

                    else:
                        embed = discord.Embed(title="エラー", description=f"指定された引数「{content}」は無効です。", color=discord.Colour.red())

                await message.channel.send(embed=embed)
            
            # 移動販売
            if content.startswith("idou"):
                content = rmprefix(content, "idou")

                # 日付取得
                dt_now = datetime.datetime.now()
                idou_y = (dt_now.year)
                idou_m = (dt_now.month)
                idou_d = (dt_now.day)

                if content == "":
                    embed = idou_ymd(idou_y, idou_m, idou_d)
            
                elif(content == "next"):
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
                
                elif(content.isdigit()):
                    if(len(content) == 2 or len(content) == 1):
                        # 0詰めさせないためのint変換
                        idou_d = int(content)
                        embed = idou_ymd(idou_y, idou_m, idou_d)

                    elif(len(content) == 4):
                        result = list(content)
                        idou_m = int(result[0] + result[1])
                        idou_d = int(result[2] + result[3])
                        embed = idou_ymd(idou_y, idou_m, idou_d)
                    
                    elif(len(content) == 8):
                        result = list(content)
                        idou_y = int(result[0] + result[1] + result[2] + result[3])
                        idou_m = int(result[4] + result[5])
                        idou_d = int(result[6] + result[7])
                        embed = idou_ymd(idou_y, idou_m, idou_d)

                    else:
                        embed = discord.Embed(title="エラー", description=f"日時の指定方法が違います。", color=discord.Colour.red())
                        embed.add_field(name="記述例", value=f"今月20日の場合\n`{LOCAL_SETTINGS[str(guild_id)]['PREFIX']}idou 20`\n12月1日の場合\n`{LOCAL_SETTINGS[str(guild_id)]['PREFIX']}idou 1201`\n2022年1月12日の場合\n`{LOCAL_SETTINGS[str(guild_id)]['PREFIX']}idou 20220112`", inline=False)
                
                await message.channel.send(embed=embed)


            # help
            if content.startswith("help"):
                content = rmprefix(content, "help")
                if(content == "all"):
                    file = open(HELPALL_PATH, 'r')
                else:
                    file = open(HELP_PATH, 'r')
                data = file.read()
                file.close()
                data = data.replace("==", LOCAL_SETTINGS[str(guild_id)]["PREFIX"])
                await message.channel.send(data)
            
            # 時間割
            if content.startswith("timetable"):
                content = rmprefix(content, "timetable")
                if content == "":
                    try:
                        await message.channel.send(embed = timetable(TIMETABLE_ID_NAME[str(message.author.id)]))
                    except:
                        await message.channel.send(embed = timetable(message.author.name))
                else:
                    await message.channel.send(embed = timetable(content))
            
            # QRコード
            if content.startswith("qr"):
                content = rmprefix(content, "qr")
                img = qrcode.make(content)
                img.save("./temp/qr.png")
                await message.channel.send(file=discord.File("./temp/qr.png"))
                os.remove("./temp/qr.png")
                return
            
            # ping
            if content == "ping":
                # Ping値を秒単位で取得
                raw_ping = client.latency

                # ミリ秒に変換して丸める
                ping = round(raw_ping * 1000)

                # 送信する
                await message.channel.send(f"Latency: {ping}ms")
                
    # オーナーのDMの場合
    if (message.guild is None) and (message.author.id in USERS["OWNER"]):
        # メッセージが4桁の数字の場合
        if (content.isdigit()) and (len(content) == 4):
            endTime = int(content)
            nowTime = datetime.datetime.now()
            
            if(nowTime.hour >= 20 & nowTime.hour <= 21):                
                r = requests.get(f"https://script.google.com/macros/s/AKfycbwbnKzSsQLFjmKoPQQ9DQSE-zOHyQTk_yw0OHTlRLKEfAoijQVpMNlNm40mGcq-G2qX/exec?hours={endTime / 100}&minutes={endTime % 100}")
                await message.channel.send(f"就業時刻を`{endTime / 100}時{endTime % 100}分`をして記録しました")

@client.event
async def on_guild_join(guild):
    print(f"サーバー{guild}に参加したよー")
    update_guilds()
    initialize()

@client.event
async def on_guild_remove(guild):
    print(f"サーバー{guild}から消されたよー")
    update_guilds()

client.run(GLOBAL_SETTINGS["TOKEN"])