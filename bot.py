import asyncio
import discord
import asyncio

import logger
from discord_utils import * 
from config import *
from database import *
from utils import *
from custom_message import get_customised_message

import modules.instagram_module as Insta
import modules.kofi_module as Kofi
from modules.voice_module import VoiceModule, VoiceModuleEvent
import modules.gumroad_module as Gumroad
import modules.interaction_module as Interaction

from discord.ext import tasks, commands

config = Config()
config.load_json('configs/config.json')

database = Database(config.get('database_url'), 'Cluster0')

insta_config = Config()
insta_config.load_json('configs/insta_config.json')
if not Insta.init(insta_config, database):
	logger.fail_message("Can't init instagram module")
	exit()

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

interaction_module = Interaction.InteractionModule(client)

current_activity = discord.Activity(type=discord.ActivityType.watching, name="Lymeria \N{HEAVY BLACK HEART}")
current_status = discord.Status.invisible
married_member = None

async def marry_command(args, origin_channel):
	if len(args) != 2:
		await origin_channel.send("Wrong number of argument, usage : !marry <ID of luckiest user>")
		return

	try:
		wanted_user = client.get_user(int(args[1]))
		if wanted_user == None:
			await origin_channel.send("""{0} don't match any user, sowwy, wedding aborded """.format(args[1]))
			return

		config.set_value("marry", args[1]) 
		config.save_json()

		global married_member
		married_member = None # Need to be searched again

		await origin_channel.send("""{0.mention} is now married to {1.mention}""".format(client.user, wanted_user))

	except ValueError:
			await origin_channel.send("""{0} is not an valid ID, command aborded""".format(args[1]))
	except:
		logger.fail_message('Error occured with marry command')

async def divorce_command(origin_channel):
	try:
		if config.get("marry") == "":
			await origin_channel.send("""{0.mention} is already alone""".format(client.user))
		else: 
			config.set_value("marry", "")
			config.save_json()

			global married_member
			married_member = None

			await origin_channel.send("""{0.mention} will walk alone now""".format(client.user))
	except:
		logger.fail_message('Error occured with divorce command')


async def handle_input(message):
	args = parse(message.content)
	command = args[0]

	if has_role_by_id(config.get('modo_role_id'), message.author):
		if await interaction_module.handle_command(command, args, message):
			return
		elif command == 'marry':
			await marry_command(args, message.channel)
		elif command == 'divorce':
			await divorce_command(message.channel)
		elif voice_module.is_actif():
			if await voice_module.handle_command(command, args, message):
				return

async def on_mention(message):
	if str(message.author.id) == config.get("marry"):
		await message.add_reaction('\N{HEAVY BLACK HEART}')

	if voice_module.is_actif():
		await voice_module.handle_event(VoiceModuleEvent.Ping)

@client.event
async def on_message(message):
	if message.content.startswith('!'):
		await handle_input(message)
	elif client.user.mentioned_in(message):
		await on_mention(message)
	
@client.event
async def on_member_remove(member):
	print("Recognized that " + member.name + " left")

	welcome_channel = client.get_channel(config.get('welcome_channel'))
	bye_message = """{0.mention} *{0.name}* ({0.nick}) a quitté le serveur.""".format(member)

	await welcome_channel.send(bye_message)

async def update_status():
	if config.get("marry") == "":
		return

	try:
		global married_member
		if married_member == None:
			wanted_user = client.get_user(int(config.get("marry")))
			if wanted_user == None:
				logger.fail_message("""{0} don't match any user, status update aborded""".format(config.get("marry")))
				return

			married_member = get_member_by_id(wanted_user.id, client)
			if married_member == None:
				logger.fail_message("""{0} isn't find in possible member, status update aborded""".format(wanted_user.name))
				return
		
		next_status = None
		if married_member.status == discord.Status.invisible:
			next_status = discord.Status.offline
		elif married_member.status == discord.Status.offline:
			next_status = discord.Status.offline
		elif married_member.status == discord.Status.online:
			next_status = discord.Status.online
		elif married_member.status == discord.Status.dnd:
			next_status = discord.Status.idle
		elif married_member.status == discord.Status.idle:
			next_status = discord.Status.do_not_disturb

		global current_status
		if next_status != current_status and next_status != None:
			current_status = next_status
			await set_status(client, current_status, current_activity)

	except ValueError:
		logger.fail_message("""{0} is not an valid ID, status update aborded""".format(config.get("marry")))
	except Exception as e:
		print('Exception occured with status update', e)

class Looper(commands.Cog):
	def __init__(self, bot, insta_config, kofi_config, gumroad_config, database):
		self.bot = bot
		self.insta_config = insta_config
		self.kofi_config = kofi_config
		self.gumroad_config = gumroad_config
		self.database = database

		self.update_status_loop.start()
		self.update_instagram_loop.start()
		if kofi_config.get('active'):
			self.update_kofi_loop.start()
		if gumroad_config.get('active'):
			self.update_gumroad_loop.start()

	def cog_unload(self):
		self.update_status_loop.cancel()
		self.update_instagram_loop.cancel()
		self.update_kofi_loop.cancel()

	@tasks.loop(minutes=10.0)
	async def update_status_loop(self):
		await update_status()

	@tasks.loop(minutes=10.0)
	async def update_instagram_loop(self):
		await Insta.update(self.bot, self.insta_config, self.database)

	@tasks.loop(minutes=10.0)
	async def update_kofi_loop(self):
		await Kofi.update(self.bot, self.kofi_config, self.database)

	@tasks.loop(minutes=30.0)
	async def update_gumroad_loop(self):
		await Gumroad.update(self.bot, self.gumroad_config, self.database)
	
	@update_status_loop.before_loop
	async def status_before_bot(self):
		await self.bot.wait_until_ready()

	@update_instagram_loop.before_loop
	async def isntagram_before_bot(self):
		await self.bot.wait_until_ready()

	@update_kofi_loop.before_loop
	async def kofi_before_bot(self):
		await self.bot.wait_until_ready()

	@update_gumroad_loop.before_loop
	async def kofi_before_bot(self):
		await self.bot.wait_until_ready()

@client.event
async def on_ready():
	logger.success_message("""Logged in as {0.name} ({0.id})""".format(client.user))

	await set_status(client, current_status, current_activity)

	Looper(client, insta_config, kofi_config, gumroad_config, database)

async def main():
	async with client:
		await client.load_extension("modules.quote")
		await client.load_extension("modules.welcome")
		await client.start(config.get('token'))

asyncio.run(main())