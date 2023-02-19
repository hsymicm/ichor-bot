import discord
from discord import app_commands
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

  async def search(inp, *, loop=None, multiple=False):
    loop = loop or asyncio.get_event_loop()
    # Exctract information from url/search
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch1:{url}", download=not stream))
    if 'entries' in data:
      data = data['entries'][0]
    
    print(data)
    return data

  # Class method for processing video
  @classmethod
  async def from_url(cls, url, *, loop=None, stream=False):
    data = await self.search(url, loop)
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
def play_next(self, voice_client, queue):
  if queue.getLength() > 1:
    voice_client.stop()
    queue.delQueue(0)
    voice_client.play(queue.getSource(0), after = lambda e: play_next(self, voice_client, queue))
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
  
  @app_commands.command(name="listen", description="Listen to your favorite song!")
  @app_commands.describe(music="Input URL / Search")
  async def listen(self, interaction: discord.Interaction, music: str) -> None:
    if not await self.ensure_voice(interaction, True):
      return

    await interaction.response.defer()
    
    voice_channel = interaction.user.voice.channel
    
    if interaction.guild.voice_client is None:
      await voice_channel.connect()
    else:
      await interaction.guild.voice_client.move_to(voice_channel)

    voice_client = interaction.guild.voice_client
    
    # Start typing
    try:
      # Get audio source
      source = await YTDLSource.from_url(music, loop=self.client.loop, stream=True)

      # Sending Embed
      embed = discord.Embed(
        title=source.title, 
        url=source.url, 
        description="Requested by {}".format(interaction.user.display_name), 
        color=0xebd234)
      embed.set_author(name=source.channel)
      embed.set_image(url=source.thumbnail)

      await interaction.followup.send(embed=embed)

      # Appending audio source to queue
      try:
        self.queue[interaction.guild.id].addQueue(source)
      except:
        self.queue[interaction.guild.id] = player()
        self.queue[interaction.guild.id].addQueue(source)
        
      # Playing the source audio or adding to queue
      if not voice_client.is_playing():
        voice_client.play(self.queue[interaction.guild.id].getSource(0), after = lambda e: play_next(self, voice_client, self.queue[interaction.guild.id]))
      else:
        await interaction.channel.send("**Song added to the queue!** 📝")
            
    except Exception as err:
      await interaction.followup.send("**An error occurred, try requesting again.** 🚫")
      logger.exception(f"ERROR {err}")
      
  @app_commands.command(name="pause", description="Pause the current music.")
  async def pause(self, interaction: discord.Interaction) -> None:
    if not await self.ensure_voice(interaction):
      return
    interaction.guild.voice_client.pause()
    await interaction.response.send_message("**Pause** ⏸️")

  @app_commands.command(name="resume", description="Resume the paused music.")
  async def resume(self, interaction: discord.Interaction) -> None:
    if not await self.ensure_voice(interaction):
      return
    interaction.guild.voice_client.resume()
    await interaction.response.send_message("**Resume** ▶️")
    
  @app_commands.command(name="clear", description="Clear queue and stop the current music.")
  async def clear(self, interaction: discord.Interaction) -> None:
    if not await self.ensure_voice(interaction):
      return
    self.player.clearQueue()
    interaction.guild.voice_client.stop()
    await interaction.response.send_message("**Stopping** ⏹️")

  @app_commands.command(name="skip", description="Skip the current music.")
  async def skip(self, interaction: discord.Interaction) -> None:
    if not await self.ensure_voice(interaction):
      return
    interaction.guild.voice_client.stop()
    await interaction.response.send_message("**Skipping to the next song!** ⏯️")

  @app_commands.command(name="queue", description="Show every music in the queue.")
  async def queue(self, interaction: discord.Interaction) -> None:
    # Ensure client in voice channel
    if not await self.ensure_voice(interaction):
      return
    length = self.queue[interaction.guild.id].getLength()
    # If queue is empty
    if length == 0:
      embed=discord.Embed(title="Current Queue 📝", description="There's no queue at the moment! play a song.", color=0xebd234)  
    # If queue is not empty
    else:
      embed=discord.Embed(title="Current Queue 📝", color=0xebd234)
      # Iterates through queue
      for pos in range(length):
        source = self.queue[interaction.guild.id].getSource(pos)
        title = source.title
        link = source.url
        # Adding field based on position
        if pos == 0:
          embed.add_field(name=f"Now Playing", value=f"[{title}]({link})", inline=False)
        elif pos == 1:
          embed.add_field(name=f"Next Song", value=f"[{title}]({link})", inline=False)
        else:
          embed.add_field(name=f"Position - {pos+1}", value=f"[{title}]({link})", inline=False)
    await interaction.response.send_message(embed=embed)  
    
  @app_commands.command(name="current", description="Show the current music that is playing.")
  async def current(self, interaction: discord.Interaction) -> None:
    # Ensure client in voice channel
    if not await self.ensure_voice(interaction):
      return
    vc = interaction.guild.voice_client
    if not vc.is_playing():
      return await interaction.response.send_message("**An error occurred, the bot is currently not playing any song** 🚫")
    # Get information
    source = self.queue[interaction.guild.id].getSource(0)
    title = source.title
    url2 = source.url
    thumbnail = source.thumbnail
    # Sending embed
    embed = discord.Embed(title=title, url=url2, color=0xebd234)
    embed.set_author(name="Now Playing 🎵")
    embed.set_image(url=thumbnail)
    await interaction.response.send_message(embed=embed)

  @app_commands.command(name="leave", description="Disconnect the bot from voice channel")
  async def leave(self, interaction: discord.Interaction) -> None:
    try:
      if not await self.ensure_voice(interaction):
        return
      del self.queue[interaction.guild.id]
      interaction.guild.voice_client.stop()
      await interaction.guild.voice_client.disconnect()
      await interaction.response.send_message("**Dadah** 👋🏻")
    except Exception as err:
      logger.exception(f"ERROR {err}")

  async def ensure_voice(self, ctx, play=False):
    vc = ctx.guild.voice_client
    # Check if author is in a Voice Channel
    if ctx.user.voice is None:
      await ctx.response.send_message("**An error occurred, you're not in the voice channel** 🚫")
      return False
    elif (not vc or not vc.is_connected()) and not play:
      await ctx.response.send_message("**An error occurred, the bot is not in the voice channel** 🚫")
      return False
    else:
      return True
      
async def setup(client):
  await client.add_cog(music(client))