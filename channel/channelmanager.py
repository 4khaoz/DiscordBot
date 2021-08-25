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
        if before.channel is None:
            return

        if before.channel.name in self.chnls and len(before.channel.members) < 1:
            await before.channel.delete()
            del self.chnls[before.channel.name]

    @commands.command(pass_context=True)
    async def create(self, ctx, chname: str):
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

        channel = await ctx.guild.create_voice_channel(chname, overwrites=permissions)
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
    async def join(self, ctx, chname: str, pwd: str):
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