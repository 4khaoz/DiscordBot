from discord.ext import commands
from keep_alive import keep_alive
import discord
import os
import datetime
import string
import random

bot = commands.Bot(command_prefix="$")

# ID of private Channel
pch_id = int(os.getenv('CH_ID'))
passes = {}

@bot.event
async def on_ready():
    print('Logged in')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)


@bot.command(pass_context=True, aliases=['fp'])
async def friendpass(ctx, code):
    if not ctx.author.voice:
        await ctx.send('Please connect to a Voice Channel first')
        return

    if not code in passes:
        await ctx.send('Invalid code')
        return
    
    td = datetime.datetime.now() - passes[code]
    t = td.seconds // 3600
    print(t)
    if t > 2:
        passes.pop(code, None)
        await ctx.send('Friendpass expired')
    else:
        print('Moving Friend')
        await ctx.author.move_to(bot.get_channel(pch_id))


@bot.command(pass_context=True, aliases=['g'])
async def generate(ctx):
    if not ctx.author.voice:
        print('not connected to voice')
        return

    if ctx.author.voice.channel.id == pch_id:
        characters = string.ascii_lowercase + string.digits
        code = ''.join(random.choice(characters) for i in range(8))
        passes[code] = datetime.datetime.now()

        print(passes[code])

        embed = discord.Embed(
            title=f"FriendPass Code",
            description=f"Share this with your friends: ***$fp {code}***",
            type="rich"
        )
        await ctx.author.send(embed=embed)


keep_alive()
bot.run(os.getenv('TOKEN'), bot=True)
