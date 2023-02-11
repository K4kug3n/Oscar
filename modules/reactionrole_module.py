import discord

from config import Config
from database import Database
import utils
import discord_utils
import logger

class ReactionroleModule:
    def __init__(self, client : discord.Client, config : Config, db : Database):
        self.config = config
        self.client = client
        self.db = db

    def is_actif(self):
        return self.config.get('active')

    async def handle_command(self, command : str, args : list, message : discord.Message) -> bool:
        if command == "reactionrole" or command == "rr":
            await self.__reactionrole_command(args, message)
            return True

        return False

    async def __reactionrole_help(self, channel : discord.TextChannel):
        await channel.send('!rr <channel ID> <message ID> <action> (role) (react) \n See doc or find dev for more infomations')

    async def __reactionrole_command(self, args : list, origin_message : discord.Message):
        if len(args) < 4 or len(args) > 6:
            await self.__reactionrole_help(origin_message.channel)
            return

        channel_id = utils.to_int(args[1])
        if channel_id == None:
            await origin_message.channel.send(args[1] + "is not a valid ID, try again")
            return
        message_id = utils.to_int(args[2])
        if message_id == None:
            await origin_message.channel.send(args[2] + "is not a valid ID, try again")
            return
        message = await discord_utils.get_message_by_ids(channel_id, message_id, self.client)
        if message == None:
            await origin_message.channel.send("There's no message with " + args[2] + " ID's in " + args[1] + " channel")
            return
        
        action = args[3]
        if action == 'clear':
            self.db.delete_one(self.config.get('collection'), {"channel_id": channel_id, "message_id": message_id})
            return

        message_obj = self.db.get_one(self.config.get('collection'), {"channel_id": channel_id, "message_id": message_id})
        if message_obj == None:
            message_obj = self.__init_model(channel_id, message_id)
            self.db.insert_one(self.config.get('collection'), message_obj)

        if action == 'uniq':
            message_obj['uniq'] = True
            self.db.replace_one(self.config.get('collection'), {"channel_id": channel_id, "message_id": message_id}, message_obj)
            return
        
        # Here say that args[4] is a Role
        if len(args) < 5:
            await self.__reactionrole_help(origin_message.channel)
            return

        str_role_id = discord_utils.extract_role_id(args[4])
        if str_role_id == '':
            await origin_message.channel.send("Can't extract role id from role ping of 4th parameter (from zero)")
            return
        role_id = utils.to_int(str_role_id)
        if role_id == None:
            await origin_message.channel.send("Extracted role ID is not valid")
            return

        role = discord_utils.get_role_by_id(role_id, self.client.guilds[0]) # MONO-GUILD ONLY
        if action == 'if':
            if message_obj.get('if_role_ids') == None:
                message_obj['if_role_ids'] = []
            message_obj['if_role_ids'].append(role.id)

            self.db.replace_one(self.config.get('collection'), {"channel_id": channel_id, "message_id": message_id}, message_obj)
            return

        # Here say that args[5] is a reaction
        if len(args) != 6:
            await self.__reactionrole_help(origin_message.channel)
            return

        reaction = args[5]

        action_type = None
        if action == "addrole":
            action_type = "ADD"
        elif action == "removerole":
            action_type = "REMOVE"
        else:
            await origin_message.channel.send('Unknow action "' + action + '", try again')
            return

        try:
            await message.add_reaction(reaction)
        except discord.HTTPException as e:
            if e.code == 10014:
                origin_message.channel.send("Can't find the emoji : " + reaction)
                return

        if message_obj['reactions_roles'].get(reaction) == None:
            message_obj['reactions_roles'][reaction] = []
        message_obj['reactions_roles'][reaction].append({ "type": action_type, "role_id": role.id })
        self.db.replace_one(self.config.get('collection'), {"channel_id": channel_id, "message_id": message_id}, message_obj)


    def __init_model(self, channel_id : int, message_id : int):
        data = {
            "channel_id": channel_id,
            "message_id": message_id,
            "reactions_roles": {}
        }

        return data

    async def __apply_uniq(self, current_react : discord.Reaction, member : discord.Member, message_obj : dict):
        for other_react in current_react.message.reactions:
            if other_react != current_react and (await discord_utils.is_in_react(member, other_react)):
                actions = message_obj['reactions_roles'].get(other_react.emoji)
                if actions == None:
                    continue
                for action in actions:
                    await self.__reverse_action(action, member)
                await other_react.remove(member)

    async def on_reaction_add(self, user : discord.Member, react : discord.Reaction):
        message_obj = self.db.get_one(self.config.get('collection'), {"channel_id": react.message.channel.id, "message_id": react.message.id}) ##CHECK
        if message_obj == None:
            return

        actions = message_obj['reactions_roles'].get(react.emoji)
        if actions == None:
            return

        is_uniq = message_obj.get('uniq')
        if is_uniq != None and is_uniq:
            await self.__apply_uniq(react, user, message_obj)
        
        if message_obj.get('if_role_ids') != None:
            for id in message_obj.get['if_role_ids']:
                if not discord_utils.has_role_by_id(id, user):
                    await react.remove(user)
                    return

        for action in actions:
            await self.__apply_action(action, user)

    async def on_reaction_remove(self, member : discord.Member, react : discord.Reaction):
        message_obj = self.db.get_one(self.config.get('collection'), {"channel_id": react.message.channel.id, "message_id": react.message.id}) ##CHECK
        if message_obj == None:
            return

        actions = message_obj['reactions_roles'].get(react.emoji)
        if actions == None:
            return

        for action in actions:
            await self.__reverse_action(action, member)

    async def __apply_action(self, action : dict, user : discord.Member):
        role = discord_utils.get_role_by_id(action['role_id'], self.client.guilds[0]) # MONO-GUILD ONLY
        if role == None:
            logger.fail_message('(Reactionrole) Error : Unknow role id registered, ' + action['role_id'])
            return

        if action['type'] == "ADD":
            await user.add_roles(role)
        elif action['type'] == "REMOVE":
            await user.remove_roles(role) #CHECK
        else:
            logger.fail_message('(Reactionrole) Error : Unknow active type registered, ' + action['type'])
    
    async def __reverse_action(self, action : dict, user : discord.Member):
        role = discord_utils.get_role_by_id(action['role_id'], self.client.guilds[0]) # MONO-GUILD ONLY
        if role == None:
            logger.fail_message('(Reactionrole) Error : Unknow role id registered, ' + action['role_id'])
            return

        if action['type'] == "ADD":
            await user.remove_roles(role) #CHECK
        elif action['type'] == "REMOVE":
            await user.add_roles(role)
        else:
            logger.fail_message('(Reactionrole) Error : Unknow active type registered, ' + action['type'])