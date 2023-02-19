import discord
from discord.ext import commands
import asyncio

from lyrics_game.Lyrics import Lyrics
from lyrics_game.Player import Player

class lyricsgame(commands.Cog):
  
  def __init__(self, client, lyrics):
    self.client = client
    self.lyrics = lyrics
    self.sessions = {}
    self.maxHealth = 3
    self.yellow = 0xebd234
    self.gameTitle = "Lyric Guesser"
    
  @commands.group(invoke_without_command=True)
  async def lyrics(self, ctx):
    if ctx.invoked_subcommand is None:
      await ctx.send("main lyrics command")
      # Add short description and help sections
  
  def getPlayerInfo(self, ctx):
    sid = ctx.guild.id
    uid = ctx.author.id
    name = ctx.author.name
    return (sid, uid, name)

  def getPlayerList(self, data):
    return [
      f"{count}. " + data[ids].getName() 
      for count, ids in enumerate(data.keys(), 1)
    ]
    
  def joinGame(self, sid, uid, name):
    try:
      self.sessions[sid][uid] = Player(name, self.maxHealth)
    except:
      self.sessions[sid] = {uid : Player(name, self.maxHealth)}
  
  async def _startGame(self, ctx):
    maxRound = 5
    def embedRound(self, curRound, songTitle, question):
      embed_round = discord.Embed(
        title=f"{songTitle} ~ Round {curRound}",
        description=question,
        color=self.yellow
      )
      embed_round.set_author(name=self.gameTitle)
      embed_round.set_footer(text="Type .stop to stop the session.")
      return embed_round

    def embedFinish(self):
      embed_finish = discord.Embed(
        title=f"Thank you for playing Lyric Guesser!",
        color=self.yellow
      )
      for data in self.sessions[ctx.guild.id].values():
        health_num = data.getHealth()
        health = ":heart:"*health_num + ":black_heart:"*(self.maxHealth-health_num)
        score = data.getScore()
        embed_finish.add_field(name=data.getName(), value=f"Score: {score} pts\nHealth: {health}", inline=True)
      embed_finish.set_author(name=self.gameTitle)
      embed_finish.set_footer(text="Type >lyrics play to play again.")
      return embed_finish
      
    def check_msg(m):
        try:
          return (
            m.channel.id == ctx.channel.id
          )
        except:
          return False
          
    check = True
    for i in range(maxRound):
      self.lyrics.setQuestion()
      await ctx.send(embed=embedRound(self, (i+1), self.lyrics.getChoosenSong(), self.lyrics.getQuestion()))
      
      while True:
        try:
          msgs = await self.client.wait_for(
            "message", 
            check=check_msg, 
            timeout=60
          )
          content = msgs.content
          author = msgs.author

          if content == ".stop" and author == ctx.author:
            check = False
            break
            
          if not content.startswith("."):
            if self.lyrics.checkPlayerAnswer(content):
              self.sessions[ctx.guild.id][author.id].modifyScore(100)
              await ctx.send(f"Congrats {author.name}! your answer is correct. (+100 pts)")
              break
            else:
              self.sessions[ctx.guild.id][author.id].modifyHealth(-1)
              await ctx.send(f"Sorry {author.name}, your answer is wrong. (-1 Life)")
              if 0 in [life.getHealth() for life in self.sessions[ctx.guild.id].values()]:
                check = False
                break
        except asyncio.TimeoutError:
          await ctx.send("Timed out, no response in 60 seconds.")
          break
      if check is False:
        break

    await ctx.send(embed=embedFinish(self))
    self.sessions[ctx.guild.id] = {}
      
  @lyrics.command(name='play')
  async def _play(self, ctx):
    sid, uid, name = self.getPlayerInfo(ctx)
    self.joinGame(sid, uid, name)

    def embedPlay(self):
      embed_play = discord.Embed(
        title=f"Player List :",
        description="\n".join(self.getPlayerList(self.sessions[sid])) + "\n...",
        color=self.yellow
      )
      embed_play.set_author(name=self.gameTitle)
      embed_play.set_footer(
        text="Type .join to join or .start to start"
      )
      return embed_play
    message = await ctx.send(embed=embedPlay(self))
    
    def check_msg(m):
      try:
        return (
          m.content.startswith(".")
          and m.channel.id == ctx.channel.id
        )
      except:
        return False
      
    while True:
      try:
        msgs = await self.client.wait_for(
          "message", 
          check=check_msg, 
          timeout=60
        )
        content = msgs.content
        author = msgs.author
        
        if content == ".join" and author != ctx.author:
          self.joinGame(sid, author.id, author.name)
          await message.edit(embed=embedPlay(self))

        elif content == ".start" and author == ctx.author:
          await self._startGame(ctx)
          break
          
      except asyncio.TimeoutError:
        embed_timeout = discord.Embed(
          title="Command timed out.",
          decsription="No response in 60 seconds, try again.",
          color=self.yellow
        )
        embed_timeout.set_author(name=self.gameTitle)
        await message.edit(embed=embed_timeout)
        break

  @lyrics.command(name='player')
  async def _player(self, ctx):
    await ctx.send("player list")

  @lyrics.command(name='highscore')
  async def _highscore(self, ctx):
    await ctx.send("player highscore")

  @lyrics.command(name='list')
  async def _list(self, ctx):
    embed_list = discord.Embed(
      title = "Song list",
      description = self.lyrics.getSongList(),
      color=self.yellow
    )
    embed_list.set_author(name=self.gameTitle)
    await ctx.send(ctx.author.mention, embed=embed_list)
    
async def setup(client):
  await client.add_cog(lyricsgame(client, Lyrics("lyrics_game/lyrics/")))