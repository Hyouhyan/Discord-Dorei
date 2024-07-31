import discord
from discord import app_commands
import json
import datetime
import re
import requests
import os
import qrcode

import random

# Local
import bus
import idou
import qrMaker

intents = discord.Intents.all()

client = discord.Client(intents = intents)

commandTree = app_commands.CommandTree(client)

# URLパターン
url_pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

APPLICATION_ID = 0

# グローバル(全部共通の)設定
GLOBAL_SETTINGS_PATH = "./data/global_settings.json"
GLOBAL_SETTINGS = {
    "TOKEN": "",
    "PLAYING":"",
    "SALARY_URL": ""
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
    settings_fromfile = json.load(file)
    for key in settings_fromfile:
        if GLOBAL_SETTINGS.get(key) != None: GLOBAL_SETTINGS[key] = settings_fromfile[key]
        else: print(f"存在しないキー{key}を読み込みました at global_settings.json")
    file.close()

    file = open(LOCAL_SETTINGS_PATH, 'r')
    LOCAL_SETTINGS = json.load(file)
    file.close()

    file = open(USERS_PATH, 'r')
    settings_fromfile = json.load(file)
    for key in settings_fromfile:
        if USERS.get(key) != None: USERS[key] = settings_fromfile[key]
        else: print(f"存在しないキー{key}を読み込みました at users.json")
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
    await client.change_presence(activity=discord.CustomActivity(name=str(GLOBAL_SETTINGS["PLAYING"])))
    await commandTree.sync()
    
    global APPLICATION_ID
    APPLICATION_ID = client.application_id

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
                await message.channel.send(dakoku(content))


def dakoku(endTime):
    endTime = int(endTime)
    rtn = ""
    if (GLOBAL_SETTINGS["SALARY_URL"] != ""):
        r = requests.get(f"{GLOBAL_SETTINGS['SALARY_URL']}?hours={int(endTime / 100)}&minutes={endTime % 100}")
        print(f"打刻しました。{endTime}")
        rtn = f"{datetime.datetime.now().strftime('%m月%d日')}の終業時刻を`{int(endTime / 100)}時{endTime % 100}分`として記録しました"
    else:
        rtn = "エラー: 給料計算のURLが設定されていません"
    return rtn

def is_owner(user):
    return user.id in USERS["OWNER"]

def is_mod(user):
    return user.id in USERS["MOD"] or is_owner(user)

@commandTree.command(name="dkk", description="退勤時間を打刻します。(オーナー様専用)")
async def dkk_command(interaction: discord.Interaction, time: int = None):
    if(is_owner(interaction.user)):
        if time is None:
            dt_now = datetime.datetime.now()
            # 時間を1分前にする
            dt_now = dt_now - datetime.timedelta(minutes=1)
            time = dt_now.strftime("%H%M")
        await interaction.response.send_message(dakoku(time))
    else:
        await interaction.response.send_message("オーナー様ではありません")

@commandTree.command(name="invite", description="Botの招待リンクを生成します")
async def invite_command(interaction: discord.Interaction, app_id: str):
    await interaction.response.send_message(f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions=8&scope=bot%20applications.commands", ephemeral=True)

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
    await interaction.response.send_message(embed=bus.bus_command(time))


@commandTree.command(name="idou", description="移動販売のスケジュールを表示します")
@app_commands.describe(date="日付を指定(数字2桁 or 4桁 or 8桁, nで翌日)")
async def idou_command(interaction: discord.Interaction, date: str = ""):
    await interaction.response.send_message(embed=idou.idou_command(date))


@commandTree.command(name="ping", description="Ping値を表示します")
async def ping_command(interaction: discord.Interaction):
    # Ping値を秒単位で取得
    raw_ping = client.latency

    # ミリ秒に変換して丸める
    ping = round(raw_ping * 1000)

    # 送信する
    await interaction.response.send_message(f"Latency: {ping}ms", ephemeral=True)
    
    
@commandTree.command(name="help", description="ヘルプを表示します")
async def help_command(interaction: discord.Interaction, arg: str = None):
    if arg == "all":
        file = open(HELPALL_PATH, 'r')
    else:
        file = open(HELP_PATH, 'r')
    data = file.read()
    file.close()
    await interaction.response.send_message(data, ephemeral=True)



@commandTree.command(name="whoami", description="自分の情報を表示します")
async def whoami_command(interaction: discord.Interaction):
    user = interaction.user
    embed = discord.Embed(title="あなたの情報", color=discord.Colour.blue())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="名前", value=user.name, inline=False)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="is_owner", value=is_owner(user), inline=False)
    embed.add_field(name="is_mod", value=is_mod(user), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@commandTree.command(name="control", description="Botの管理(モデレーター以上)")
async def control_command(interaction: discord.Interaction):
    if(is_mod(interaction.user)):
        view = manageCommand()
        await interaction.response.send_message("ようこそ、モデレーター様", view=view, ephemeral=True)
    else:
        await interaction.response.send_message("権限がありません")


@commandTree.context_menu(name = "whois")
async def whois(interaction: discord.Interaction, user: discord.User):
    embed = discord.Embed(title=f"Who is {user.name}", color=discord.Colour.blue())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="名前", value=user.name, inline=False)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="is_owner", value=is_owner(user), inline=False)
    embed.add_field(name="is_mod", value=is_mod(user), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@commandTree.context_menu(name = "魚拓")
async def gyotaku(interaction: discord.Interaction, message: discord.Message):
    embed = discord.Embed(title = message.content)
    try:
        embed.add_field(name = "送信先", value = f"{message.guild.name} {message.channel.name}")
    except:
        embed.add_field(name = "送信先", value = f"DM")
    embed.set_author(name = message.author.name,icon_url = message.author.avatar.url)
    embed.set_footer(text = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
    await interaction.response.send_message(embed = embed)

jinro_urls = []

@commandTree.command(name="jinro_add", description="人狼用ワード追加")
@app_commands.describe(word="ワードかurl")
async def jinro_add(interaction: discord.Interaction, word: str):
    jinro_urls.append(word)
    await interaction.response.send_message("追加完了", ephemeral=True)
    await interaction.channel.send_message(f"追加済み{interaction.user.display_name}")

@commandTree.command(name="jinro_pop", description="ワードを1つ取り出し")
async def jinro_pop(interaction: discord.Interaction):
    if len(jinro_urls) > 0:
        # ランダムに取り出し
        jinro_url = random.choice(jinro_urls)
        # 取り出したやつ削除
        jinro_urls.remove(jinro_url)
        await interaction.response.send_message(jinro_url)
    else:
        await interaction.response.send_message("データがありません")

@commandTree.command(name="jinro_clear", description="ワードを全て削除")
async def jinro_clear(interaction: discord.Interaction):
    jinro_urls.clear()
    await interaction.response.send_message("全削除完了")

@client.event
async def on_guild_join(guild):
    print(f"サーバー{guild}に参加したよー")
    update_guilds()
    initialize()

@client.event
async def on_guild_remove(guild):
    print(f"サーバー{guild}から消されたよー")
    update_guilds()


class manageCommand(discord.ui.View): # UIキットを利用するためにdiscord.ui.Viewを継承する
    def __init__(self, timeout=180): # Viewにはtimeoutがあり、初期値は180(s)である
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="シャットダウン", style=discord.ButtonStyle.secondary)
    async def shutdown(self, interaction: discord.Interaction, button: discord.ui.Button):
        if(is_owner(interaction.user)):
            save_all()
            await interaction.response.send_message("シャットダウンします")
            await client.change_presence(activity=discord.CustomActivity(name = "シャットダウン中"), status = discord.Status.dnd)
            await client.close()
            exit()
        else:
            await interaction.response.send_message("オーナー様限定のコマンドです")
    
    @discord.ui.button(label="招待URL生成", style=discord.ButtonStyle.secondary)
    async def invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"https://discord.com/api/oauth2/authorize?client_id={APPLICATION_ID}&permissions=8&scope=bot%20applications.commands", ephemeral=True)
    
    @discord.ui.button(label="メッセージ送信", style=discord.ButtonStyle.secondary)
    async def send(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = sendMessage()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="ステメ変更", style=discord.ButtonStyle.secondary)
    async def suteme(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = changeStatus()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="打刻URL変更", style=discord.ButtonStyle.secondary)
    async def salaryurl(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = salaryURL()
        await interaction.response.send_modal(modal)

    
class sendMessage(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="送信先とメッセージの設定",
            timeout=None
        )
    
        self.channelid = discord.ui.TextInput(
            label = "チャンネルID",
            placeholder = "チャンネルIDを入力",
            required = True
        )
        self.add_item(self.channelid)
        
        self.content = discord.ui.TextInput(
            label = "送信内容",
            placeholder = "送信する内容を入力",
            required = True,
            style = discord.TextStyle.paragraph
        )
        self.add_item(self.content)
    
    async def on_submit(self, interaction: discord.Interaction):
        botRoom = client.get_channel(int(self.channelid.value))
        await botRoom.send(self.content.value)
        await interaction.response.send_message(f'<#{self.channelid.value}>に送信しました。以下送信内容\n`{self.content.value}`')
        return

class changeStatus(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="ステータス変更",
            timeout=None
        )
    
        self.status = discord.ui.TextInput(
            label = "ステータス",
            placeholder = "ステータスを入力",
            required = True
        )
        self.add_item(self.status)
    
    async def on_submit(self, interaction: discord.Interaction):
        GLOBAL_SETTINGS["PLAYING"] = self.status.value
        await client.change_presence(activity=discord.CustomActivity(name = GLOBAL_SETTINGS["PLAYING"]))
        await interaction.response.send_message(f"ステータスを{GLOBAL_SETTINGS['PLAYING']}に変更しました")
        save.global_settings()
        return

class salaryURL(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="打刻URL変更",
            timeout=None
        )
    
        self.url = discord.ui.TextInput(
            label = "URL",
            placeholder = "URLを入力",
            required = True
        )
        self.add_item(self.url)
    
    async def on_submit(self, interaction: discord.Interaction):
        GLOBAL_SETTINGS["SALARY_URL"] = self.url.value
        await interaction.response.send_message(f"打刻URLを`{self.url.value}`に変更しました")
        save.global_settings()
        return

client.run(GLOBAL_SETTINGS["TOKEN"])