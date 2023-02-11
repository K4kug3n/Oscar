import discord
import logger
import utils

def has_role(role : discord.Role, user : discord.User) -> bool:
    return user.roles.count(role) != 0

def has_role_by_name(role_name : str, user : discord.User) -> bool:
    searched_role = discord.utils.get(user.guild.roles, name=role_name)
    if searched_role == None:
        logger.fail_message("Error: Canno't find role '" + role_name + "'")
        return False

    return has_role(searched_role, user)

def has_role_by_id(role_id : int, user : discord.User) -> bool:
    searched_role = user.guild.get_role(role_id)
    if searched_role == None:
        logger.fail_message("Error: Canno't find role '" + str(role_id) + "'")
        return False

    return has_role(searched_role, user)

async def is_in_react(user : discord.Member, react : discord.Reaction) -> bool:
    users = await react.users().flatten()

    return user in users

def get_role_by_id(id : int, guild : discord.Guild) -> discord.Role:
    role = guild.get_role(id)
    if role == None:
        logger.fail_message("Error: Canno't find role with id '" + str(id) + "'")

    return role

def get_emoji_by_name(name : str, guild : discord.Guild) -> discord.Emoji:
    return discord.utils.get(guild.emojis, name=name)

def get_member_by_id(id : int, client : discord.Client) -> discord.Member:
    for member in client.get_all_members():
        if member.id == id:
            return member
    
    return None

async def get_message_by_ids(channel_id : int, message_id : int, client : discord.Client) -> discord.Message:
    channel = client.get_channel(channel_id)
    if channel == None:
        return None
    
    try:
        message = await channel.fetch_message(message_id)
        return message
    except discord.NotFound:
        return None

def extract_role_id(argument : str) -> str:
    prefix = '<@&'

    occurences_index = utils.find_all(argument, prefix)
    for i in occurences_index:
        role_id = ''

        i += len(prefix)
        while i < len(argument):
            if argument[i].isdigit():
                role_id += argument[i]
            elif argument[i] == '>':
                return role_id
            else:
                break
            i += 1
    
    return ''

def no_embed_link(link : str) -> str:
    return "<" + link + ">"