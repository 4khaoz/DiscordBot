import discord
from discord.ext import commands
import os

import music.player
import channel.channelmanager
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="!", help_command=None)

guild = 0
proto = 0


#
# EVENTS
#
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py Version: {discord.__version__}")

    global guild
    global proto

    global god_role
    global king_role

    guild = bot.get_guild(int(os.getenv('GUILDID')))
    proto = bot.get_channel(int(os.getenv('PROTOCOL')))

    god_role = discord.utils.find(lambda r: r.name == 'God', guild.roles)
    king_role = discord.utils.find(lambda r: r.name == 'King', guild.roles)

    bot.add_cog(music.player.Player(bot))
    bot.add_cog(channel.channelmanager.ChannelManager(bot))

    await bot.change_presence(activity=discord.Game("Nothing"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    await proto.send(f"Msg by {message.author.name} deleted:\n\"" + message.content + "\"")


@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        return

    if god_role in member.roles or king_role in member.roles:
        return

    if not (before.self_mute or before.self_deaf) and not (after.self_mute or after.self_deaf):
        a = ""
        b = ""
        if after.channel:
            a = f" joined {after.channel}."

        if before.channel:
            b = f" left {before.channel}."

        await proto.send(f"{member}{b}{a}")


@bot.command(pass_context=True, aliases=['h'])
async def help(ctx):
    target = ctx.author

    # EMBED
    embed = discord.Embed(
        title=f"{bot.user.name}'s Commands",
        description=f"Bot Commands for {bot.user.name} on the server {ctx.guild.name}",
        type="rich"
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/567471897282084875/662486195498123286/diaochan.jpg")
    embed.add_field(
        name="Play Music",
        value="***!play <arg>***\n"
              "Plays the Youtube Video (audio-only, cuz meant for Music). <arg> can be the title or URL",
        inline=False
    )
    embed.add_field(
        name="Stop Music",
        value="***!stop***\n"
              "Stops Music from Playing",
        inline=False
    )
    embed.add_field(
        name="Set Volume",
        value="***!volume <value>***\n"
              "Change the audio volume (value: 1-100)",
        inline=False
    )
    await target.send(embed=embed)


bot.run(os.getenv('DCTOKEN'), bot=True)
