from discord.ext import commands, tasks
import discord

from config import Config

class Wedding(commands.Cog):
	def __init__(self, bot : commands.Bot):
		self.bot = bot

		self.conf = Config()
		self.conf.load_json("configs/wedding.json")

		self.married_member = self.conf.get("married_member")
		self.current_status = discord.Status.invisible

		self.update_status_loop.start()

	@commands.command()
	async def marry(self, ctx, member: discord.Member):
		self.conf.set_value("married_member", str(member.id)) 
		self.conf.save_json()

		self.married_member = str(member.id)

		await ctx.send("""{self.bot.user.mention} is now married to {member.mention}""")

	@commands.command()
	async def divorce(self, ctx):
		if self.married_member == "":
			await ctx.send("""{self.bot.user.mention} is already alone""")
			return

		self.conf.set_value("married_member", "")
		self.conf.save_json()
		self.married_member = ""

		await ctx.send("""{self.bot.user.mention} will walk alone now""")

	@tasks.loop(minutes=1.0)
	async def update_status_loop(self):
		if self.married_member == "":
			return

		user = discord.utils.get(self.bot.get_all_members(), id=int(self.married_member))
		if not user:
			self.married_member = ""
			return
    		
		next_status = None
		if user.status == discord.Status.invisible:
			next_status = discord.Status.offline
		elif user.status == discord.Status.offline:
			next_status = discord.Status.offline
		elif user.status == discord.Status.online:
			next_status = discord.Status.online
		elif user.status == discord.Status.dnd:
			next_status = discord.Status.idle
		elif user.status == discord.Status.idle:
			next_status = discord.Status.do_not_disturb

		activity = discord.Activity(type=discord.ActivityType.watching, name="""{} \N{HEAVY BLACK HEART}""".format(user.name))

		if next_status != self.current_status and next_status != None:
			self.current_status = next_status
			await self.bot.change_presence(status=self.current_status, activity=activity)

	@update_status_loop.before_loop
	async def status_before_bot(self):
		await self.bot.wait_until_ready()
		
async def setup(bot):
	await bot.add_cog(Wedding(bot))