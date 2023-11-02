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
# get the starting time
start = time.perf_counter()

# client initialization (discord and gd)
i = discord.Intents().all()
client = discord.Client(intents=i)
t = app_commands.CommandTree(client)
gd_client = gd.Client()

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

def create_level_embed(level : gd.Level) -> discord.Embed:
    ld_name = str.replace(level.difficulty.name, '_', ' ').lower().split()
    ld_name = list(map(str.capitalize, ld_name))
    ld_name = "{0} {1}".format(ld_name[0], ld_name[1]) if len(ld_name) > 1 else ld_name[0]

    song_author = level.song.artist

    e = (
        discord.Embed(colour=0xFF1E27)
        .add_field(name="Name", value=level.name)
        .add_field(name="Rating", value="{0}<:Star:1166360223859101737> ({1})".format(level.stars, ld_name))
        .add_field(name="Stats", value="<:Share:1166362299179745422>: {0}\n<:Fake_Spike:1169611005098205204>: {1}".format(level.downloads, level.object_count), inline=False)
        .add_field(name="Song", value="{0} by {1} ([Link]({2}))".format(level.song.name, song_author, level.song.url), inline=False)
        .set_footer(icon_url="https://preview.redd.it/putting-my-geometry-dash-creator-points-image-here-so-v0-sgfl38xxycta1.png?width=640&crop=smart&auto=webp&s=817ca45d6616a201980b7be4fd980ec53e26f721", text="{0}".format(level.creator.name))
    )

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
        "{0} servers".format(server_count)
    ])
    # randomly pick the next presence
    for x in range(random.randint(1, 4)):
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
    change_presence.start()

# func that finds the guild owner (might not be used)
async def get_owner(guild_id : int) -> discord.Member:
    guild = client.get_guild(guild_id)
    return guild.owner

search_group = app_commands.Group(name="search", description="Search for something (users or levels)")

# uwu
@t.command(name="ping")
async def ping(interaction):
    await interaction.response.send_message("pong uwu")

# function that implements the daily command
@t.command(name="daily", description="Gets the current daily level.",)
async def daily(interaction):
    # error handling? what's error handling? i just wrap all of my code in a try catch -a person who wraps all their code in a try catch
    try:
        d = await gd_client.get_daily()
    except:
        return await interaction.response.send_message("Daily level not found.")
    
    e = create_level_embed(d)

    await interaction.response.send_message(embed=e)

# i ain't doin all those comments again
@t.command(name="weekly", description="Gets the current weekly level.")
async def weekly(interaction):
    try:
        w = await gd_client.get_weekly()
    except:
        return await interaction.response.send_message("Weekly level not found.")
    
    e = create_level_embed(w)

    await interaction.response.send_message(embed=e)

@search_group.command(name="user", description="Search for a user and display their stats")
async def search_user(interaction, user : str):
    try:
        search = await gd_client.search_user(user)
    except:
        return await interaction.response.send_message("There was a problem finding the user.")
    stats = search.statistics
    levels = await search.get_levels()

    if levels:
        r = levels[0]

        id = r.id
        name = r.name
    else:
        name = "User has no levels"
        id = "N/A"

    e = (
        discord.Embed(colour=0x00C9FF)
        .add_field(name="Name", value="{0} (ID: {1})".format(search.name, search.account_id), inline=False)
        .add_field(name="Stats", value="<:Star:1166360223859101737>: {0}\n<:Diamond:1166362286496153690>: {1}\n<:Demon:1169589936505229312>: {2}\n<:Secret_Coin:1166362293660025064>: {3}\n<:Silver_Coin:1166362296159834202>: {4}\n<:Creator_Point:1169589714110644295>: {5}".format(stats.stars, stats.diamonds, stats.demons, stats.secret_coins, stats.user_coins, stats.creator_points), inline=False)
        .add_field(name="Most Recent Level", value="{0} ({1})".format(name, id), inline=False)

    )
    await interaction.response.send_message(embed=e)

@search_group.command(name="level", description="Search for a level")
async def search_level(interaction, level : str):
    try:
        search = await gd_client.search_levels(level)
    except:
        await interaction.response.send_message("There was an issue finding the level.")
    
    if search:
        level = search[0]
        await interaction.response.defer()
        await asyncio.sleep(0)

        e = create_level_embed(level)

        await interaction.followup.send(embed=e)
    else:
        await interaction.response.send_message("Level not found.")
    
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
    

t.add_command(search_group)
client.run(yagddb.config["token"])

