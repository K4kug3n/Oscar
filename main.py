import asyncio
import discord
from discord.ext import commands

import logger
from config import Config

config = Config()
config.load_json('configs/config.json')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
	logger.success_message("""Logged in as {0.name} ({0.id})""".format(bot.user))

async def main():
	async with bot:
		await bot.load_extension(f"""modules.module""")
		for module in config.get("active_modules"):
			await bot.load_extension(f"""modules.{module}""")
		await bot.start(config.get('token'))

asyncio.run(main())