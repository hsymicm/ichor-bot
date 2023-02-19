import discord
from discord.ext import commands
import asyncio
import yt_dlp as ydl
import time
import logging

# Logging config
logger = logging.getLogger('__name__')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] Function %(funcName)s - %(message)s')

file_handler = logging.FileHandler('logs/music.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Youtube downloder config
ydl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
  'format': 'bestaudio/best',
  'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
  'restrictfilenames': True,
  'noplaylist': False,
  'nocheckcertificate': True,
  'ignoreerrors': False,
  'logtostderr': False,
  'quiet': True,
  'no_warnings': True,
  'default_search': 'auto',
  'source_address': '0.0.0.0',
}

ytdl = ydl.YoutubeDL(ytdl_format_options)

# FFmpeg config
ffmpeg_options = {
  'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 3',
  'options': '-vn',
}

# Youtube downloader class
class YTDLSource(discord.PCMVolumeTransformer):
  def __init__(self, source, *, data, volume=0.5):
    super().__init__(source, volume)
    
    # Video information
    self.data = data
    self.url = data.get('url')
    self.title = data.get('title')
    self.channel = data.get('channel')
    self.thumbnail = data.get('thumbnail')

  # Class method for processing video
  @classmethod
  async def from_url(cls, url, *, loop=None, stream=False):
    loop = loop or asyncio.get_event_loop()
    # Exctract information from url/search
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch1:{url}", download=not stream))
    if 'entries' in data:
      data = data['entries'][0]
    filename = data['url'] if stream else ytdl.prepare_filename(data)
    # Returning object class
    return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Player 
class player():
  def __init__(self):
    self.source = []

  # Return queue length
  def getLength(self):
    return len(self.source)

  # Adding audio & information to queue
  def addQueue(self, source):
    self.source.append(source)

  # Delete audio & information based on given index
  def delQueue(self, index):
    del self.source[index]

  # Clear queue
  def clearQueue(self):
    self.source = []
    
  # Return audio based on given index
  def getSource(self, index):
    return self.source[index]

  # Return ALL information
  def getPlaylist(self):
    return self.source
    
# Play next song in queue
def play_next(self, ctx, queue):
  voice_client = ctx.voice_client
  if queue.getLength() > 1:
    voice_client.stop()
    queue.delQueue(0)
    voice_client.play(queue.getSource(0), after = lambda e: play_next(self, ctx, queue))
  else:
    # Bot time out auto disconnect
    time.sleep(120)
    try:
      if not voice_client.is_playing():
          asyncio.run_coroutine_threadsafe(voice_client.disconnect(), self.client.loop)
    except Exception as err:
      logger.error(f"INFO {err}")
          
