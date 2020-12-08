import asyncio
import datetime
import json
import os
import random
import time
import unicodedata
from collections import defaultdict

import discord
from discord.ext import commands, menus
from discord.ext.commands.cooldowns import BucketType
from discord.utils import get
from utils import default, permissions


class HelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return '{0.clean_prefix}{1.qualified_name} {1.signature}'.format(self, command)

class HC(commands.Cog):
    """HC Cog by hatred#0041"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.save_data())
        self.queue = []
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self
        with open('data/hc/data.json', 'r') as f:
            self.data = json.load(f)

    async def save_data(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            with open('data/hc/data.json', 'w') as s:
                json.dump(self.data, s, indent=2)

            await asyncio.sleep(60)
            #print('saved')

    async def force_save(self):
        with open('data/hc/data.json', 'w') as s:
            json.dump(self.data, s, indent=2)

    @commands.Cog.listener()    
    async def on_raw_reaction_add(self, payload):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await self.bot.fetch_user(payload.user_id)
        _channel = await self.bot.fetch_channel(self.data["settings"]["judging"])
        submissions = await self.bot.fetch_channel(self.data["settings"]["submissions"])
        guild = channel.guild
        guild_id = str(channel.guild.id)
        emoji = payload.emoji
        ctx = await self.bot.get_context(message)
        _emoji = {"approved": "<a:approved:698226381288374342>", "denied": "<a:denied:698226411953061941>", "judging": "<:checkmark:698936269866270761>"}
        if user.bot:
            return
        #if str(message.id) not in self.data:
        #    return
        if str(emoji) not in _emoji.values():
            return
        else:
            if channel.id == submissions.id:
                #user_id = str(message.embeds[0].to_dict()["fields"][4]['value'])
                if str(emoji) == _emoji["approved"]:
                    self.data['data'][str(message.embeds[0].to_dict()["fields"][4]['value'])][f"{datetime.date.today()}"]["status"] = "Approved"
                    if self.queue:
                        self.queue.append(message.id)
                    else:
                        self.queue.append(message.id)
                        judge = await _channel.send("React to this message when you want to begin judging.")
                        await judge.add_reaction("checkmark:698936269866270761")
                elif str(emoji) == _emoji["denied"]:
                    self.data['data'][str(message.embeds[0].to_dict()["fields"][4]['value'])][f"{datetime.date.today()}"]["status"] = "Rejected"
                else:
                    print('unknown reaction')
            elif channel.id == _channel.id:
                if str(emoji) == _emoji["judging"]:
                    next_up = self.queue.pop(0)
                    msg = await submissions.fetch_message(next_up)
                    judge = await _channel.send(embed=msg.embeds[0])
                    await judge.add_reaction("a:approved:698226381288374342")
                    msg.embeds[0].set_field_at(index=2, name='Status', value='Approved', inline=False)
                    await judge.edit(embed=msg.embeds[0])
                elif str(emoji) == _emoji["approved"]:
                    user_id = str(message.embeds[0].to_dict()["fields"][4]['value'])
                    name = str(message.embeds[0].to_dict()["fields"][0]['value'])
                    msg_status = str(message.embeds[0].to_dict()["fields"][2]['value'])
                    rating = str(message.embeds[0].to_dict()["fields"][3]['value'])
                    #message.embeds[0].set_field_at(2, 'Status', 'Approved', False)
                    await ctx.send(f"What rating would you like to give {name} **({int(self.queue.index(message.id))+1}/{len(self.queue)})**")
                    try:
                        #await _channel(message.embeds[0].to_dict())
                        response = await self.bot.wait_for('message', timeout=1800.0)
                        rating = response.clean_content
                        self.data['data'][user_id][f"{datetime.date.today()}"]["rating"] = rating
                        message.embeds[0].set_field_at(3, 'Rating', rating, False)
                        await message.edit(embed=message.embeds[0])
                    except asyncio.TimeoutError:
                        return
                    await asyncio.sleep(3)
                    if self.queue:
                        print(self.queue)
                        next_up = self.queue.pop(0)
                        msg = await submissions.fetch_message(next_up)
                        judge = await _channel.send(embed=msg.embeds[0])
                        await judge.add_reaction("a:approved:698226381288374342")
                    else:
                        await _channel.send("There isn't anything else queued.")

    @commands.command(name='submit')
    @commands.cooldown(1, 60, BucketType.user)
    @commands.dm_only()
    async def submit(self, ctx, *, link):
        """Submit your edit for MitoHC"""
        _channel = await self.bot.fetch_channel(self.data["settings"]["submissions"])
        #dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        #tomorrow = datetime.date.today() + datetime.timedelta(days = 1) 
        wrap = "```py\n{}```"
        today = datetime.date.today()
        _id = str(ctx.author.id)
        if 'data' not in self.data:
            self.data['data'] = {}
        if _id in self.data['data']:
            if str(today) in self.data['data'][_id]:
                print('debug3')
                await ctx.send("You have already submitted an edit.")
                return
            else:
                print('debug2')
                self.create_set(ctx, _id, link)
                await ctx.send("Your edit has been submitted.")
        else:
            print('debug1')
            self.data['data'][_id] = {f"{datetime.date.today()}": {"name": ctx.author.name, "date": f"{datetime.date.today()}", "edit": link, "status": "Pending", "rating": "0.0"}}
            await ctx.send("Your edit has been submitted.")
        try:
            #colour=discord.Colour(0xf49595)
            embed = discord.Embed(colour=ctx.author.colour, url=f"{link}", timestamp=datetime.datetime.utcnow())
            embed.set_author(name=f"{str(ctx.author)}", url="https://discordapp.com", icon_url=ctx.author.avatar_url)
            embed.set_footer(text="Created by hatred#0041", icon_url="https://cdn.discordapp.com/attachments/133251234164375552/697541893034082344/186730658767437836.png")
            embed.add_field(name="Name:", value=f"{str(ctx.author.name)}", inline=True)
            embed.add_field(name="Edit", value=f"[Link]({link})", inline=True)
            embed.add_field(name="Status", value="Pending", inline=False)
            embed.add_field(name="Rating", value=0.0, inline=False)
            embed.add_field(name="ID", value=ctx.author.id, inline=False)
            msg = await _channel.send(embed=embed)
            await msg.add_reaction("a:approved:698226381288374342")
            await msg.add_reaction("a:denied:698226411953061941")
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=wrap.format(type(e).__name__ + ': ' + str(e)), colour=ctx.author.colour))

    @commands.group(name="hc")
    @commands.has_permissions(manage_roles=True)
    async def hc(self, ctx):
        """HC refrence command"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @commands.group(name="hcset")
    @commands.has_permissions(manage_roles=True)
    async def hcset(self, ctx):
        """HCSet refrence command"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @hcset.command(name='submissions')
    async def set_submissions(self, ctx, channel: discord.TextChannel):
        """Change the submissions channel."""
        self.data["settings"]["submissions"] = int(channel.id)
        await ctx.send("Channel set.")

    @hcset.command(name='judging')
    async def set_judging(self, ctx, channel: discord.TextChannel):
        """Change the judging channel."""
        self.data["settings"]["judging"] = int(channel.id)
        await ctx.send("Channel set.")

    @hc.command(name='save')
    async def hc_save(self, ctx, confirmation: bool = False):
        """Force save all data."""
        if confirmation is False:
            await ctx.send("This will force save all data.\nIf you're sure, type "
                    f"`{ctx.prefix}hc save yes`")
        else:
            await self.force_save()
            await ctx.send("Data saved.")

    @hc.command(name='open')
    async def hc_open(self, ctx, confirmation: bool = False):
        """Open HC submissinos."""
        if confirmation is False:
            await ctx.send("This will open submissions.\nIf you're sure, type "
                    f"`{ctx.prefix}hc open yes`")
        else:
            self.data["settings"]["closed"] = False
            await ctx.send("Submissions opened.")

    @hc.command(name='close')
    async def hc_close(self, ctx, confirmation: bool = False):
        """Close HC submissinos."""
        if confirmation is False:
            await ctx.send("This will close submissions.\nIf you're sure, type "
                    f"`{ctx.prefix}hc close yes`")
        else:
            self.data["settings"]["closed"] = True
            await ctx.send("Submissions closed.")

    @hc.command(name='reset')
    async def hc_reset(self, ctx, confirmation: bool = False):
        """Reset all data."""
        if confirmation is False:
            await ctx.send("This will reset all data.\nIf you're sure, type "
                    f"`{ctx.prefix}hc reset yes`")
        else:
            self.data['data'] = {}
            self.data["settings"]["submissions"] = {}
            self.data["settings"]["judging"] = {}
            self.data["settings"]["closed"] = {}
            await self.force_save()
            await ctx.send("Data reset.")

    @hc.command(name='debug')
    async def debug(self, ctx):
        """Debug command for developmental purpose."""
        await ctx.send(self.get_bot_data(ctx))
        paginator = commands.Paginator()
        for guild in ctx.bot.guilds:
            #await ctx.send(dir(guild))
            await ctx.send(f"debug: {guild}")

    def create_set(self, ctx, _id, link):
        _data = self.data['data'][_id]
        print(f"Before:\n{_data}")
        _data[f"{datetime.date.today()}"] = {"name": ctx.author.name, "date": f"{datetime.date.today()}", "edit": link, "status": "Pending", "rating": "0.0"}
        print(f"After:\n{_data}")

    def random_date(self, seed):
        random.seed(seed)
        d = random.randint(1, int(time.time()))
        return datetime.datetime.fromtimestamp(d).strftime('%Y-%m-%d')

    async def check_queue(self):
        _judging = await self.bot.fetch_channel(self.data["settings"]["judging"])
        print(_judging)
        submissions = await self.bot.fetch_channel(self.data["settings"]["submissions"])
        if self.queue:
            print(self.queue)
            next_up = self.queue.pop(0)
            msg = await submissions.fetch_message(next_up)
            judge = await _judging.send(embed=msg.embeds[0])
            await judge.add_reaction("a:approved:698226381288374342")
        else:
            await _judging.send("There isn't anything queued.")

    def get_bot_data(self, ctx):
        members = len([e.name for e in ctx.bot.get_all_members()])
        channels = len([e.name for e in ctx.bot.get_all_channels()]) 
        guilds = len(ctx.bot.guilds)
        dc = {"members": members, "channels": channels, "guilds": guilds}
        return dc

def check_folders():
    if not os.path.exists("data/hc"):
        print("Creating data/hc folder...")
        os.makedirs("data/hc")

def check_files():
    if not os.path.exists("data/hc/data.json"):
        print("Creating data/hc/data.json file...")
        with open('data/hc/data.json', 'w') as s:
                json.dump({}, s, indent=2)
        #jsonIO.save_json(filename="data/tickets/settings.json", data={})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(HC(bot))
