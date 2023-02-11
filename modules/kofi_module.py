import discord
import logger

from custom_message import get_customised_message

from config import Config
from database import Database

def init(config : Config, database : Database):
    if not config.get('active'):
       return True

    collection = config.get('collection')
    if collection == '' or collection == None:
        logger.fail_message("(Kofi module) Need collection in configuration")
        return False

    if config.get('channel_id') == None:
        logger.fail_message("(Kofi module) Need channel id in configuration")
        return False

    if database.get_one('messages', {'type' : 'kofi_transaction_message'}) == None:
        logger.fail_message("(Kofi module) Need transaction message (kofi_transaction_message) in database (collection : messages)")
        return False

    return True

def prepare_description(static_data : dict, runtime_data : dict, client : discord.ClientUser) -> str:
    needed_data = {
        'amount': runtime_data['amount'],
        'message': None
    }

    if runtime_data['is_public']:
        needed_data['buyer_name'] = runtime_data['from_name']        
    else:
        needed_data['buyer_name'] = "Un(e) inconnu(e)"

    if runtime_data['message'] != "":
        needed_data['message'] = runtime_data['message']

    return get_customised_message(static_data['description'], static_data['description_args'], client, needed_data)

def prepare_embed_message(static_data : dict, runtime_data : dict, client : discord.ClientUser):
    embded_msg = discord.Embed()
    embded_msg.title = "Transaction"
    embded_msg.color = 768255

    embded_msg.description = prepare_description(static_data, runtime_data, client)
    embded_msg.set_image(url=static_data['image_url'])    

    embded_msg.set_footer(text=runtime_data['timestamp'])

    return embded_msg

def prepare_log(transaction : dict) -> dict:
    log_data = {
        'name': transaction.get('from_name'),
        'email': transaction.get('email'),
        'date': transaction.get('timestamp'),
        'amount': transaction.get('amount')
    }

    return log_data

async def update(client : discord.ClientUser, config : Config, database : Database):
    transactions = database.get_all(config.get('collection'))
    if not transactions:
        return

    channel_id = config.get('channel_id')
    channel = client.get_channel(channel_id)
    if channel == None:
        logger.fail_message("(Kofi Module) " + str(channel_id) + " is not a valid channel id")
        return

    base_message = database.get_one('messages', {'type' : 'kofi_transaction_message'})

    for transaction in transactions:
        await channel.send(get_customised_message(base_message['introduction'], base_message['introduction_args'], client))
        await channel.send(embed=prepare_embed_message(base_message.copy(), transaction, client))

        database.insert_one('kofi_history', prepare_log(transaction))

        database.delete_one(config.get('collection'), transaction)