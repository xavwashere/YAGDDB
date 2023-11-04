###################
#     IMPORTS     #
###################


import discord
from discord import app_commands
from discord.ext import tasks
import gd

import yagddb

import random
import time
import asyncio
import requests
import os
# get the starting time
start = time.perf_counter()

# client initialization (discord and gd)
i = discord.Intents().all()
client = discord.Client(intents=i)
t = app_commands.CommandTree(client)
gd_client = gd.Client()

class RateWebhookModal(discord.ui.Modal, title="Add a rate webhook."):
    webhook_url = discord.ui.TextInput(label="Webhook URL")

    async def on_submit(self, interaction):

        self.webhook_url = str(self.webhook_url)

        try:
            webhook = discord.Webhook.from_url(self.webhook_url, client=client)
            await webhook.send("This channel has been configured to recieve rate notifications.", username="Geometry Dash", avatar_url="https://upload.wikimedia.org/wikipedia/en/3/35/Geometry_Dash_Logo.PNG")
            await interaction.response.send_message("Setup completed successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error setting up: {e}", ephemeral=True)
            return

        with open("yagddb/webhooks.txt", "a") as txt:
            txt.write("\n{0}".format(self.webhook_url))


class SettingsBtns(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Rate Webhook", style=discord.ButtonStyle.blurple, emoji=discord.PartialEmoji(name="Star", id=1166360223859101737))
    async def rate_webhook(self, interaction : discord.Interaction, button):

        await interaction.response.send_modal(RateWebhookModal())

class MusicBtns(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(label="End", style=discord.ButtonStyle.blurple)
    async def end_music(self, interaction : discord.Interaction, button):
        guild = interaction.guild
        vc = discord.utils.get(client.voice_clients, guild=guild)
        if vc.is_connected():
            await vc.disconnect()
            for x in os.listdir("music/"):
                p = os.path.join("music/", x)
                os.remove(p)
            await interaction.response.send_message("Disconnected from VC.")

@gd_client.event
async def on_rate(level : gd.Level):
    webhooks = []
    with open("yagddb/webhooks.txt", 'r') as txt:
        p = str.split(txt.read(), "\n")
        webhooks.append(p for x in p)
    for x in webhooks:
        w = discord.Webhook.from_url(x)
        w.send(content="New rated level!", embed=create_level_embed(level), username="Geometry Dash", avatar_url="https://upload.wikimedia.org/wikipedia/en/3/35/Geometry_Dash_Logo.PNG")
        

async def get_demon_list(limit : int = 10) -> dict:
    pointercrate = "https://pointercrate.com/api/v2/"
    params = "listed/?limit={0}".format(limit)

    res = requests.get("{0}demons/{1}".format(pointercrate, params)).json()
    # r = json.loads(res)
    return res

async def get_player_list(limit : int = 10) -> dict:
    pointercrate = "https://pointercrate.com/api/v1/"
    params = "?limit={0}".format(limit)

    res = requests.get("{0}players/ranking/{1}".format(pointercrate, params)).json()
    # r = json.loads(res)
    return res

def create_level_embed(level : gd.Level, extra_info : dict or None = {"title": "Level: ", "thumbnail": None}) -> discord.Embed:
    ld_name = str.replace(level.difficulty.name, '_', ' ').lower().split()
    ld_name = list(map(str.capitalize, ld_name))
    ld_name = "{0} {1}".format(ld_name[0], ld_name[1]) if len(ld_name) > 1 else ld_name[0]

    if extra_info["title"] != "Weekly: " or extra_info["title"] != "Daily: " or extra_info["title"] != "Level: ":
        extra_info["title"] = "Level: "

    song_author = level.song.artist

    coins = ""

    for x in range(1, level.coins + 1):
        if level.verified_coins:
            coins += "<:Silver_Coin:1166362296159834202> "
        else:
            coins += "<:UnverifiedUserCoin:1170324905829597264> "
    
    if coins == "":
        coins = "None"

    extra_info["title"] += "{0} by {1}".format(level.name, level.creator.name)

    like_type = ""

    if level.rating >= 0:
        like_type = "<:Like:1170329567844638761>"
    else:
        like_type = "<:Dislike:1170330583101087764>"
    
    length = str(level.length).removeprefix("LevelLength.").lower().capitalize()
    if length == "Xl":
        length = length.upper()

    copyable = "No"
    if level.is_copyable():
        copyable = "Yes"
    
    copied = "No"
    
    if level.original_id != 0:
        copied = "Yes. Original ID: {0}".format(level.original_id)

    
    gameplay_type = "One-Player"
    if level.two_player:
        gameplay_type = "Two-Player"

    

    e = (
        discord.Embed(colour=0xFF1E27, title=extra_info["title"])
        .add_field(name="", value="**Description**: {0}\n\n**Coins**: {1}".format(level.description, coins))
        .add_field(name="Rating", value="{0}<:Star:1166360223859101737> ({1})".format(level.stars, ld_name), inline=False)
        .add_field(name="Stats", value="<:Share:1166362299179745422> {0}\n{1} {2}\n<:Fake_Spike:1169611005098205204> {3}\n<:Length:1170332753066197032>  {4}".format(level.downloads, like_type, level.rating, level.object_count, length), inline=False)
        .add_field(name="Song", value="{0} by {1} ({2} MB)\n<:Play:1170315572261703830> [{3} on Newgrounds]({4})\n<:Download:1170329573448220802> [Download {5} as MP3]({6})".format(level.song.name, song_author, level.song.size, level.song.name, level.song.url, level.song.name, level.song.download_url), inline=False)
        .add_field(name="Other Stats", value="ID: {0}\nCopyable: {1}\nGameplay Type: {2}\nCopied: {3}".format(level.id, copyable, gameplay_type, copied))
        .set_footer(icon_url="https://preview.redd.it/putting-my-geometry-dash-creator-points-image-here-so-v0-sgfl38xxycta1.png?width=640&crop=smart&auto=webp&s=817ca45d6616a201980b7be4fd980ec53e26f721", text="{0}".format(level.creator.name))
    )
    if extra_info["thumbnail"] is not None:
        e.set_thumbnail(url=extra_info["thumbnail"])

    return e

# useless print function
print("YAGDDB - Yet Another Geometry Dash Discord Bot")



# func that changes the bot's presence every 10 seconds
@tasks.loop(seconds=10)
async def change_presence():
    # get the amount of servers the bot is in
    server_count = str(len(client.guilds))
    global x
    # list of presences
    watch = iter([
        "2.2 come out",
        "xavvvv sleep",
        "DemonGDPS",
        "{0} servers".format(server_count),
        "Zoink verify a top 1",
        "Tidal Wave not be rated",
        "Avernus be top 1"
    ])
    # randomly pick the next presence
    for x in range(random.randint(1, 7)):
        x = next(watch)
    # actually change the presence
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=x))

