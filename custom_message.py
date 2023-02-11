import discord
import logger

from discord_utils import get_role_by_id, get_member_by_id

def process_discord_arg(arg : dict, client : discord.Client) -> str:
    if 'DISCORD:ROLE' in arg['type']:
        role = get_role_by_id(arg['id_role'], client.guilds[0])
        if role == None:
           return ""

        if arg['type'] == 'DISCORD:ROLE:PING':
            return role.mention

    elif 'DISCORD:USER' in arg['type']:
        user = get_member_by_id(arg['id_user'], client)
        if user == None:
            return ""

        if arg['type'] == 'DISCORD:USER:PING':
            return user.mention

    elif 'DISCORD:CHANNEL' in arg['type']:
        channel = client.get_channel(arg['id_channel'])
        if channel == None:
            return ""

        if arg['type'] == 'DISCORD:CHANNEL:PING':
            return channel.mention


    logger.fail_message("Unknow arg's type : " + arg['type'])
    return ""

def process_optional_arg(arg : dict, runtime_args : dict) -> str:
    value = runtime_args[arg['value_name']]
    if value == None:
        return ""

    return arg['content'].format_map({ 'value': value })

def get_customised_message(content : str, raw_args : list, client : discord.Client, runtime_args : dict = {}) -> str:
    processed_args = {}
    for arg in raw_args:
        if 'DISCORD' in arg['type']:
            processed_args[arg['name']] = process_discord_arg(arg, client)
        elif 'OPTIONAL' in arg['type']:
            processed_args[arg['name']] = process_optional_arg(arg, runtime_args)
        else:
            logger.fail_message("Unknow arg's type : " + arg['type'])
    
    processed_args = processed_args | runtime_args

    return content.format_map(processed_args)