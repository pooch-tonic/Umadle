from dotenv import load_dotenv
load_dotenv()

from os import getenv

import discord
from discord.ext import commands

from gsheet import get_data, update_data, get_autocomplete_names
from logger import setup_discord_logging
from chardle import play_game, handle_answer

TOKEN = getenv('TOKEN')
LOGGING_CHANNEL_ID = getenv('LOGGING_CHANNEL_ID')
OWNER_ID = getenv('OWNER_ID')

update_data()

intents = discord.Intents.default()

bot = discord.Bot(intents=intents)

game = bot.create_group("game", "Game commands")
util = bot.create_group("util", "Utility commands")

@bot.event
async def on_ready():
    wakeup_msg='We have logged in as {0.user}'.format(bot)

    if LOGGING_CHANNEL_ID is not None:
        await setup_discord_logging(bot, LOGGING_CHANNEL_ID)
        print(wakeup_msg)
    else:
        print(wakeup_msg)

@game.command()
async def play(ctx: discord.ApplicationContext):    
    await play_game(ctx, ctx.author.id, get_data())

@game.command()
async def answer(ctx: discord.ApplicationContext, name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_autocomplete_names()))):
    await handle_answer(ctx, ctx.author.id, name, get_data(), get_autocomplete_names())

@util.command(description="Check my response time.") 
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f"My latency is {round(bot.latency * 1000)} ms.")

@util.command(description="Owner only. Update my data.")
async def refetch(ctx: discord.ApplicationContext):
    if ctx.author.id == int(OWNER_ID):
        update_data()
        await ctx.respond("Updated from Google Sheets.", ephemeral=True)
    else:
        await ctx.respond(f"You are not allowed to execute this command.", ephemeral=True)

bot.run(TOKEN)
