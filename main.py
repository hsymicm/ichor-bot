import os
import discord
from discord.ext import commands, tasks
import otaku, music3, misc, genshin_fun, genshin_stats, lyricsgame, tictactoegame
import keep_alive
import asyncio
from itertools import cycle

cogs = [
  otaku, 
  genshin_fun, 
  genshin_stats, 
  lyricsgame, 
  tictactoegame,
  music3, 
  misc
]

client = commands.Bot(
  command_prefix='>',
  intents=discord.Intents.all(),
  help_command=None
)

stat = cycle([
  'Python',
  'Otaku Stuff',
  'Music Player',
  'Mini Games',
  'Wish Simulator',
  'Wish Inventory',
  'Genshin Wiki',
  'Genshin Stats'
])

@tasks.loop(seconds=10)
async def change_status():
  await client.change_presence(activity=discord.Game(next(stat)), status=discord.Status.idle)

@client.event
async def on_ready():
  change_status.start()
  print("Your bot is ready")
  for i in range(len(cogs)):
    await cogs[i].setup(client)

@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    msg = '**Still on cooldown, please try again in {:.2f}s**'.format(error.retry_after)
    await ctx.send(msg)
  else:
    print(error)

async def main():
  async with client:
    my_secret = os.environ['TOKEN']
    await client.start(my_secret)

repl_link = 'https://DiscordBot.fadilhisyam.repl.co'
keep_alive.awake(repl_link, True)

try:
  asyncio.run(main())
except:
  os.system("kill 1")
