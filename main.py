import discord
import json
import datetime
import re
import requests
import os
import qrcode

import bus
import idou
import qrMaker

intents = discord.Intents.all()

client = discord.Client(intents = intents)

# URLパターン
url_pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

# 給料のURL from gas
SalaryURL = "https://script.google.com/macros/s/AKfycbzmEvS_ty_6vMTHSeEVbVry9Xhj4AlOO6xZlnOCooxjzR85rCDfCLemiqifTY2TTXZh/exec"

# グローバル(全部共通の)設定
GLOBAL_SETTINGS_PATH = "./data/global_settings.json"
GLOBAL_SETTINGS = {
    "TOKEN": "",
    "PLAYING":"人生"
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
    global GLOBAL_SETTINGS, LOCAL_SETTINGS, USERS

    file = open(GLOBAL_SETTINGS_PATH, 'r')
    GLOBAL_SETTINGS = json.load(file)
    file.close()

    file = open(LOCAL_SETTINGS_PATH, 'r')
    LOCAL_SETTINGS = json.load(file)
    file.close()

    file = open(USERS_PATH, 'r')
    USERS = json.load(file)
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

# ここから本編
load()

@client.event
async def on_ready():
    print("ログイン成功")
    update_guilds()
    initialize()
    await client.change_presence(activity = discord.Activity(name=str(GLOBAL_SETTINGS["PLAYING"]), type=discord.ActivityType.playing))

@client.event
async def on_message(message):
    global GLOBAL_SETTINGS, LOCAL_SETTINGS, GUILDS, USERS

    # botからのメッセージは無視する
    if message.author.bot:
        return

    print(f"{message.channel.id} {message.channel}メッセージ検知")
    print(f"\t{message.content}")

    # logRoom = client.get_channel(1035225346431275138)
    # embed = discord.Embed(title = message.content)
    # try:
    #     embed.add_field(name = "送信先", value = f"{message.guild.name} {message.channel.name}")
    # except:
    #     embed.add_field(name = "送信先", value = f"DM")
    # embed.set_author(name = message.author.name,icon_url = message.author.avatar.url)
    # embed.set_footer(text = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
    # await logRoom.send(embed = embed)
    
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
                await client.close()
                exit()
            
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
                    embed = bus.bus_mdh(bus_m, bus_d, bus_h)
                else:
                    if(content == "next" or content == "n"):
                        bus_h = int(bus_h) + 1
                        if(bus_h > bus.BUS_LAST):
                            bus_h = bus.BUS_FIRST
                        embed = bus.bus_mdh(bus_m, bus_d, bus_h)
                    
                    elif(content.isdigit()):
                        if(len(content) == 2 or len(content) == 1):
                            # contentは時間帯
                            # 0詰めさせないためのint変換
                            bus_h = int(content)
                            embed = bus.bus_mdh(bus_m, bus_d, bus_h)
                            
                        elif(len(content) == 6):
                            result = list(content)
                            bus_m = int(result[0] + result[1])
                            bus_d = int(result[2] + result[3])
                            bus_h = int(result[4] + result[5])

                            embed = bus.bus_mdh(bus_m, bus_d, bus_h)

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
                    embed = idou.idou_ymd(idou_y, idou_m, idou_d)
            
                elif(content == "next" or content == "n"):
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
                    
                    embed = idou.idou_ymd(idou_y, idou_m, idou_d)
                
                elif(content.isdigit()):
                    if(len(content) == 2 or len(content) == 1):
                        # 0詰めさせないためのint変換
                        idou_d = int(content)
                        embed = idou.idou_ymd(idou_y, idou_m, idou_d)

                    elif(len(content) == 4):
                        result = list(content)
                        idou_m = int(result[0] + result[1])
                        idou_d = int(result[2] + result[3])
                        embed = idou.idou_ymd(idou_y, idou_m, idou_d)
                    
                    elif(len(content) == 8):
                        result = list(content)
                        idou_y = int(result[0] + result[1] + result[2] + result[3])
                        idou_m = int(result[4] + result[5])
                        idou_d = int(result[6] + result[7])
                        embed = idou.idou_ymd(idou_y, idou_m, idou_d)

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
            
            # QRコード
            if content.startswith("qr"):
                QR_TEMP_PATH = "./temp/qr.png"
                QR_LOGO_TEMP_PATH = "./temp/qr-logo.png"
                content = rmprefix(content, "qr")
                if message.attachments:
                    file = message.attachments[0]
                    await file.save(QR_LOGO_TEMP_PATH)
                    qrMaker.encode_qr_with_logo(content, QR_LOGO_TEMP_PATH, QR_TEMP_PATH)
                    os.remove(QR_LOGO_TEMP_PATH)
                else:
                    img = qrcode.make(content)
                    img.save(QR_TEMP_PATH)
                await message.channel.send(file=discord.File(QR_TEMP_PATH))
                os.remove(QR_TEMP_PATH)
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
            nowTime = datetime.datetime.now()
            print("4桁の数字を検知")
            print(nowTime.hour)
            
            if(nowTime.hour >= 20 and nowTime.hour <= 21):
                endTime = dakoku(content)
                await message.channel.send(f"終業時刻を`{int(endTime / 100)}時{endTime % 100}分`として記録しました")
                
        if content.startswith("dkk"):
            print("dakoku")
            content = rmprefix(content, "dkk")
            if (content.isdigit()) and (len(content) == 4):
                endTime = dakoku(content)
                await message.channel.send(f"終業時刻を`{int(endTime / 100)}時{endTime % 100}分`として記録しました")
            else:
                await message.channel.send(f"なんか変です。時刻の指定間違ってませんか？")
            
def dakoku(endTime):
    endTime = int(endTime)          
    r = requests.get(f"{SalaryURL}?hours={int(endTime / 100)}&minutes={endTime % 100}")
    print(f"打刻しました。${endTime}")

    return endTime

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