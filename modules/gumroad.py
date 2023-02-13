import discord
import logger
import requests
from discord.ext import commands, tasks

from utils import HTMLFilter
from custom_message import get_customised_message

from config import Config

def prepare_product_embed_message(product):
	embded_prod = discord.Embed()
	embded_prod.url=product['short_url']
	embded_prod.title = product['name']
	embded_prod.color = 15277667

	descriptionFilter = HTMLFilter()
	descriptionFilter.feed(product['description'])

	embded_prod.description = descriptionFilter.text
	embded_prod.set_image(url=product['preview_url'])

	embded_prod.set_footer(text=product['formatted_price'])

	return embded_prod

def prepare_introduction_embed_message(client : discord.ClientUser):
	return get_customised_message("{ping}", [{"name": "ping", "type": "DISCORD:ROLE:PING", "id_role": 800672409379405855}], client)

class Gumroad(commands.Cog):
	def __init__(self, bot : commands.Bot):
		self.bot = bot

		self.conf = Config()
		self.conf.load_json("configs/gumroad.json")

		self.validate_config()

	def validate_config(self):
		accounts = self.conf.get("accounts")
		for acc in accounts:
			if not "token" in acc or acc["token"] == "":
				logger.fail_message("[Gumroad] No token")

			if not "product_channel_id" in acc:
				logger.fail_message("[Gumroad] No product_channel_id")

			if not "published_ids" in acc:
				acc["published_ids"] = []

		self.conf.set_value("accounts", accounts)
		self.conf.save_json()

		if not self.conf.has("endpoint"):
			logger.fail_message("[Gumroad] No endpoint")

		self.product_update.start()


	@tasks.loop(minutes=30.0)
	async def product_update(self):
		accounts = self.conf.get("accounts")
		for acc in accounts:
			r = requests.get(self.conf.get("endpoint") + acc["token"])
			if r.status_code != requests.codes['ok'] and r.status_code != 204:
				logger.fail_message("[Gumroad] Failed to retrive product list")
				return

			data = r.json()
			if not data["success"]:
				logger.fail_message("[Gumroad] Request didn't succed")
				return

			products = data['products']

			product_channel = self.bot.get_channel(acc['product_channel_id'])
			if not product_channel:
				logger.fail_message(f"""[Gumroad] {str(acc['product_channel_id'])} is not a valid channel id""")
				return

			for product in products:
				if product["published"] == False:
					logger.warning_message(f"""[Gumroad] Not published : {product["id"]} ({product["name"]})""")
					continue

				if not product["id"] in acc['published_ids']:
					acc['published_ids'].append(product["id"])
					logger.success_message("[Gumroad] New ID : {} ({})".format(product["id"], product["name"]))

					introduction_message = prepare_introduction_embed_message(self.bot)
					embed_message = prepare_product_embed_message(product)

					try:
						await product_channel.send(introduction_message)
						await product_channel.send(embed=embed_message)
					except discord.HTTPException as e:
						logger.fail_message("[Gumroad] HTTPException : " + e.text)
					except:
						logger.fail_message(f"""[Gumroad] Can't send message in channel {str(acc['product_channel_id'])}""")

			if not self.conf.save_json():
				logger.fail_message(f"""[Insta] Can't update config file for {acc['name']}""")

	@product_update.before_loop
	async def product_update_before_bot(self):
		await self.bot.wait_until_ready()

async def setup(bot):
	await bot.add_cog(Gumroad(bot))