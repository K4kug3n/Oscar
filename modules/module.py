from discord.ext import commands
import discord

from config import Config

class Module(commands.Cog, name='module'):
	def __init__(self, bot : commands.Bot):
		self.bot = bot

		self.conf = Config()
		self.conf.load_json("configs/config.json")

	@commands.group()
	@commands.has_permissions(administrator = True)
	async def module(self, ctx : commands.Context):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid module command')

	@module.command()
	@commands.has_permissions(administrator = True)
	async def list(self, ctx : commands.Context):
		embed = discord.Embed(
			title='Active module',
			description='\n'.join(self.conf.get("active_modules")),
			color=0xFF5733
		)

		await ctx.send(embed=embed)

	@module.command()
	@commands.has_permissions(administrator = True)
	async def load(self, ctx : commands.Context, name : str):
		active_modules = self.conf.get("active_modules")
		if name in active_modules:
			await ctx.send(f"""{name} is an active module""")
			return

		await self.bot.load_extension(f"""modules.{name}""")
		
		active_modules.append(name)
		self.conf.set_value("active_modules", active_modules)
		self.conf.save_json()

		await ctx.message.add_reaction("✅")

	@module.command()
	@commands.has_permissions(administrator = True)
	async def unload(self, ctx : commands.Context, name : str):
		active_modules = self.conf.get("active_modules")
		if not name in active_modules:
			await ctx.send(f"""{name} is not an active module""")
			return

		await self.bot.unload_extension(f"""modules.{name}""")
		
		active_modules.remove(name)
		self.conf.set_value("active_modules", active_modules)
		self.conf.save_json()

		await ctx.message.add_reaction("✅")
		
async def setup(bot):
	await bot.add_cog(Module(bot))