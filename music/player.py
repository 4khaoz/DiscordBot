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
    async def connect(self, ctx, channel: discord.VoiceChannel):
        """
        Connecting the bot to a Voice Channel
        """
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
    async def play(self, ctx, *arg: str):
        await self.connect(ctx, ctx.message.author.voice.channel)
        
        song = self.load_song(arg)
        self.voice_client.stop()
        
        # Sending Embed of Song
        embed = discord.Embed(
            title=f"Now Playing",
            description=f"{song.title}"
        )
        embed.set_thumbnail(url=song.thumbnail)
        await ctx.send(embed=embed)

        FFMPEG_OPTS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
        }

        self.voice_client.play(
            discord.FFmpegPCMAudio(song.source, **FFMPEG_OPTS), 
            after=lambda e: print(f"{song.title} has finished playing")
        )
        self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source, volume=self.voice_volume)

    def load_song(self, arg: str):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'no_warnings': True,
        }

        # Extract Youtube Video Data
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                if "https://" in arg:
                    info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
                else:
                    info = ydl.extract_info(arg[0], download=False)
            except:
                raise youtube_dl.utils.DownloadError('RIP')
            
            title = info['title']
            source = info['formats'][0]['url']
            url = "https://www.youtube.com/watch?v=" + info['id']
            thumbnail = info['thumbnail']

            return Song(title, url, source, thumbnail)

    @commands.command(pass_context=True)
    async def volume(self, ctx, args):
        try:
            vol = int(args)
            if vol < 1:
                vol = 1
            if vol > 100:
                vol = 100

            self.voice_volume = vol / 100
            print("Volume: " + str(self.voice_volume))

            self.voice_client.source.volume = self.voice_volume
            await ctx.send(f"Changed Volume to {vol}")
        except ValueError:
            print("Failed to change volume")
            return

    @commands.command(pass_context=True)
    async def leave(self, ctx):
        if self.voice and self.voice.is_connected():
            await ctx.send("See u next time")
            await self.voice.disconnect()