from discord.ext import commands
import discord

class Interaction(commands.Cog):
	def __init__(self, bot : commands.Bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def say(self, _, channel: discord.TextChannel, text: str):
		await channel.send(text)

	@commands.command()
	@commands.has_permissions(administrator = True)
	async def react(self, ctx, channel: discord.TextChannel, msg_id: int, smiley):
		try:
			message = await channel.fetch_message(msg_id)

			await message.add_reaction(smiley)
		except discord.NotFound:
			await ctx.send(f"Can't find message with {msg_id} ID's in {channel.name}")            
		except discord.HTTPException as e:
			if e.code == 10014:
				ctx.send(f"Can't find the emoji : {smiley}")

async def setup(bot):
	await bot.add_cog(Interaction(bot))