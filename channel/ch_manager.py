import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

bot = commands.Bot(command_prefix='#', help_command=None)

guild = 0
gaming = 0

@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name}")
  global guild
  global gaming

  guild = bot.get_guild(int(os.getenv('GUILDID')))
  gaming = bot.get_channel(int(os.getenv('GAMINGID')))
  
  print("ready")
  
  await bot.change_presence(activity=discord.Game("a chill game"))

@bot.event
async def on_voice_state_update(member, before, after):
  global guild
  global gaming

  if after.channel:
    bMove = False
    if after.channel.id == gaming.id:
      print("creating Gaming Channel")
      temp = await guild.create_voice_channel(
        'Group' + str(countTempChannels(0)), 
        category=discord.utils.get(guild.categories, id=int(os.getenv('CATEGORYID')))
      )
      bMove = True
    
    if bMove:
      await member.move_to(temp)

  if before.channel:
    bDelete = False
    if before.channel.name[0:5] == 'Group' and len(before.channel.members) < 1:
      bDelete = True
      print(f"deleting {before.channel.name}")
    
    if bDelete:
      await before.channel.delete()

def countTempChannels(mode: int):
  last_index = 0
  if mode == 0:
    for channel in guild.channels:
      if channel.name[0:5] == 'Group':
        last_index = int(channel.name[4])

  return last_index + 1

keep_alive()
bot.run(os.getenv('TOKEN'))