@client.event
async def on_ready():
    # sync cmd tree
    await t.sync()
    # performance thing
    perf = time.perf_counter() - start
    # print success and start presence
    print("SUCCESS: Connected to Discord API and synced commands in {0} seconds".format(perf))

    if not change_presence.is_running():
        change_presence.start()

# func that finds the guild owner (might not be used)
async def get_owner(guild_id : int) -> discord.Member:
    guild = client.get_guild(guild_id)
    return guild.owner

search_group = app_commands.Group(name="search", description="Search for something (users or levels)")

# uwu
@t.command(name="ping")
async def ping(interaction):
    await interaction.response.send_message(":ping_pong: Pong! GD server responded in {0}s. The bot responded in {1} seconds.".format(await gd_client.ping(), round(client.latency, 3)))

# function that implements the daily command
@t.command(name="daily", description="Gets the current daily level.",)
async def daily(interaction):
    # error handling? what's error handling? i just wrap all of my code in a try catch -a person who wraps all their code in a try catch
    try:
        d = await gd_client.get_daily()
    except:
        return await interaction.response.send_message("Daily level not found.")
    
    e = create_level_embed(d, {"title": "Daily: ", "thumbnail": "https://images-ext-2.discordapp.net/external/WmbQOWwJgceD7Ag9QF07ZYU_q6-fSdbsDRpnCBROk3c/https/i.imgur.com/enpYuB8.png"})

    await interaction.response.send_message(embed=e)

# i ain't doin all those comments again
@t.command(name="weekly", description="Gets the current weekly level.")
async def weekly(interaction):
    try:
        w = await gd_client.get_weekly()
    except:
        return await interaction.response.send_message("Weekly level not found.")
    
    e = create_level_embed(w, {"title": "Weekly: ", "thumbnail": "https://images-ext-2.discordapp.net/external/-V-AYSPiOoLwoowRlUWtlDAFJx7N4xyVqpZuKuFMitM/https/i.imgur.com/kcsP5SN.png"})

    await interaction.response.send_message(embed=e)

