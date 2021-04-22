from discord.ext import commands
import discord
import json
import random
import string
import os

class ChannelManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.chnls = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel.name in self.chnls and len(before.channel.members) < 1:
            await before.channel.delete()
            del self.chnls[before.channel.name]
            """
            # Delete Temporary Channel
            for channel in bot.get_guild(240621494437150744).channels:
                #if before.channel.name == 'temp' and before.channel.members == 0:
                if before.channel.name[0:4] == 'temp' and len(before.channel.members) < 1:
                    print(f"{channel} empty")
                    break
            """

    @commands.command(pass_context=True)
    async def createSecret(self, ctx, chname: str):
        if chname in self.chnls:
            await ctx.send("Channel already exists")
            return

        permissions = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
            ctx.guild.me: discord.PermissionOverwrite(connect=True)
        }
        characters = string.ascii_lowercase + string.digits
        pwd = ''.join(random.choice(characters) for i in range(8))
        print(pwd)

        self.chnls[chname] = pwd

        channel = await self.guild.create_voice_channel(chname, overwrites=permissions)
        if ctx.author.voice:
            await ctx.author.move_to(channel)

        embed = discord.Embed(
            title=f"Private Channel",
            description=f"Created Private-Channel: ***{chname}***\n"
                        f"Your Auto-Generated Password: ***{pwd}***",
            type="rich"
        )
        await ctx.author.send(embed=embed)

    @commands.command(pass_context=True)
    async def joinSecret(self, ctx, chname: str, pwd: str):
        await ctx.message.delete()

        if chname not in self.chnls:
            await ctx.send("Channel does not exist")
            return

        if not ctx.author.voice:
            await ctx.send("Please join a Voice-Channel to be eventually moved")
            return

        if (self.chnls[chname] == pwd):
            for channel in ctx.guild.channels:
                if channel.name == chname:
                    print(f"Moving {ctx.author} to {channel}")
                    await ctx.author.move_to(channel)

    """
    @commands.event
    async def on_voice_state_update(member, before, after):
        global guild
        global raid
        global dungeon
        if after.channel:
            bMove = False
            if after.channel.id == raid.id:
                print("creating Raid Channel")
                temp = await guild.create_voice_channel(
                    'Raid' + str(countTempChannels(0)), 
                    category=discord.utils.get(guild.categories, id=int(os.getenv('CATEGORYID')))
                )
                bMove = True
            if after.channel.id == dungeon.id:
                print("creating Dungeon Channel")
                temp = await guild.create_voice_channel(
                    'Dungeon' + str(countTempChannels(1)), 
                    category=discord.utils.get(guild.categories, id=int(os.getenv('CATEGORYID')))
                )
                bMove = True
            
            if bMove:
                await member.move_to(temp)

        if before.channel:
            bDelete = False
            if before.channel.name[0:4] == 'Raid' and len(before.channel.members) < 1:
                bDelete = True
                print(f"deleting {before.channel.name}")
            if before.channel.name[0:7] == 'Dungeon' and len(before.channel.members) < 1:
                bDelete = True
                print(f"deleting {before.channel.name}")
            
            if bDelete:
                await before.channel.delete()

    def countTempChannels(mode: int):
        last_index = 0
        if mode == 0:
            for channel in guild.channels:
                if channel.name[0:4] == 'Raid':
                    last_index = int(channel.name[4])
        if mode == 1:
            for channel in guild.channels:
                if channel.name[0:7] == 'Dungeon':
                    last_index = int(channel.name[7])

        return last_index + 1
    """