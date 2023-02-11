import discord
import asyncio

import logger

def calul_typing_time(msg : str) -> float:
    return len(msg) * 0.2

class InteractionModule:
    def __init__(self, client : discord.Client):
        self.client = client

    async def handle_command(self, command : str, args : list, message : discord.Message) -> bool:
        if command == 'say':
            await self.__say__command(args, message)
            return True
        elif command == 'react':
            await self.__react_command(args, message)
            return True

        return False

    async def __say__command(self, args, message):
        if (len(args) > 3) or (len(args) < 2):
            await message.channel.send("Wrong number of argument, usage : !say <channel id (optional)> <message>")
            return

        if len(args) == 3:
            try:
                target_channel_id = int(args[1])
                target_channel = self.client.get_channel(target_channel_id)
                if target_channel == None:
                    await message.channel.send("Can't find channel " + args[1] + ", command aborded, sowwy")
                    return

                async with target_channel.typing():
                    await asyncio.sleep(calul_typing_time(args[2]))
                    await target_channel.send(args[2])
            except ValueError:
                await message.channel.send("Can't find channel " + args[1] + ", command aborded, sowwy")
            except:
                logger.fail_message("Can't send " + args[2] + " in channel " + args[1])
        else:
            await message.channel.send(args[1])

    async def __react_help(self, channel):
        await channel.send("!react <channel ID> <message ID> <reaction>")

    async def __react_command(self, args, message):
        if len(args) != 4:
            await self.__react_help(message.channel)
            return

        channel = None
        try:
            channel_id = int(args[1])
            channel = self.client.get_channel(channel_id)
            if channel == None:
                await message.channel.send("Can't find channel " + args[1] + ", command aborded, sowwy")
                return
        except ValueError:
            await message.channel.send("Can't convert " + args[1] + " to valid ID, command aborded, sowwy")
            return

        message = None
        try:
            message_id = int(args[2])
            message = await channel.fetch_message(message_id)
        except ValueError:
            await message.channel.send("Can't convert " + args[2] + " to valid ID, command aborded, sowwy")
        except discord.NotFound:
            await message.channel.send("Can't find message with " + args[2] + " ID's in " + channel.name + ", command aborded, sowwy")


        try:
            await message.add_reaction(args[3])
        except discord.HTTPException as e:
            if e.code == 10014:
                message.channel.send("Can't find the emoji : " + args[3])
            else:
                logger.fail_message("Error : HHTP Exeception in react command")