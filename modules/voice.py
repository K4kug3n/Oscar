import discord
import logger
import random
import asyncio
from enum import Enum, auto

from discord.ext import commands

import logger
from config import Config

class VoiceModuleEvent(Enum):
	Join = auto()
	Quit = auto()
	Ping = auto()

class Voice(commands.Cog):
	def __init__(self, bot : commands.Bot):
		self.bot = bot

		self.conf = Config()
		self.conf.load_json('configs/voice.json')

		if not self.conf.has("on_ping") or not "active" in self.conf.get("on_ping"):
			self.conf.set_value("on_ping", { "active": False })

		if not self.conf.has("on_join") or not "active" in self.conf.get("on_join"):
			self.conf.set_value("on_join", { "active": False })

		if not self.conf.has("on_quit") or not "active" in self.conf.get("on_quit"):
			self.conf.set_value("on_quit", { "active": False })

		self.conf.save_json()

		self.voice_client = None

	def is_connected(self):
		return self.voice_client != None

	def play_file(self, file : str, after_callback=None):
		audio_source = discord.FFmpegOpusAudio('sounds/' + file, options='-loglevel panic')

		self.voice_client.play(audio_source, after=after_callback)

	async def handle_event(self, event : VoiceModuleEvent):
		if not self.is_connected():
			return
		
		if event == VoiceModuleEvent.Join:
			await self.on_event('on_join')
		elif event == VoiceModuleEvent.Quit:
			await self.on_event('on_quit')
		elif event == VoiceModuleEvent.Ping:
			await self.on_event('on_ping')

	def process_custom_sound(self, custom_sound_data : dict):
		if custom_sound_data['type'] == 'SINGLE':
			return [ custom_sound_data['name'] ]
		if custom_sound_data['type'] == 'RANDOM':
			return [ random.choice(custom_sound_data['names']) ]

		logger.fail_message(f"""[Voice] Unknow custom sound type : {custom_sound_data['type']}""")

		return None

	async def on_event(self, event_name : str):
		on_event_data = self.conf.get(event_name)
		if not on_event_data['active']:
			return
		
		sound_names = self.process_custom_sound(on_event_data)
		if not sound_names:
			return
		
		for name in sound_names:
			self.play_file(name)
			await self.wait_until_silent()

	@commands.group()
	@commands.has_permissions(administrator = True)
	async def voice(self, ctx : commands.Context):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid quote command')

	@voice.command()
	@commands.has_permissions(administrator = True)
	async def join(self, ctx : commands.Context, channel : discord.VoiceChannel):
		if self.is_connected():
			await ctx.send("I'm only one guy, how can I be in 2 places at same time ? (quantum not allowed)")
			return
	
		self.voice_client = await channel.connect()

		await self.handle_event(VoiceModuleEvent.Join)

	@voice.command()
	@commands.has_permissions(administrator = True)
	async def quit(self, ctx : commands.Context):
		if not self.is_connected():
			await ctx.send("I must be connected to a voice channel before quit")
			return

		await self.handle_event(VoiceModuleEvent.Quit)
		await self.wait_until_silent()

		await self.voice_client.disconnect()
		self.voice_client = None

	@voice.command()
	@commands.has_permissions(administrator = True)
	async def play(self, ctx : commands.Context, file : str):
		if not self.is_connected():
			await ctx.send("I must be connected to a voice channel before play")
			return

		self.play_file(file)

	@commands.Cog.listener()
	async def on_message(self, message : discord.Message):
		if self.bot.user.mentioned_in(message):
			await self.handle_event(VoiceModuleEvent.Ping)
	
async def setup(bot):
	await bot.add_cog(Voice(bot))