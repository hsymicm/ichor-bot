import discord
from discord.ext import commands
import asyncio
import time

from tictactoe_game.tictactoe import Tictactoe

class tictactoegame(commands.Cog):
  def __init__(self, client, tictactoe):
    self.client = client
    self.session = tictactoe    
    self.yellow = 0xebd234
    self.author = "Playing Tictactoe"

  def loadingEmbed(self):
    embed = discord.Embed(
      title='Loading...',
      color=self.yellow
    )
    embed.set_author(name=self.author)
    return embed
    
  @commands.command(name='ttt')
  async def _tictactoe(self, ctx):
    img = self.session.getBoard()
    embed = discord.Embed(
      title="Tictactoe Board",
      color=self.yellow
    )
    file = discord.File(img, filename="image1.png")
    embed.set_author(name=self.author)
    embed.set_image(url="attachment://image1.png")
    embed.set_footer(text="Type .quit to stop playing.")
    await ctx.send(file=file, embed=embed)
    
    def get_key(val):
      for key, value in self.session.getBoardChoice().items():
          if val == value:
            return key
    def check_msg(m):
      try:
        return (
          m.channel.id == ctx.channel.id and 
          (m.content.startswith(".") or 
          m.content.lower() in self.session.getBoardChoice().keys())
        )
      except:
        return False

    def choiceEmbed(author, choice):
      embed = discord.Embed(
        title=f"{author} chooses '{choice}'",
        color=self.yellow
      )
      embed.set_author(name=self.author)
      embed.set_footer(text="Type .quit to stop playing.")
      return embed
      
    for i in range(9):
      
      if (i % 2 == 0):
        msg = await ctx.send("Type your move according to the board.")
        
        check = True
        choice = None
        while True:
          try:
            msgs = await self.client.wait_for(
              "message", 
              check=check_msg, 
              timeout=60
            )
            content = msgs.content
            author = msgs.author
            
            if content == ".quit" and author == ctx.author:
              check=False
              await ctx.send("Thanks for playing.")
              break
              
            if not content.startswith("."):
              choice = content
              self.session.playerMove(choice)
              img = self.session.getBoard()
              await msg.delete()
              embed = choiceEmbed(author.name, choice)
              file = discord.File(img, filename="image1.png")
              embed.set_image(url="attachment://image1.png")
              await ctx.send(ctx.author.mention, file=file, embed=embed)
              break
              
          except asyncio.TimeoutError:
            await ctx.send("Timed out, no response in 60 seconds.")
            check = False
            break
            
        if check is False:
          break
        time.sleep(1)
      else:
        choice = get_key(self.session.compMove())
        img = self.session.getBoard()
        embed = choiceEmbed("Computer", choice)
        file = discord.File(img, filename="image.png")
        embed.set_image(url="attachment://image.png")
        time.sleep(1)
        await ctx.send(ctx.author.mention, file=file, embed=embed)
        
        
      status = self.session.checkGameStatus()
      if (status == 1):
        await ctx.send("Computer won! Thanks for playing.")
        break
      elif (status == -1):
        await ctx.send(f"{ctx.author.name} won! Thanks for playing.")
        break
      elif (status == 0):
        await ctx.send("Game draw! Thanks for playing.")
        break
        
def setup(client):
  client.add_cog(tictactoegame(client, Tictactoe()))