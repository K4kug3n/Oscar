import requests
import time
import discord

from discord.ext import commands, tasks

import logger
from custom_message import get_customised_message
from discord_utils import no_embed_link
from config import Config

def outdated(lifetime : float):
	return time.time() > lifetime

def unchecked_code(code):
	return code != requests.codes['ok'] and code != 204

def get_updated_token(token : str, config : Config):
	r = requests.get(config.get("refresh_endpoint") + token)
	if unchecked_code(r.status_code):
		logger.fail_message(f"""[Insta] {str(r.status_code)} : {r.text}""")
		return None, None

	data = r.json()

	return data["access_token"], data["expires_in"]

def update_token(acc : dict, config : Config):
	new_token, lifetime = get_updated_token(acc["token"], config)
	if not new_token:
		logger.fail_message(f"""[Insta] Can't update token for {acc["name"]}""")
		return False

	acc["token"] = new_token
	acc["token_expires_date"] = time.time() + lifetime
	acc["token_next_update_date"] = time.time() + lifetime * 0.8

	return True

def token_status(acc : dict):
	# Check if update needed, and if token_expires_date is expired (but differente than token_next_update_date, for default config)
	return outdated(acc["token_next_update_date"]), outdated(acc["token_expires_date"]) and (acc["token_expires_date"] != acc["token_next_update_date"])

def get_new_publications(publications : list[dict], posted : list[int]):
	new_publications = []

	for pub in publications:
		if not pub["id"] in posted:
			new_publications.append(pub)
		else:
			break
	
	return new_publications

def prepare_embded_pub(requested_data : dict, user_data : dict):
    embded_pub = discord.Embed()
    embded_pub.title = requested_data['username']
    embded_pub.color = 13500530

    if "caption" in requested_data:
        embded_pub.description = requested_data['caption'].split("#")[0]
    else:
        embded_pub.description = ""
    embded_pub.set_image(url=requested_data['media_url'])    

    embded_pub.set_footer(text=requested_data['timestamp'], icon_url="https://www.instagram.com/static/images/ico/xxhdpi_launcher.png/99cf3909d459.png")

    return embded_pub

def prepare_introduction_message(user_data : dict, bot : commands.Bot):
    if 'message' in user_data.keys():

        message_object = user_data['message']
        if not 'arguments' in message_object.keys() or message_object['arguments'] == []:
            return message_object['content']

        return get_customised_message(message_object['content'], message_object['arguments'], bot)
    else:
        return ""

class Instagram(commands.Cog):
	def __init__(self, bot : commands.Bot):
		self.bot = bot

		self.conf = Config()
		self.conf.load_json("configs/instagram.json")

		self.validate_config()

	def validate_config(self):
		accounts = self.conf.get("accounts")
		for acc in accounts:
			if not "token" in acc or acc["token"] == "":
				logger.fail_message("[Insta] No token")

			if not "channel_id" in acc:
				logger.fail_message("[Insta] No channel id")

			if not "token_expires_date" in acc:
				acc["token_expires_date"] = 0
			
			if not "token_next_update_date" in acc:
				acc["token_next_update_date"] = 0

			if not "published_ids" in acc:
				acc["published_ids"] = []

			if not "message" in acc or not "content" in acc["message"] or not "arguments" in acc["message"]:
				acc["message"] = { "content": "", "arguments": [] }

		self.conf.set_value("accounts", accounts)
		self.conf.save_json()

		if not self.conf.has("media_endpoint"):
			logger.fail_message("[Insta] No media endpoint")

		if not self.conf.has("refresh_endpoint"):
			logger.fail_message("[Insta] No refresh endpoint")

		self.publication_update.start()


	@tasks.loop(minutes=10.0)
	async def publication_update(self):
		accounts = self.conf.get("accounts")
		for acc in accounts:
			need_update, is_expired = token_status(acc)
			if is_expired:
				logger.fail_message(f"""[Insta] Expired token for {acc["name"]}""")
				continue

			if need_update:
				if not update_token(acc, self.conf):
					continue
				self.conf.save_json()
				
			r = requests.get(self.conf.get("media_endpoint") + acc["token"])
			if unchecked_code(r.status_code):
				logger.fail_message(f"""[Insta] Can't get data for the token : {acc["token"]} ({acc["name"]}):\n {str(r.status_code)} : {r.text}""")
				continue
				
			data = r.json()['data']

			new_publications = get_new_publications(data, acc["published_ids"])
			if not new_publications:
				continue
			# elif len(new_publications) > 4: # One line + 1 post
			# 	logger.warning_message(f"""[Insta] {acc["name"]} : {str(len(new_publications))} detected as need to be publish""")
			# 	logger.warning_message(str(new_publications))
			# 	continue
				
			channel_id = acc["channel_id"]
			channel = self.bot.get_channel(channel_id)
			if channel == None:
				logger.fail_message(f"""[Insta] {str(channel_id)} is not a valid channel id""")
				continue
			
			introduction_message = prepare_introduction_message(acc, self.bot)
			try:
				await channel.send(introduction_message)
			except:
				logger.fail_message(f"""[Insta] Can't send message in channel {str(channel_id)}""")
			
			
			for publication in reversed(new_publications):
				embded_message = prepare_embded_pub(publication, acc)
				try:
					await channel.send(no_embed_link(publication['permalink']))
					await channel.send(embed=embded_message)
				except:
					logger.fail_message(f"""[Insta] Can't send message in channel {str(channel_id)}""")

				logger.success_message(f"""[Insta] Published {publication["id"]} for {acc['name']}""")
				acc["published_ids"].append(publication["id"])

			if not self.conf.save_json():
				logger.fail_message(f"""[Insta] Can't update config file for {acc['name']}""")

	@publication_update.before_loop
	async def publication_update_before_bot(self):
		await self.bot.wait_until_ready()

async def setup(bot):
	await bot.add_cog(Instagram(bot))