@search_group.command(name="user", description="Search for a user and display their stats")
async def search_user(interaction, user : str):
    try:
        search = await gd_client.search_user(user)
    except:
        return await interaction.response.send_message("There was a problem finding the user.")
    stats = search.statistics
    levels = await search.get_levels()

    await interaction.response.defer()
    await asyncio.sleep(0)

    username = search.name

    is_mod = False
    is_elder = False

    acc_id = search.account_id

    data = {
        "secret": "Wmfd2893gb7",
        "targetAccountID": acc_id
    }

    resp = iter(str.split(requests.post("http://www.boomlings.com/database/getGJUserInfo20.php", data=data, headers={"User-Agent": ""}).text, ':'))
    resp = dict(zip(resp, resp))
    mod_level = resp["49"]

    if mod_level == "1":
        is_mod = True
        username += " <:Moderator:1166362417266180156>"

    elif mod_level == "2":
        is_elder = True
        username += " <:SeniorModerator:1166362419048755241>"


    if levels:
        r = levels[0]

        id = r.id
        name = r.name
    else:
        name = "User has no levels"
        id = "N/A"
    
    youtube = search.socials.youtube
    twitter = search.socials.twitter
    twitch = search.socials.twitch

    if not os.path.exists("icons/{0}{1}.png".format(search.id, search.name)):
        icons = await search.cosmetics.generate_full_async()
        icons.save("icons/{0}{1}.png".format(search.id, search.name))
        
    d_icons = discord.File("icons/{0}{1}.png".format(search.id, search.name), filename="{0}{1}.png".format(search.id, search.name))
    

    if youtube is None:
        youtube = "None"
    else:
        youtube = "https://youtube.com/{0}".format(youtube)
        youtube = "[YouTube]({0})".format(youtube)
    if twitter is None:
        twitter = "None"
    else:
        twitter = "https://twitter.com/{0}".format(twitter)
        twitter = "[Twitter]({0})".format(twitter)
    if twitch is None:
        twitch = "None"
    else:
        twitch = "https://twitch.tv/{0}".format(twitch)
        twitch = "[Twitch]({0})".format(twitch)

    rank = stats.rank
    if rank == 0:
        rank = "Unranked"

    e = (
        discord.Embed(colour=0x00C9FF)
        .add_field(name="Name", value="{0} (ID: {1} | Account ID: {2})".format(username, search.id, search.account_id), inline=False)
        .add_field(name="Stats", value="<:Star:1166360223859101737> {0}\n<:Diamond:1166362286496153690> {1}\n<:Demon:1169589936505229312> {2}\n<:Secret_Coin:1166362293660025064> {3}\n<:Silver_Coin:1166362296159834202> {4}\n<:Creator_Point:1169589714110644295> {5}\n<:Rank:1170362250570236004> {6}".format(stats.stars, stats.diamonds, stats.demons, stats.secret_coins, stats.user_coins, stats.creator_points, rank), inline=False)
        .add_field(name="Socials", value="<:YouTube:1170315574803451904> {0}\n<:Twitter:1170315580205699112> {1}\n<:Twitch:1170315578964193280> {2}".format(youtube, twitter, twitch))
        .add_field(name="Most Recent Level", value="{0} ({1})".format(name, id), inline=False)
        .set_image(url="attachment://{0}{1}.png".format(search.id, search.name))
    )
    await interaction.followup.send(embed=e, file=d_icons)
    icons = os.listdir("icons/")
    for x in icons:
        p = os.path.join("icons/", x)
        os.remove(p)

@search_group.command(name="level", description="Search for a level")
async def search_level(interaction, level : str):
    try:
        search = await gd_client.search_levels(level)
    except:
        await interaction.response.send_message("There was an issue finding the level.")
    
    await interaction.response.defer()
    await asyncio.sleep(0)
    
    if search:
        level = search[0]

        e = create_level_embed(level)

        await interaction.followup.send(embed=e)
    else:
        await interaction.followup.send("Level not found.")
    
