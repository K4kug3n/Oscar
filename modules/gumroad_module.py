import discord
import logger
import requests

from utils import HTMLFilter
from custom_message import get_customised_message

from config import Config
from database import Database

def init(config : Config, database : Database):
    if not config.get('active'):
       return True

    transaction_collection = config.get('transaction_collection')
    if transaction_collection == '' or transaction_collection == None:
        logger.fail_message("(Gumroad module) Need transaction_collection in configuration")
        return False

    published_product_collection = config.get('published_product_collection')
    if published_product_collection == '' or published_product_collection == None:
        logger.fail_message("(Gumroad module) Need published_product_collection in configuration")
        return False

    # if config.get('transaction_channel_id') == None:
    #     logger.fail_message("(Gumroad module) Need transation channel id in configuration")
    #     return False

    if config.get('product_channel_id') == None:
        logger.fail_message("(Gumroad module) Need product channel id in configuration")
        return False

    # if database.get_one('messages', {'type' : 'gumroad_transaction_message'}) == None:
    #     logger.fail_message("(Gumroad module) Need transaction message (gumroad_transaction_message) in database (transaction_collection : messages)")
    #     return False

    return True

# def prepare_transaction_price(raw_price : str) -> str :
#     return raw_price[:-2] + ',' + raw_price[-2:]

# def prepare_transaction_description(static_data : dict, runtime_data : dict, client : discord.ClientUser) -> str:
#     needed_data = {
#         'product_name' : runtime_data['product_name'],
#         'link' : runtime_data['product_permalink'],
#         'email' : runtime_data['email'],
#         'price' : prepare_transaction_price(str(runtime_data['price']))
#     }

#     return get_customised_message(static_data['description'], static_data['description_args'], client, needed_data)

# def prepare_transation_embed_message(static_data : dict, runtime_data : dict, client : discord.ClientUser):
#     embded_msg = discord.Embed()
#     embded_msg.title = "Transaction"
#     embded_msg.color = 5701376

#     embded_msg.description = prepare_transaction_description(static_data, runtime_data, client)
#     embded_msg.set_image(url=static_data['image_url'])    

#     embded_msg.set_footer(text=runtime_data['sale_timestamp'])

#     return embded_msg

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

# async def transaction_update(client : discord.ClientUser, config : Config, database : Database):
#     transactions = database.get_all(config.get('transaction_collection'))
#     if not transactions:
#         return

#     transaction_channel_id = config.get('transaction_channel_id')
#     transaction_channel = client.get_channel(transaction_channel_id)
#     if not transaction_channel:
#         logger.fail_message("(Gumroad Module) " + str(transaction_channel_id) + " is not a valid channel id")
#         return

#     base_message = database.get_one('messages', {'type' : 'gumroad_transaction_message'})

#     for transaction in transactions:
#         await transaction_channel.send(get_customised_message(base_message['introduction'], base_message['introduction_args'], client))
#         await transaction_channel.send(embed=prepare_transation_embed_message(base_message.copy(), transaction, client))

#         database.delete_one(config.get('transaction_collection'), transaction)

async def product_update(client : discord.ClientUser, config : Config, database : Database):
    r = requests.get(config.get("endpoint"))
    if r.status_code != requests.codes['ok'] and r.status_code != 204:
        logger.fail_message("(Gumroad Module) Failed to retrive product list")
        return

    data = r.json()
    if data["success"] == False:
        logger.fail_message("(Gumroad Module) Request didn't succed")
        return

    products = data["products"]

    published_products = database.get_all(config.get("published_product_collection"))
    published_id = [ product["id"] for product in published_products ]

    product_channel_id = config.get('product_channel_id')
    product_channel = client.get_channel(product_channel_id)
    if not product_channel:
        logger.fail_message("(Gumroad Module) " + str(product_channel_id) + " is not a valid channel id")
        return

    for product in products:
        if product["published"] == False:
            logger.warning_message(" (Gumroad Module) Not published : {} ({})".format(product["id"], product["name"]))
            continue

        if not product["id"] in published_id:
            logger.success_message("(Gumroad Module) New ID : {} ({})".format(product["id"], product["name"]))

            introduction_message = prepare_introduction_embed_message(client)
            embed_message = prepare_product_embed_message(product)

            database.insert_one(config.get("published_product_collection"), {"id": product["id"], "name": product["name"]} )

            try:
                await product_channel.send(introduction_message)
                await product_channel.send(embed=embed_message)
            except discord.HTTPException as e:
                logger.fail_message("(Gumroad Module) HTTPException : " + e.text)
            except:
                logger.fail_message("(Gumroad Module) Can't send message in channel " + str(product_channel_id))
        

async def update(client : discord.ClientUser, config : Config, database : Database):
    #await transaction_update(client, config, database)
    await product_update(client, config, database)