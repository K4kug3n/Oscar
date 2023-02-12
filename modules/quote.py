import random

from discord.ext import commands

from utils import load_csv
import logger

class Quote(commands.Cog):
	def __init__(self, bot : commands.Bot):
		self.bot = bot

	@commands.group()
	async def quote(self, ctx : commands.Context):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid quote command')

	@quote.command()
	async def say(self, ctx : commands.Context):
		try:
			quotes = load_csv("modules/quotes.csv")
			if len(quotes) > 0:
				await ctx.send(random.choice(quotes))
			else:
				await ctx.send("No quotes registered")
		except:
			logger.fail_message('[Quote] Error occured with say command')

async def setup(bot):
	await bot.add_cog(Quote(bot))