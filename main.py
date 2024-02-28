import discord
from discord import app_commands
import json
import datetime
import re
import requests
import os
import qrcode

# Local
import bus
import idou
import qrMaker

intents = discord.Intents.all()

client = discord.Client(intents = intents)

commandTree = app_commands.CommandTree(client)

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
        commandTree.clear_commands(guild = discord.Object(id = int(i)))
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
    await commandTree.sync()

@client.event
async def on_message(message):
    global GLOBAL_SETTINGS, LOCAL_SETTINGS, GUILDS, USERS

    # botからのメッセージは無視する
    if message.author.bot:
        return

    print(f"{message.channel.id} {message.channel}メッセージ検知")
    print(f"\t{message.content}")
    
    if message.content in ["idou", "bus", "==idou", "==bus"]:
        await message.channel.send("該当コマンドはスラッシュコマンドに移行しました。`/help`で確認してください。")

    # オーナーのDMの場合
    if (message.guild is None) and (message.author.id in USERS["OWNER"]):
        content = message.content
        # メッセージが4桁の数字の場合
        if (content.isdigit()) and (len(content) == 4):
            nowTime = datetime.datetime.now()
            print("4桁の数字を検知")
            print(nowTime.hour)
            
            if(nowTime.hour >= 20 and nowTime.hour <= 21):
                endTime = dakoku(content)
                await message.channel.send(f"{datetime.datetime.now.strftime('%m月%d日')}の終業時刻を`{int(endTime / 100)}時{endTime % 100}分`として記録しました")


def dakoku(endTime):
    endTime = int(endTime)          
    r = requests.get(f"{SalaryURL}?hours={int(endTime / 100)}&minutes={endTime % 100}")
    print(f"打刻しました。${endTime}")

    return endTime

def is_owner(user):
    return user.id in USERS["OWNER"]

def is_mod(user):
    return user.id in USERS["MOD"] or is_owner(user)

@commandTree.command(name="dkk", description="退勤時間を打刻します。(オーナー様専用)")
async def dkk_command(interaction: discord.Interaction, time: int):
    if(is_owner(interaction.user)):
        endTime = dakoku(time)
        await interaction.response.send_message(f"{datetime.datetime.now.strftime('%m月%d日')}の終業時刻を`{int(endTime / 100)}時{endTime % 100}分`として記録しました")
    else:
        await interaction.response.send_message("オーナー様ではありません")

@commandTree.command(name="shutdown", description="Botをシャットダウンします。(オーナー様専用)")
async def shutdown_command(interaction: discord.Interaction):
    if(is_owner(interaction.user)):
        save_all()
        await interaction.response.send_message("シャットダウンします")
        await client.change_presence(activity=discord.Game(name=f"シャットダウン中"), status=discord.Status.dnd)
        await client.close()
        exit()
    else:
        await interaction.response.send_message("オーナー様ではありません")

@commandTree.command(name="invite", description="Botの招待リンクを表示します(モデレーター以上)")
async def invite_command(interaction: discord.Interaction):
    if(is_mod(interaction.user)):
        await interaction.response.send_message("https://discord.com/api/oauth2/authorize?client_id=991156508781969438&permissions=8&scope=bot%20applications.commands", ephemeral=True)
    else:
        await interaction.response.send_message("権限がありません", ephemeral=True)

@commandTree.command(name="suteme", description="Botのステータスを変更します(モデレーター以上)")
@app_commands.describe(status="変更するステータス")
async def suteme_command(interaction: discord.Interaction, status: str):
    if(is_mod(interaction.user)):
        GLOBAL_SETTINGS["PLAYING"] = status
        await client.change_presence(activity = discord.Activity(name=str(GLOBAL_SETTINGS["PLAYING"]), type=discord.ActivityType.playing))
        await interaction.response.send_message(f'ステータスを`{GLOBAL_SETTINGS["PLAYING"]}`に変更しました')
        save.global_settings()
    else:
        await interaction.response.send_message("権限がありません")

@commandTree.command(name="send", description="指定したチャンネルにメッセージを送信します(モデレーター以上)")
@app_commands.describe(channel="送信するチャンネルのID", content="送信する内容")
async def send_command(interaction: discord.Interaction, channel: str, content: str):
    channel = int(channel)
    if(is_mod(interaction.user)):
        botRoom = client.get_channel(channel)
        await botRoom.send(content)
        await interaction.response.send_message(f'<#{channel}>に送信しました。以下送信内容\n`{content}`')
    else:
        await interaction.response.send_message("権限がありません")


@commandTree.command(name="qr", description="QRコードを生成します")
async def qr_command(interaction: discord.Interaction, content: str, logo:discord.Attachment = None):
    QR_TEMP_PATH = "./temp/qr.png"
    QR_LOGO_TEMP_PATH = "./temp/qr-logo.png"
    if logo:
        file = logo
        await file.save(QR_LOGO_TEMP_PATH)
        qrMaker.encode_qr_with_logo(content, QR_LOGO_TEMP_PATH, QR_TEMP_PATH)
        os.remove(QR_LOGO_TEMP_PATH)
    else:
        img = qrcode.make(content)
        img.save(QR_TEMP_PATH)
    await interaction.response.send_message(content=content, file=discord.File(QR_TEMP_PATH))
    os.remove(QR_TEMP_PATH)


