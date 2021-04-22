from discord.ext import commands
from discord.utils import get
from .song import Song
import asyncio
import discord
import youtube_dl

class Player(commands.Cog):

    def __init__(self, bot):
        self.voice_client = None
        self.voice_volume = 0.1
        self.is_playing = False
        self.bot = bot

    @commands.command()
    async def connect(self, channel: discord.VoiceChannel):
        if self.voice_client is None:
            self.voice_client = await channel.connect()
            await ctx.send(f"Joined {channel}")
        
        # Already connected and in the right channel
        if self.voice_client.channel == channel and self.voice_client.is_connected():
            return

        # Stop Voice if moving
        if self.voice_client:
            await self.voice_client.stop()

        # Move Voice
        if self.voice_client.is_connected():
            await self.voice_client.move_to(channel)
        
        await ctx.send(f"Joined {channel}")

    @commands.command(pass_context=True)
    async def play(self, ctx, url: str):
        #self.voice_client = get(self.bot.voice_clients, guild=ctx.guild)
        await self.connect(ctx.message.author.voice.channel)
        await ctx.send("Preparing music...")

        song = self.load_song(url)
        self.voice_client.stop()
        
        await ctx.send(f"Playing: {song.title}")

        FFMPEG_OPTS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
        }

        self.voice_client.play(
            discord.FFmpegPCMAudio(song.source, **FFMPEG_OPTS), 
            after=lambda e: print(f"{song.title} has finished playing")
        )
        self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source, volume=0.1)

        #await discord.Embed

    def load_song(self, url: str):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
            'restrictfilenames': True,
            'noplaylist': 'True',
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'no_warnings': True,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise DownloadError('RIP')
            
            title = info['title']
            source = info['formats'][0]['url']

            return Song(title, url, source)

    @commands.command(pass_context=True)
    async def volume(self, ctx, args):
        try:
            vol = int(args)
            if vol < 1:
                vol = 1
            if vol > 100:
                vol = 100

            self.voice_volume = vol / 100
            print("Volume: " + str(voice_volume))

            self.voice_client.source.volume = self.voice_volume
            await ctx.send(f"Changed Volume to {vol}")
        except ValueError:
            print("Failed to change volume")
            return


    @commands.command(pass_context=True)
    async def leave(ctx):
        if voice and voice.is_connected():
            await ctx.send("See u next time")
            await voice.disconnect()