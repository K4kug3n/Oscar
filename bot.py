import asyncio
import discord

import logger
from discord_utils import * 
from config import *
from database import *
from utils import *

import modules.kofi_module as Kofi
import modules.gumroad_module as Gumroad

from discord.ext import tasks, commands

config = Config()
config.load_json('configs/config.json')

database = Database(config.get('database_url'), 'Cluster0')

kofi_config = Config()
kofi_config.load_json('configs/kofi_config.json')
if kofi_config.get('active') and not Kofi.init(kofi_config, database):
	logger.fail_message("Can't init kofi module")
	exit()

gumroad_config = Config()
gumroad_config.load_json('configs/gumroad_config.json')
if gumroad_config.get('active') and not Gumroad.init(gumroad_config, database):
	logger.fail_message("Can't init Gumroad module")
	exit()

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

class Looper(commands.Cog):
	def __init__(self, bot, kofi_config, gumroad_config, database):
		self.bot = bot
		self.kofi_config = kofi_config
		self.gumroad_config = gumroad_config
		self.database = database

		if kofi_config.get('active'):
			self.update_kofi_loop.start()
		if gumroad_config.get('active'):
			self.update_gumroad_loop.start()

	def cog_unload(self):
		self.update_kofi_loop.cancel()

	@tasks.loop(minutes=10.0)
	async def update_kofi_loop(self):
		await Kofi.update(self.bot, self.kofi_config, self.database)

	@tasks.loop(minutes=30.0)
	async def update_gumroad_loop(self):
		await Gumroad.update(self.bot, self.gumroad_config, self.database)

	@update_kofi_loop.before_loop
	async def kofi_before_bot(self):
		await self.bot.wait_until_ready()

	@update_gumroad_loop.before_loop
	async def kofi_before_bot(self):
		await self.bot.wait_until_ready()

@client.event
async def on_ready():
	logger.success_message("""Logged in as {0.name} ({0.id})""".format(client.user))

	Looper(client, kofi_config, gumroad_config, database)

async def main():
	async with client:
		for module in config.get("active_modules"):
			await client.load_extension(f"""modules.{module}""")
		await client.start(config.get('token'))

asyncio.run(main())