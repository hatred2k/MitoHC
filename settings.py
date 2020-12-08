import discord
from discord.ext import commands
import yaml
import os

class Settings(commands.Cog):
    """Settings Cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="set", hidden=True)
    @commands.is_owner()
    async def set(self, ctx):
        "Set refrence command"
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @set.command(name='token', hidden=True)
    async def set_token(self, ctx, token):
        """Change the bot token."""
        dataIO.change_value("config.json", "token", token)
        await ctx.send('Token changed.')

    @set.command(name='prefix', hidden=True)
    async def set_prefix(self, ctx, prefix):
        """Change the bot prefix."""
        dataIO.change_value("config.json", "prefix", prefix)
        await ctx.send('Prefix changed.')

    @set.command(name='game', hidden=True)
    async def set_game(self, ctx, *, game):
        """Change the playing status of the bot."""
        members = len([e.name for e in ctx.bot.get_all_members()])
        channels = len([e.name for e in ctx.bot.get_all_channels()]) 
        guilds = len(ctx.bot.guilds)
        await ctx.bot.change_presence(activity=discord.Activity(name=f'{game} | {members} users on {guilds} guilds', type=1, url='https://twitch.tv/hatred2k'))
        dataIO.change_value("config.json", "streaming", game)
        await ctx.send('Game set.')

    def get_bot_data(self, ctx):
        members = len([e.name for e in ctx.bot.get_all_members()])
        channels = len([e.name for e in ctx.bot.get_all_channels()]) 
        guilds = len(ctx.bot.guilds)
        return dict(members, guilds, channels)

        
def setup(bot):
    bot.add_cog(Settings(bot))