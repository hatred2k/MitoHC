import datetime
import sys
import traceback

import discord
from art import *
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from utils import default

config = default.get("config.json")

def get_bot_data(): 
    members = len([e.name for e in bot.get_all_members()])
    channels = len([e.name for e in bot.get_all_channels()]) 
    guilds = len(bot.guilds)
    dc = {"members": members, "channels": channels, "guilds": guilds}
    return dict(dc)

def get_prefix(bot, message):
    prefixes = config.prefix

    if not message.guild:
        return '!'

    return commands.when_mentioned_or(*prefixes)(bot, message)
#command_attrs=dict(hidden=True)
bot = commands.Bot(command_prefix=get_prefix, description='Mito HC Discord Bot by hatred#0041')
initial_extensions = [
    'cogs.owner',
    'utils.events', 
    'cogs.settings',
    'cogs.hc',
    'cogs.clash'
    ]

async def logout():
    await bot.logout()

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print(f'Loaded {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

@bot.event
async def on_ready():
    app_info = await bot.application_info()
    invite_url = discord.utils.oauth_url(app_info.id)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(name='!hc - @FaZeMito', type=1, url='https://twitch.tv/mito'))
    #print(texthopefully.encode('ascii'))
    tprint("Mito HC Bot")
    print(f'Logged in as: {bot.user.name} - {bot.user.id}\nInvite link: {invite_url}\n\nVersion: {discord.__version__}\nGuilds: {get_bot_data()["guilds"]}\nMembers: {get_bot_data()["members"]}\nChannels: {get_bot_data()["channels"]}')


bot.run(config.token, bot=True, reconnect=True)
start_time = datetime.datetime.utcnow()
