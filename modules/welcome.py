from discord.ext import commands
from discord import Member

import discord

from config import Config
from discord_utils import get_role_by_id
from custom_message import get_customised_message
import logger

class WelcomeButton(discord.ui.Button):
	def __init__(self, member : discord.Member, role_ids, *, label="", emoji=""):
		super().__init__(label=label, emoji=emoji)

		self.member = member
		self.role_ids = role_ids

	async def callback(self, interaction: discord.Interaction):
		logger.success_message(f"""[Welcome] {self.member.name} picked {self.role_ids}""")
		for role_id in self.role_ids:
			role = get_role_by_id(role_id, self.member.guild)
			if not role:
				logger.fail_message(f"""[Welcome] Can't find role {role_id}""")
				return

			try:
				await self.member.add_roles(role)
			except discord.Forbidden as e:
				logger.fail_message(f"""[Welcome] Add role forbiden : {e}""")

		await interaction.response.edit_message(content=interaction.message.content, view=None)

		return await super().callback(interaction) 

class WelcomeView(discord.ui.View):
	def __init__(self, member : discord.Member, button_objs, *, timeout=None):
		super().__init__(timeout=timeout)

		for button_obj in button_objs:
			button = WelcomeButton(member, button_obj["roles"], emoji=button_obj["emoji"])
			self.add_item(button)

class Welcome(commands.Cog):
	def __init__(self, bot : commands.Bot):
		self.bot = bot
		self.welcome_msg_unused = []

		self.conf = Config()
		self.conf.load_json("configs/welcome.json")

	@commands.Cog.listener()
	async def on_member_join(self, member : Member):
		print('=> Welcome message')
		welcome_channel = self.bot.get_channel(self.conf.get('welcome_channel'))
		welcome_msg_obj = self.conf.get('welcome_message')

		view = WelcomeView(member, self.conf.get("buttons_roles"))
		await welcome_channel.send(get_customised_message(welcome_msg_obj['content'], welcome_msg_obj['content_args'], self.bot, { "ping": member.mention }), view=view)

		for default_role_id in self.conf.get('default_role_ids'):
			default_role = get_role_by_id(default_role_id, member.guild)
			if not default_role:
				logger.fail_message(f"""[Welcome] Can't find default role {default_role_id}""")
				return

			try:
				await member.add_roles(default_role)
			except discord.Forbidden as e:
				logger.fail_message(f"""[Welcome] Add role forbiden : {e}""")

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def welcome(self, ctx, member : Member):
		welcome_msg_obj = self.conf.get('welcome_message')

		view = WelcomeView(member, self.conf.get("buttons_roles"))
		await ctx.send(get_customised_message(welcome_msg_obj['content'], welcome_msg_obj['content_args'], self.bot, { "ping": member.mention }), view=view)

		for default_role_id in self.conf.get('default_role_ids'):
			default_role = get_role_by_id(default_role_id, member.guild)
			if not default_role:
				logger.fail_message(f"""[Welcome] Can't find default role {default_role_id}""")
				return

			try:
				await member.add_roles(default_role)
			except discord.Forbidden as e:
				logger.fail_message(f"""[Welcome] Add role forbiden : {e}""")

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		print("Recognized that " + member.name + " left")

		welcome_channel = self.bot.get_channel(self.conf.get('welcome_channel'))
		bye_message = """{0.mention} *{0.name}* ({0.nick}) a quitté le serveur.""".format(member)

		await welcome_channel.send(bye_message)

async def setup(bot):
	await bot.add_cog(Welcome(bot))