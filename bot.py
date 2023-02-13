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

@bot.command()
@commands.has_permissions(administrator = True)
async def list(ctx):
	embed = discord.Embed(
		title='Active module',
		description='\n'.join(config.get("active_modules")),
		color=0xFF5733
	)

	await ctx.send(embed=embed)

async def main():
	async with bot:
		for module in config.get("active_modules"):
			await bot.load_extension(f"""modules.{module}""")
		await bot.start(config.get('token'))

asyncio.run(main())