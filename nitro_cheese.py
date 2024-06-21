# bot.py
import os
import random
import discord
import pickle
import asyncio
from pprint import pprint
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents(reactions = True, messages = True, message_content = True, guilds = True)

bot = commands.Bot(command_prefix='/', intents=intents)

try:
	with open("nitro_cheese_settings", "rb") as file:
		settings = pickle.load(file)
except FileNotFoundError:
	print("Settings file not found. Using defaults.");
	settings = {}

def save_settings():
	with open("nitro_cheese_settings", "wb") as file:
		pickle.dump(settings, file)

@bot.event
async def on_ready():
	print(f"{bot.user} has connected to Discord!")

@bot.command(name="reactions", help="Sets the reactions that Nitro Cheese uses.")
async def nine_nine(ctx, subcommand, *args):
	if subcommand == "set":
		if ctx.guild.id not in settings:
			settings[ctx.guild.id] = {}
		if ctx.channel.id not in settings[ctx.guild.id]:
			settings[ctx.guild.id][ctx.channel.id] = {}
		settings[ctx.guild.id][ctx.channel.id]["reactions"] = set(args)
		await ctx.send("Set reactions to: " + " ".join(set(args)))
		save_settings()
	elif subcommand == "remove_all":
		if ctx.guild.id in settings and ctx.channel.id in settings[ctx.guild.id]:
			settings[ctx.guild.id][ctx.channel.id]["reactions"] = set([])
		await ctx.send("Removed all reactions from channel")
	elif subcommand == "add":
		if ctx.guild.id not in settings:
			settings[ctx.guild.id] = {}
		if ctx.channel.id not in settings[ctx.guild.id]:
			settings[ctx.guild.id][ctx.channel.id] = {}
		if "reactions" not in settings[ctx.guild.id][ctx.channel.id]:
			settings[ctx.guild.id][ctx.channel.id]["reactions"] = set([])
		settings[ctx.guild.id][ctx.channel.id]["reactions"] = settings[ctx.guild.id][ctx.channel.id]["reactions"].union(set(args))
		await ctx.send("Added reactions: " + " ".join(set(args)))
		save_settings()
	elif subcommand == "delay":
		if ctx.guild.id in settings and ctx.channel.id in settings[ctx.guild.id]:
			settings[ctx.guild.id][ctx.channel.id]["delay"] = int(args[0])
			await ctx.send(f"Set delay of {int(args[0])} seconds")
	elif subcommand == "view":
		await ctx.send("Current reactions: " + " ".join(settings[ctx.guild.id][ctx.channel.id]["reactions"]))
	elif subcommand == "check_channel":
		await ctx.send(f"guild: `{ctx.guild.id}`\nchannel: `{ctx.channel.id}`")
	elif subcommand == "add_to":
		guild_id = int(args[0])
		channel_id = int(args[1])
		if guild_id in settings and channel_id in settings[guild_id]:
			settings[guild_id][channel_id]["reactions"] = settings[guild_id][channel_id]["reactions"].union(set(args[2:]))
			await ctx.send("Added reactions: " + " ".join(set(args[2:])))
			save_settings()
	else:
		await ctx.send(f"Unknown argument '{subcommand}'.")

@bot.listen()
async def on_message(message):
	if message.guild.id in settings and message.channel.id in settings[message.guild.id] and message.content[0] != "/":
		for reaction in settings[message.guild.id][message.channel.id]["reactions"]:
			await message.add_reaction(reaction)
		await asyncio.sleep(settings[message.guild.id][message.channel.id]["delay"])
		for reaction in settings[message.guild.id][message.channel.id]["reactions"]:
			await message.remove_reaction(reaction, member = bot.user)
		await bot.process_commands(message)

bot.run(TOKEN)