@t.command(name="checkmod", description="Check if someone has moderator permissions")
async def check_mod(interaction, username : str):


    if username is None:
        await interaction.response.send_message("No user chosen. Please choose a user to check before running this command")
        return
    
    user = await gd_client.search_user(username)

    if not user:
        await interaction.response.send_message("Invalid user.")
        return
    
    await interaction.response.defer()
    await asyncio.sleep(0)
       
    is_mod = False
    is_elder = False

    id = user.account_id

    data = {
        "secret": "Wmfd2893gb7",
        "targetAccountID": id
    }

    resp = iter(str.split(requests.post("http://www.boomlings.com/database/getGJUserInfo20.php", data=data, headers={"User-Agent": ""}).text, ':'))
    resp = dict(zip(resp, resp))
    mod_level = resp["49"]

    if mod_level == "1":
        is_mod = True
    elif mod_level == "2":
        is_elder = True
    


    if is_mod:
        e = (
            discord.Embed(colour=0x00C9FF)
            .add_field(name=user.name + " <:Moderator:1166362417266180156>", value="User is a moderator.")
        )
        await interaction.followup.send(embed=e)
    elif is_elder:
        e = (
            discord.Embed(colour=0x00C9FF)
            .add_field(name=user.name + " <:SeniorModerator:1166362419048755241>", value="User is an elder moderator.")
        )
        await interaction.followup.send(embed=e)
    elif not is_mod and not is_elder:
        e = (
            discord.Embed(colour=0x00C9FF)
            .add_field(name=user.name, value="User is not a moderator.")
        )
        await interaction.followup.send(embed=e)
    

@t.command(name="demonlist", description="Show the top 10 demonlist levels")
async def demonlist(interaction):
    demonlist = await get_demon_list()


    
    e = discord.Embed(colour=0x00C9FF)

    for pos in demonlist:
        e.add_field(name="{0}. {1}".format(pos["position"], pos["name"]), value="Verifier: {0}\nCreator: {1}\n[Verification]({2})".format(pos["verifier"]["name"], pos["publisher"]["name"], pos["video"]), inline=False)
    
    e.add_field(name="JSON", value="[Download JSON](https://pointercrate.com/api/v2/demons/listed/?limit=10)")
    await interaction.response.send_message(embed=e)
        
@t.command(name="leaderboard", description="Show the top 10 demonlist players")
async def playerlist(interaction):
    player_list = await get_player_list()


    
    e = discord.Embed(colour=0x00C9FF)

    for pos in player_list:
        e.add_field(name="{0}. {1}".format(pos["rank"], pos["name"]), value="Points: {0}\nNationality: {1} ({2})".format(round(pos["score"]), pos["nationality"]["nation"], pos["nationality"]["country_code"]), inline=False)
    e.add_field(name="JSON", value="[Download JSON](https://pointercrate.com/api/v1/players/ranking?limit=10)")
    await interaction.response.send_message(embed=e)


@t.command(name="settings", description="Change the YAGDDB settings (per server)")
async def settings(interaction):
    e = (
        discord.Embed(colour=0x00C9FF, title="Settings")
        .add_field(name="Rate Webhook", value="Recieve a message through a webhook when a level on Geometry Dash is rated (currently broken)")
    )
    await interaction.response.send_message(embed=e, view=SettingsBtns())


@t.command(name="music", description="Play a song from Newgrounds.")
async def music(interaction : discord.Interaction, id : int):
    try:
        channel = interaction.user.voice.channel
    except:
        await interaction.response.send_message("You are not in a voice channel! Join one before continuing!")
    try:
        music = await gd_client.get_song(id)
    except:
        await interaction.response.send_message("Invalid song ID.", ephemeral=True)
    link = music.download_url
    await interaction.response.send_message("Downloading {0} from Newgrounds...".format(music.name), ephemeral=True)
    d = requests.get(link)
    print(link)
    with open("music/{0}.mp3".format(id), "wb") as f:
        f.write(d.content)
    cv = await channel.connect()
    await interaction.followup.send("Joined voice channel! Controls:", view=MusicBtns(), ephemeral=True)

    cv.play(discord.FFmpegPCMAudio("music/{0}.mp3".format(id)))
    cv.is_playing()

    while cv.is_playing():
        if len(channel.members) < 2:
            await cv.disconnect()
        await asyncio.sleep(1)
    await cv.disconnect()
    for x in os.listdir("music/"):
        p = os.path.join("music/", x)
        os.remove(p)

t.add_command(search_group)
client.run(yagddb.config["token"])
gd_client.listen_for_rate()
gd_client.create_controller().run()