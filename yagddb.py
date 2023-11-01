import discord
from discord import app_commands
from discord.ext import tasks
import gd
import yagddb

import random

import time
from time import sleep

start = time.perf_counter()

# contemplating whether to do one client and do all requests thru that or to create a new client every time
# ok i've decided.

i = discord.Intents().all()
client = discord.Client(intents=i)
t = app_commands.CommandTree(client)
gd_client = gd.Client()

print("YAGDDB - Yet Another Geometry Dash Discord Bot")

@tasks.loop(seconds=10)
async def change_presence():
    server_count = str(len(client.guilds))
    global x
    watch = iter([
        "2.2 come out",
        "xavvvv sleep",
        "DemonGDPS",
        "{0} servers".format(server_count)
    ])

    for x in range(random.randint(1, 4)):
        x = next(watch)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=x))

@client.event
async def on_ready():
    await t.sync(guild=discord.Object(id=1155489454031654943))
    perf = time.perf_counter() - start
    print("SUCCESS: Connected to Discord API and synced commands in {0} seconds".format(perf))
    change_presence.start()

async def get_owner(guild_id : int) -> discord.Member:
    guild = client.get_guild(guild_id)
    return guild.owner


@t.command(name="test", guild=discord.Object(id=1155489454031654943))
async def test(interaction):
    await interaction.response.send_message("pong uwu")

@t.command(name="daily", guild=discord.Object(id=1155489454031654943))
async def daily(interaction):
    try:
        d = await gd_client.get_daily()
    except:
        return await interaction.response.send_message("Daily level not found.")
    
    e = (
        discord.Embed(colour=0x00C9FF)
        .add_field(name="Current Daily", value="{0} ({1})".format(d.name, d.id))
        .add_field(name="Rating", value="{0} ({1})".format(d.stars, d.difficulty.name))
        .set_footer(text="Creator: {0}".format(d.creator.name))
    )

    await interaction.response.send_message(embed=e)


client.run(yagddb.config["token"])