class music(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.queue = {}
  
  @commands.command(name="play", aliases=['p', 'listen', 'sing', 'add'])
  async def play_(self,ctx, *, inp):
    # Check if author is in a Voice Channel
    if not await self.ensure_voice(ctx, True):
      return
    
    # Gets voice channel
    voice_channel = ctx.author.voice.channel

    # Move to author's Voice channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
    voice_client = ctx.voice_client

    # Start typing
    async with ctx.typing():
      try:
        # Get audio source
        source = await YTDLSource.from_url(inp, loop=self.client.loop, stream=True)
        title = source.title
        url2 = source.url
        username = source.channel
        thumbnail = source.thumbnail
        
        # Sending Embed
        embed = discord.Embed(title=title, url=url2, description="Requested by {}".format(ctx.author.display_name), color=0xebd234)
        embed.set_author(name=username)
        embed.set_image(url=thumbnail)
        await ctx.send(embed=embed)

        # Appending audio source to queue
        try:
          self.queue[ctx.guild.id].addQueue(source)
        except:
          self.queue[ctx.guild.id] = player()
          self.queue[ctx.guild.id].addQueue(source)
          
        # Playing the source audio or adding to queue
        if not voice_client.is_playing():
          voice_client.play(self.queue[ctx.guild.id].getSource(0), after = lambda e: play_next(self, ctx, self.queue[ctx.guild.id]))
        else:
          await ctx.send("**Song added to the queue!** 📝")
              
      except Exception as err:
        await ctx.send("**An error occurred, try requesting again.** 🚫")
        logger.exception(f"ERROR {err}")
      
  @commands.command(name="pause")
  async def pause_(self, ctx):
    if not await self.ensure_voice(ctx):
      return
    ctx.voice_client.pause()
    await ctx.send("**Pause** ⏸️")

  @commands.command(name="resume")
  async def resume_(self, ctx):
    if not await self.ensure_voice(ctx):
      return
    ctx.voice_client.resume()
    await ctx.send("**Resume** ▶️")
    
  @commands.command(name="clear", aliases=['clr', 'cls', 'stop', 'clean'])
  async def clear_(self,ctx):
    if not await self.ensure_voice(ctx):
      return
    self.player.clearQueue()
    ctx.voice_client.stop()
    await ctx.send("**Stopping** ⏹️")

  @commands.command(name="skip", aliases=['next', 'cont', 'ns'])
  async def skip_(self, ctx):
    if not await self.ensure_voice(ctx):
      return
    ctx.voice_client.stop()
    await ctx.send("**Skipping to the next song!** ⏯️")

  @commands.command(name="queue", aliases=['playlist', 'list', 'songs'])
  async def queue_(self, ctx):
    # Ensure client in voice channel
    if not await self.ensure_voice(ctx):
      return
    length = self.queue[ctx.guild.id].getLength()
    # If queue is empty
    if length == 0:
          embed=discord.Embed(title="Current Queue 📝", description="There's no queue at the moment! play a song.", color=0xebd234)  
    # If queue is not empty
    else:
      embed=discord.Embed(title="Current Queue 📝", color=0xebd234)
      # Iterates through queue
      for pos in range(length):
        source = self.queue[ctx.guild.id].getSource(pos)
        title = source.title
        link = source.url
        # Adding field based on position
        if pos == 0:
          embed.add_field(name=f"Now Playing", value=f"[{title}]({link})", inline=False)
        elif pos == 1:
          embed.add_field(name=f"Next Song", value=f"[{title}]({link})", inline=False)
        else:
          embed.add_field(name=f"Position - {pos+1}", value=f"[{title}]({link})", inline=False)
    await ctx.send(embed=embed)  
    
  @commands.command(name="current", aliases=['np', 'cs', 'now', 'song'])
  async def nowPlaying_(self, ctx):
    # Ensure client in voice channel
    if not await self.ensure_voice(ctx):
      return
    vc = ctx.voice_client
    if not vc.is_playing():
      return await ctx.send("**An error occurred, the bot is currently not playing any song** 🚫")
    # Get information
    source = self.queue[ctx.guild.id].getSource(0)
    title = source.title
    url2 = source.url
    thumbnail = source.thumbnail
    # Sending embed
    embed = discord.Embed(title=title, url=url2, color=0xebd234)
    embed.set_author(name="Now Playing 🎵")
    embed.set_image(url=thumbnail)
    await ctx.send(embed=embed)

  @commands.command(name="leave", aliases=['disconnect', 'dc', 'quit'])
  async def leave_(self, ctx):
    try:
      if not await self.ensure_voice(ctx):
        return
      del self.queue[ctx.guild.id]
      ctx.voice_client.stop()
      await ctx.voice_client.disconnect()
      await ctx.send("**Dadah** 👋🏻")
    except Exception as err:
      logger.exception(f"ERROR {err}")

  async def ensure_voice(self, ctx, play=False):
    vc = ctx.voice_client
    # Check if author is in a Voice Channel
    if ctx.author.voice is None:
      await ctx.send("**An error occurred, you're not in the voice channel** 🚫")
      return False
    elif (not vc or not vc.is_connected()) and not play:
      await ctx.send("**An error occurred, the bot is not in the voice channel** 🚫")
      return False
    else:
      return True
async def setup(client):
  await client.add_cog(music(client))