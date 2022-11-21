import discord
from discord.ext import commands
from sys_info import *


# misc
pfp = 'https://media.discordapp.net/attachments/880704270838669325/975661475333013554/ProfilePicturePhoto.png?width=682&height=682'

def stripes(n):
  stripe = ""
  for i in range(0,n):
    stripe += "_"
  return stripe

class misc(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.yellow = 0xebd234

  @commands.command()
  async def stats(self, ctx):
    embed=discord.Embed(title="Status Bot", description="Monitoring resource, versi API, dll.", color=self.yellow)
    embed.add_field(name=stripes(50), value='\u200b', inline=False)
    embed.add_field(name="CPU", value=f"```{cpu_model}```", inline=False)
    embed.add_field(name=stripes(50), value='\u200b', inline=False)
    embed.add_field(name="Speed", value=cpu_speed[0:4] + " GHz", inline=True)
    embed.add_field(name="Cores", value=thread_count, inline=True)
    embed.add_field(name="CPU Usage", value=cpu_usage, inline=True)
    embed.add_field(name="Architecture", value=arch, inline=True)
    embed.add_field(name="RAM", value=mem_total, inline=True)
    embed.add_field(name="RAM Usage", value=mem_usage, inline=True)
    embed.add_field(name=stripes(50), value='\u200b', inline=False)
    embed.add_field(name="Discord.py", value=discord_py, inline=True)
    embed.add_field(name="Python ", value=ver, inline=True)
    embed.add_field(name="OS", value=os, inline=True)
    await ctx.send(embed=embed)
    
  @commands.group(invoke_without_command=True)
  async def help(self,ctx):
    if ctx.invoked_subcommand is None:
      embed=discord.Embed(
        title="Help Category & Other",
        color=self.yellow
      )
      embed.set_author(name="Help Page")
      embed.add_field(name="Prefix Bot", value="```> ```", inline=False)
      embed.add_field(name='Music Player', value="```>help music```", inline=True)
      embed.add_field(name='Genshin Impact', value="```>help genshin```", inline=True)
      embed.add_field(name='Anime List', value="```>help anime```", inline=True)
      embed.add_field(name='Help', value='```>help```', inline=True)
      embed.add_field(name='Status', value='```>stats```', inline=True)
      await ctx.send(embed=embed)

  @help.command(name='music')
  async def _music(self, ctx):
    embed=discord.Embed(
      title="Music Player Commands",
      color=self.yellow
    )
    embed.add_field(name="Prefix Bot", value="```> ```", inline=False)
    embed.add_field(name='Search', value="```>p {YT}```", inline=True)
    embed.add_field(name='Pause', value="```>pause```", inline=True)    
    embed.add_field(name='Resume', value="```>resume```", inline=True)
    embed.add_field(name='Stop', value="```>stop```", inline=True)
    embed.add_field(name='Skip', value="```>skip```", inline=True)
    embed.add_field(name='Leave', value="```>leave```", inline=True)
    await ctx.send(embed=embed)

  @help.command(name='genshin')
  async def _genshin(self, ctx):
    embed=discord.Embed(
      title="Genshin Impact Commands",
      color=self.yellow
    )
    embed.add_field(name="Prefix Bot", value="```> ```", inline=False)
    embed.add_field(name='Character List', value="```>wish list```", inline=True)
    embed.add_field(name='Wish Simulator', value="```>wish {Character}```", inline=True)
    embed.add_field(name='Wish Inventory', value="```>wish inventory```", inline=True)
    embed.add_field(name='Genshin Wiki', value="```>g {Weapon Name}```", inline=True)  
    await ctx.send(embed=embed)

  @help.command(name='otaku', aliases=['jpn', 'japanese', 'media'])
  async def _media(self, ctx):
    embed=discord.Embed(
      title="Otaku Commands",
      color=self.yellow
    )
    embed.add_field(name="Prefix Bot", value="```> ```", inline=False)
    
    embed.add_field(name="Anime Watchlist", value="```>mylist       ```", inline=True)
    embed.add_field(name="Add Watchlist", value="```>mylist add [name]```", inline=True)
    embed.add_field(name="Remove Watchlist", value="```>mylist remove   ```", inline=True)
    embed.add_field(name='Search Anime', value="```>search anime [name]```", inline=True)
    embed.add_field(name='Search Light Novel', value="```>search ln [name]```", inline=True)
    embed.add_field(name='Anime Schedule', value="```>schedule    ```", inline=True)
    await ctx.send(embed=embed)
    
def setup(client):
  client.add_cog(misc(client))