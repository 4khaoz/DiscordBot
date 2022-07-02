from discord.ext import commands
from .song import Song, SongQueue
import discord
import youtube_dl


class Player(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.voice_client = None
        self.voice_volume = 0.1
        self.is_playing = False
        self.bot = bot
        self.queue = SongQueue()

    @commands.command()
    async def connect(self, ctx: commands.Context, channel: discord.VoiceChannel):
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
    async def play(self, ctx: commands.Context, *arg: str):
        await self.connect(ctx, ctx.message.author.voice.channel)

        self.queue.addSongToQueue(self.__load_song(arg))

        if not self.is_playing:
            await self.__playSong(ctx)
        else:
            await ctx.send("Added song to Queue")

    async def __playSong(self, ctx: commands.Context):
        if not self.queue.queue:
            self.is_playing = False
            return

        song = self.queue.getNextSong()
        self.is_playing = True

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
            after=lambda e: self.__playNextSong(ctx, e)
        )
        self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source, volume=self.voice_volume)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        self.voice_client.stop()
        self.__playNextSong(ctx, 0)

    def __playNextSong(self, ctx: commands.Context, e):
        """
        Function to create asyncio task to play the next song
        Called in playSong() through lambda
        """
        task = self.__playSong(ctx)

        self.bot.loop.create_task(task)

    @staticmethod
    def __load_song(arg: str):
        ydl_opts = {
            'format': 'bestaudio/best',
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
                if "https://" not in arg[0]:
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
    async def volume(self, ctx: commands.Context, args: int):
        try:
            vol = args
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
    async def leave(self, ctx: commands.Context):
        if self.voice_client and self.voice_client.is_connected():
            await ctx.send("See u next time")
            await self.voice_client.disconnect()

    @commands.command()
    async def queue(self, ctx: commands.Context):
        if not self.queue.queue:
            await ctx.send("Queue is empty")
            return

        # Sending Embed of Queue
        embed = discord.Embed(
            title=f"Songs in Queue"
        )
        for song in self.queue.queue:
            embed.add_field(
                name=song.title,
                value=song.url,
                inline=False
            )
        await ctx.send(embed=embed)
