import requests
import time
import discord

import logger
from custom_message import get_customised_message
from discord_utils import no_embed_link

from config import Config
from database import Database
from bson.objectid import ObjectId

def older_than(lifetime : float):
    return time.time() > lifetime

def unchecked_code(code):
    return code != requests.codes['ok'] and code != 204

def get_updated_token(token : str, config : Config):
    r = requests.get(config.get("refresh_endpoint") + token)
    if unchecked_code(r.status_code):
        logger.fail_message(str(r.status_code) + " : " + r.text)
        return False, None, None

    data = r.json()

    return True, data["access_token"], data["expires_in"]

def update_token(current_token : dict, new_token : str, lifetime : float):
    current_token["token"] = new_token
    current_token["token_expires_date"] = time.time() + lifetime
    current_token["token_next_update_date"] = time.time() + lifetime * 0.8

def is_valid_token(token : dict, config : Config, database : Database):
    if older_than(token["token_expires_date"]):
        logger.fail_message("Token for " + token["hint_name"] + " is expired, need to be recreated")
        return False

    if older_than(token["token_next_update_date"]):
        logger.warning_message("Token for " + token["hint_name"] + " need to be updated")

        success, new_token, lifetime = get_updated_token(token["token"], config)
        if success:
            update_token(token, new_token, lifetime)

            if not database.replace_one(config.get('account_collection'), {'_id' : token['_id']}, token):
                logger.fail_message("Can't update database for " + token["hint_name"])
                return False

            logger.success_message("Update success")
            return True
        else:
            logger.fail_message("Can't update token for " + token["hint_name"])
            return False
    
    return True

def get_new_publications(publications : list[dict], last_id : str):
    new_publications = []

    for pub in publications:
        if pub["id"] != last_id:
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

def prepare_introduction_message(requested_data : dict, user_data : dict, client : discord.Client):
    if 'message' in user_data.keys():

        message_object = user_data['message']
        if not 'arguments' in message_object.keys() or message_object['arguments'] == []:
            return message_object['content'] + requested_data['permalink']

        return get_customised_message(message_object['content'], message_object['arguments'], client) + no_embed_link(requested_data['permalink'])
    else:
        return requested_data['permalink'] # Add link to the publication

def init(config : Config, database: Database):
    for token in database.get_all(config.get('account_collection')):
        need_save = False

        if token["token"] == "":
            logger.fail_message("One token is empty")
            return False
        elif token["channel_id"] == "":
            logger.fail_message("channel_id is empty for " + token["token"] + " (" + token["hint_name"] + ")")
            return False

        if token["token_expires_date"] == 0.0 or token["token_next_update_date"] == 0.0:
            success, new_token, lifetime = get_updated_token(token["token"], config)
            if success:
                update_token(token, new_token, lifetime)
                need_save = True
            else:
                logger.fail_message("Can't update the token " + token["token"] + " (" + token["hint_name"] + ")")
                return False

        if token["last_published_id"] == "":
            logger.warning_message("Getting id of last publication (" + token["hint_name"] + ")")
            r = requests.get(config.get("media_endpoint") + token["token"])
            if unchecked_code(r.status_code):
                logger.fail_message("Can't get data for the token : " + token["token"] + " (" + token["hint_name"] + ") :\n" + str(r.status_code) + " : " + r.text)
                return False

            data = r.json()['data']
            if data:
                token["last_published_id"] = data[0]["id"]
                need_save = True
            else:
                logger.fail_message("Can't get id of last publication (" + token['hint_name'] + ")")
                return False

        if need_save:
            logger.success_message("Save for " + token['hint_name'])
            if not database.replace_one(config.get('account_collection'), {'_id': token['_id']}, token):
                logger.fail_message("Can't update database for " + token['hint_name'])
                return False

    return True


async def update(client : discord.ClientUser, config : Config, database : Database):
    for token in database.get_all(config.get('account_collection')):
        if not is_valid_token(token, config, database):
            continue

        r = requests.get(config.get("media_endpoint") + token["token"])
        if unchecked_code(r.status_code):
            logger.fail_message("Can't get data for the token : " + token["token"] + " (" + token["hint_name"] + ") :\n" + str(r.status_code) + " : " + r.text)
            continue

        data = r.json()['data']

        new_publications = get_new_publications(data, token["last_published_id"])
        if not new_publications:
            continue
        elif len(new_publications) > 4: # One line + 1 post
            logger.fail_message("(Instagram_module) " + token["hint_name"] + " Warning : " + str(len(new_publications)) + " detected as need to be publish")
            logger.warning_message(str(new_publications))
            continue
    
        channel_id = token["channel_id"]
        channel = client.get_channel(channel_id)
        if channel == None:
            logger.fail_message(str(channel_id) + " is not a valid channel id")
            continue

        for publication in reversed(new_publications):
            logger.warning_message("Publishing : " + publication["id"])
            
            introduction_message = prepare_introduction_message(publication, token, client)
            embded_message = prepare_embded_pub(publication, token)
            try:
                await channel.send(introduction_message)
                await channel.send(embed=embded_message)
            except:
                logger.fail_message("Can't send message in channel " + str(channel_id))

        token["last_published_id"] = new_publications[0]["id"]

        if not database.replace_one(config.get('account_collection'), {'_id' : token['_id']}, token):
            logger.fail_message("Can't update database for " + token['hint_name'])
