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
from time import sleep

import itertools

import asyncio

# get the starting time
start = time.perf_counter()

# contemplating whether to do one client and do all requests thru that or to create a new client every time
# ok i've decided.

# client initialization (discord and gd)
i = discord.Intents().all()
client = discord.Client(intents=i)
t = app_commands.CommandTree(client)
gd_client = gd.Client()

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
    await t.sync(guild=discord.Object(id=1155489454031654943))
    # performance thing
    perf = time.perf_counter() - start
    # print success and start presence
    print("SUCCESS: Connected to Discord API and synced commands in {0} seconds".format(perf))
    change_presence.start()

# func that finds the guild owner (might not be used)
async def get_owner(guild_id : int) -> discord.Member:
    guild = client.get_guild(guild_id)
    return guild.owner

search_group = app_commands.Group(name="search", description="Search for something (users or levels)", guild_ids=[1155489454031654943])

# uwu
@t.command(name="ping", guild=discord.Object(id=1155489454031654943))
async def ping(interaction):
    await interaction.response.send_message("pong uwu")

# function that implements the daily command
@t.command(name="daily", description="Gets the current daily level.",guild=discord.Object(id=1155489454031654943))
async def daily(interaction):
    # error handling? what's error handling? i just wrap all of my code in a try catch -a person who wraps all their code in a try catch
    try:
        d = await gd_client.get_daily()
    except:
        return await interaction.response.send_message("Daily level not found.")
    
    # replace _ with whitespace and pretty it up a lil
    dd_name = str.replace(d.difficulty.name, '_', ' ').lower().capitalize()
    
    # create embed and send it
    e = (
        discord.Embed(colour=0x00C9FF)
        .add_field(name="Current Daily", value="{0} ({1})".format(d.name, d.id))
        .add_field(name="Rating", value="{0}<:Star:1166360223859101737> ({1})".format(d.stars, dd_name))
        .set_footer(icon_url="https://preview.redd.it/putting-my-geometry-dash-creator-points-image-here-so-v0-sgfl38xxycta1.png?width=640&crop=smart&auto=webp&s=817ca45d6616a201980b7be4fd980ec53e26f721", text=": {0}".format(d.creator.name))
    )

    await interaction.response.send_message(embed=e)

# i ain't doin all those comments again
@t.command(name="weekly", description="Gets the current weekly level.",guild=discord.Object(id=1155489454031654943))
async def weekly(interaction):
    try:
        w = await gd_client.get_weekly()
    except:
        return await interaction.response.send_message("Weekly level not found.")
    
    # extremely bad code that removes the _, and capitalizes the first letter of each word
    wd_name = str.replace(w.difficulty.name, '_', ' ').lower().split()
    wd_name = list(map(str.capitalize, wd_name))
    wd_name = "{0} {1}".format(wd_name[0], wd_name[1])
    
    e = (
        discord.Embed(colour=0x00C9FF)
        .add_field(name="Current Weekly", value="{0} ({1})".format(w.name, w.id))
        .add_field(name="Rating", value="{0}<:Star:1166360223859101737> ({1})".format(w.stars, wd_name))
        .set_footer(icon_url="https://preview.redd.it/putting-my-geometry-dash-creator-points-image-here-so-v0-sgfl38xxycta1.png?width=640&crop=smart&auto=webp&s=817ca45d6616a201980b7be4fd980ec53e26f721", text=": {0}".format(w.creator.name))
    )

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
        downloads = r.downloads

    e = (
        discord.Embed(colour=0x00C9FF)
        .add_field(name="Name", value="{0} (ID: {1})".format(search.name, search.account_id))
        .add_field(name="Stats", value="<:Star:1166360223859101737>: {0}\n<:Diamond:1166362286496153690>: {1}\n<:Demon:1169589936505229312>: {2}\n<:Secret_Coin:1166362293660025064>: {3}\n<:Silver_Coin:1166362296159834202>: {4}\n<:Creator_Point:1169589714110644295>: {5}".format(stats.stars, stats.diamonds, stats.demons, stats.secret_coins, stats.user_coins, stats.creator_points))
        .add_field(name="Most Recent Level", value="{0} ({1})\n<:Share:1166362299179745422>: {2}".format(name, id, downloads))

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
        await asyncio.sleep(1)

        ld_name = str.replace(level.difficulty.name, '_', ' ').lower().split()
        ld_name = list(map(str.capitalize, ld_name))
        ld_name = "{0} {1}".format(ld_name[0], ld_name[1])

        song_author = level.song.artist
        
        e = (
            discord.Embed(colour=0xFF1E27)
            .add_field(name="Name", value=level.name)
            .add_field(name="Rating", value="{0}<:Star:1166360223859101737> ({1})".format(level.stars, ld_name))
            .add_field(name="Stats", value="<:Share:1166362299179745422>: {0}\n<:Fake_Spike:1169611005098205204>: {1}".format(level.downloads, level.object_count), inline=False)
            .add_field(name="Song", value="{0} by {1} ([Link]({2}))".format(level.song.name, song_author, level.song.url), inline=False)
        )

        await interaction.followup.send(embed=e)

t.add_command(search_group)
client.run(yagddb.config["token"])

