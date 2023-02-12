import asyncio
import discord

import logger
from discord_utils import * 
from config import *
from database import *
from utils import *

import modules.kofi_module as Kofi
from modules.voice_module import VoiceModule, VoiceModuleEvent
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

voice_config = Config()
voice_config.load_json('configs/voice_config.json')
voice_module = VoiceModule(client, voice_config)
if not voice_module.is_valid():
	logger.fail_message("Can't init voice module")
	exit()

async def handle_input(message):
	args = parse(message.content)
	command = args[0]

	if has_role_by_id(config.get('modo_role_id'), message.author):
		if voice_module.is_actif():
			if await voice_module.handle_command(command, args, message):
				return

async def on_mention(message):
	if voice_module.is_actif():
		await voice_module.handle_event(VoiceModuleEvent.Ping)

# @client.event
# async def on_message(message):
# 	if message.content.startswith('!'):
# 		await handle_input(message)
# 	elif client.user.mentioned_in(message):
# 		await on_mention(message)

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
		self.update_instagram_loop.cancel()
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