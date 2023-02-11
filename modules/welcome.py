from discord.ext import commands
from discord import Member

from config import Config
from discord_utils import get_role_by_id, has_role_by_id
from custom_message import get_customised_message
import logger

class Welcome(commands.Cog):
	def __init__(self, bot : commands.Bot):
		self.bot = bot
		self.welcome_msg_unused = []

		self.conf = Config()
		self.conf.load_json("configs/welcome_config.json")

		self.reactions_roles = {
			'\N{CHERRY BLOSSOM}': [self.conf.get('female_role_id'), self.conf.get('female_color_id')], # Cherry Blossom
			'\N{COMET}': [self.conf.get('male_role_id'), self.conf.get('male_color_id')], # Comet
			'\N{ROSE}': [self.conf.get('unknow_role_id'), self.conf.get('unknow_color_id')] # Rose
		}

	@commands.Cog.listener()
	async def on_member_join(self, member : Member):
		print('=> Welcome message')
		welcome_channel = self.bot.get_channel(self.conf.get('welcome_channel'))
		welcome_msg_obj = self.conf.get('welcome_message')

		sended_msg = await welcome_channel.send(get_customised_message(welcome_msg_obj['content'], welcome_msg_obj['content_args'], self.bot, { "ping": member.mention }))

		for reaction in self.reactions_roles.keys():
			await sended_msg.add_reaction(reaction)

		self.welcome_msg_unused.append(sended_msg.id) 

		for default_role_id in self.config.get('default_role_ids'):
			default_role = get_role_by_id(default_role_id, member.guild)
			if default_role == None:
				return
			await member.add_roles(default_role)

	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if user == self.bot.user:
			return

		if self.welcome_msg_unused.count(reaction.message.id) != 0:
			for role_id in self.config.get('default_role_ids'):
				if not has_role_by_id(role_id, user):
					await reaction.remove(user)
					return

			if reaction.emoji in self.reactions_roles:
				logger.success_message("""{0.mention} asked to be {1}""".format(user, self.reactions_roles[reaction.emoji])[0])

				for default_role_id in self.reactions_roles[reaction.emoji]:
					default_role = get_role_by_id(default_role_id, user.guild)
					if default_role == None:
						return
					await user.add_roles(default_role)

				self.welcome_msg_unused.remove(reaction.message.id)
			else:
				await reaction.remove(user)

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		print("Recognized that " + member.name + " left")

		welcome_channel = self.bot.get_channel(self.conf.get('welcome_channel'))
		bye_message = """{0.mention} *{0.name}* ({0.nick}) a quitté le serveur.""".format(member)

		await welcome_channel.send(bye_message)

async def setup(bot):
	await bot.add_cog(Welcome(bot))