@commandTree.command(name="bus", description="バスの時刻表を表示します")
@app_commands.describe(time="バスの時間帯を指定(数字2桁 or 6桁, nで次の時間帯)")
async def bus_command(interaction: discord.Interaction, time: str = ""):
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
        embed = bus.bus_mdh(bus_m, bus_d, bus_h)
    else:
        if(time == "next" or time == "n"):
            bus_h = int(bus_h) + 1
            if(bus_h > bus.BUS_LAST):
                bus_h = bus.BUS_FIRST
            embed = bus.bus_mdh(bus_m, bus_d, bus_h)
        
        elif(time.isdigit()):
            if(len(time) == 2 or len(time) == 1):
                # timeは時間帯
                # 0詰めさせないためのint変換
                bus_h = int(time)
                embed = bus.bus_mdh(bus_m, bus_d, bus_h)
                
            elif(len(time) == 6):
                result = list(time)
                bus_m = int(result[0] + result[1])
                bus_d = int(result[2] + result[3])
                bus_h = int(result[4] + result[5])

                embed = bus.bus_mdh(bus_m, bus_d, bus_h)

            else:
                embed = discord.Embed(title="エラー", description=f"日時の指定方法が違います。", color=discord.Colour.red())
                embed.add_field(name="記述例", value=f"12月1日20時台の場合\n`bus 120120`\n本日20時台の場合\n`bus 20`", inline=False)

        else:
            embed = discord.Embed(title="エラー", description=f"指定された引数「{time}」は無効です。", color=discord.Colour.red())
            
    await interaction.response.send_message(embed=embed)


@commandTree.command(name="idou", description="移動販売のスケジュールを表示します")
@app_commands.describe(date="日付を指定(数字2桁 or 4桁 or 8桁, nで翌日)")
async def idou_command(interaction: discord.Interaction, date: str = ""):
    # 日付取得
    dt_now = datetime.datetime.now()
    idou_y = (dt_now.year)
    idou_m = (dt_now.month)
    idou_d = (dt_now.day)

    if date == "":
        embed = idou.idou_ymd(idou_y, idou_m, idou_d)
    
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
        
        embed = idou.idou_ymd(idou_y, idou_m, idou_d)
    
    elif(date.isdigit()):
        if(len(date) == 2 or len(date) == 1):
            # 0詰めさせないためのint変換
            idou_d = int(date)
            embed = idou.idou_ymd(idou_y, idou_m, idou_d)

        elif(len(date) == 4):
            result = list(date)
            idou_m = int(result[0] + result[1])
            idou_d = int(result[2] + result[3])
            embed = idou.idou_ymd(idou_y, idou_m, idou_d)
        
        elif(len(date) == 8):
            result = list(date)
            idou_y = int(result[0] + result[1] + result[2] + result[3])
            idou_m = int(result[4] + result[5])
            idou_d = int(result[6] + result[7])
            embed = idou.idou_ymd(idou_y, idou_m, idou_d)

        else:
            embed = discord.Embed(title="エラー", description=f"日時の指定方法が違います。", color=discord.Colour.red())
            embed.add_field(name="記述例", value=f"今月20日の場合\n`{LOCAL_SETTINGS[str(interaction.guild_id)]['PREFIX']}idou 20`\n12月1日の場合\n`{LOCAL_SETTINGS[str(interaction.guild_id)]['PREFIX']}idou 1201`\n2022年1月12日の場合\n`{LOCAL_SETTINGS[str(interaction.guild_id)]['PREFIX']}idou 20220112`", inline=False)
            
            
    await interaction.response.send_message(embed=embed)


@commandTree.command(name="ping", description="Ping値を表示します")
async def ping_command(interaction: discord.Interaction):
    # Ping値を秒単位で取得
    raw_ping = client.latency

    # ミリ秒に変換して丸める
    ping = round(raw_ping * 1000)

    # 送信する
    await interaction.response.send_message(f"Latency: {ping}ms", ephemeral=True)
    
    
@commandTree.command(name="help", description="ヘルプを表示します")
async def help_command(interaction: discord.Interaction):
    file = open(HELP_PATH, 'r')
    data = file.read()
    file.close()
    await interaction.response.send_message(data, ephemeral=True)


@commandTree.command(name="whoami", description="自分の情報を表示します")
async def whoami_command(interaction: discord.Interaction):
    user = interaction.user
    embed = discord.Embed(title="あなたの情報", color=discord.Colour.blue())
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="名前", value=user.name, inline=False)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="is_owner", value=is_owner(user), inline=False)
    embed.add_field(name="is_mod", value=is_mod(user), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

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