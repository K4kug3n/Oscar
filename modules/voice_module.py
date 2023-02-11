import discord
import logger
import random
import asyncio
from enum import Enum, auto

from config import Config

class VoiceModuleEvent(Enum):
    Join = auto()
    Quit = auto()
    Ping = auto()
    
class VoiceModule:
    def __init__(self, client : discord.Client, config : Config):
        self.config = config
        self.client = client
        self.voice_client = None

    def is_valid(self):
        if not self.is_actif():
            return True

        on_join = self.config.get('on_join')
        if on_join['active']:
            exit

        on_quit = self.config.get('on_quit')
        if on_quit['active']:
            exit

        on_ping = self.config.get('on_ping')
        if on_ping['active']:
            exit

        return True

    def is_actif(self):
        return self.config.get('active')

    def is_connected(self):
        return self.voice_client != None

    async def mute(self, state=True):
        if self.is_connected():
            await self.client.guilds[0].change_voice_state(channel=self.voice_client.channel, self_mute=state) # MONO-GUILD ONLY

    def is_mute(self):
        return self.voice_client.channel.voice_states[self.client.user.id].self_mute

    def is_playing(self):
        return self.voice_client.is_playing()

    async def wait_until_silent(self):
        while self.is_playing():
            await asyncio.sleep(1)

    def __play_file(self, file : str, after_callback=None):
        filepath = self.config.get('folder') + '/' + file
        audio_source = discord.FFmpegOpusAudio(filepath, executable=self.config.get('exec'), options='-loglevel panic')

        self.voice_client.play(audio_source, after=after_callback)

    async def handle_event(self, event : VoiceModuleEvent):
        if not self.is_connected():
            return
        
        if event == VoiceModuleEvent.Join:
            await self.__on_event('on_join')
        elif event == VoiceModuleEvent.Quit:
            await self.__on_event('on_quit')
        elif event == VoiceModuleEvent.Ping:
            await self.__on_event('on_ping')

    async def handle_command(self, command, args, message):
        if command == 'join':
            await self.__join_command(args, message)
            return True
        elif command == 'quit':
            await self.__quit_command(message.channel)
            return True
        elif command == 'play':
            await self.__play_command(args, message)
            return True

        return False

    async def __play_help(self, channel):
        await channel.send('!play <name file>.<extension>')

    async def __play_command(self, args, message):
        if len(args) != 2:
            await self.__play_help(message.channel)
            return
        elif not self.is_connected():
            await message.channel.send("I must be connected to a voice channel before play, wtf")
            return

        if self.is_mute():
            await self.mute(False)

        self.__play_file(args[1])

    async def __join_help(self, channel):
        await channel.send("!join")

    async def __join_command(self, args, message):
        if len(args) > 2:
            await self.__join_help(message.channel)
            return
        elif self.is_connected():
            await message.channel.send("I'm only one guy, how can I be in 2 place at same time ? (quantum not allowed)")
            return

        channel = None
        if len(args) == 1:
            voice_module = message.author.voice
            if voice_module == None:
                await message.channel.send("You must be connected to a voice channel, try again")
                return

            channel = voice_module.channel
        else:
            try:
                channel_id = int(args[1])

                channel = self.client.get_channel(channel_id)
                if channel == None:
                    await message.channel.send("Can't find channel " + args[1] + ", sowwy")
                    return
                elif channel.type == discord.ChannelType.text:
                    await message.channel.send(channel.name + " is a text channel, wtf ?")
                    return

            except ValueError:
                await message.channel.send("Can't convert " + args[1] + " to valid ID, command aborded, sowwy")
                return
    
        if channel != None:
            self.voice_client = await channel.connect()
            await self.mute()

            await self.handle_event(VoiceModuleEvent.Join)

    async def __quit_command(self, channel):
        if not self.is_connected():
            await channel.send("I must be connected to a voice channel before quit, wtf")
            return

        await self.handle_event(VoiceModuleEvent.Quit)
        await self.wait_until_silent()

        await self.voice_client.disconnect()
        self.voice_client = None

    def __process_custom_sound(self, custom_sound_data : dict):
        if custom_sound_data['type'] == 'SINGLE':
            return [ custom_sound_data['name'] ]
        if custom_sound_data['type'] == 'RANDOM':
            return [ random.choice(custom_sound_data['names']) ]

        logger.fail_message('(VoiceModule) Unknow custom sound type : ' + custom_sound_data['type'])

        return None

    async def __on_event(self, event_name : str):
        on_event_data = self.config.get(event_name)
        if on_event_data['active'] == False:
            return
        
        sound_names = self.__process_custom_sound(on_event_data)
        if sound_names == None:
            return

        if self.is_mute():
            await self.mute(False)
        
        for name in sound_names:
            self.__play_file(name)
            await self.wait_until_silent()

        await self.mute()
