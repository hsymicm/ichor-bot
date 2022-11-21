import os
import discord
from discord.ext import commands
import genshin

LUID = os.environ['LUID']
LTOKEN = os.environ['LTOKEN']

def stripes(n):
  stripe = ""
  for i in range(0,n):
    stripe += "_"
  return stripe
  
global resin
check = "https://cdn.discordapp.com/attachments/902414074720178216/942928731855532062/pngegg.png"
img = "https://cdn.discordapp.com/attachments/902414074720178216/905114368574894100/footer.png"
d = {'ltuid': LUID, 'ltoken': LTOKEN}

uid = 812630789

class genshin_stats(commands.Cog):
  def __init__(self, client, gs_client):
    self.client = client
    self.gs_client = gs_client
    
  @commands.command(name='resin')
  async def get_resin(self, ctx):
    client = self.gs_client
    client.set_cookies(d)
    notes = await client.get_notes(uid)
    embed4 = discord.Embed(title=f"★ Resin Check ★", description=f"{notes.current_resin}/{notes.max_resin}", color=0xebd234)
    embed4.set_thumbnail(url='https://cdn.discordapp.com/attachments/902414074720178216/942942550254313523/256.png')
    await ctx.send(ctx.author.mention, embed=embed4)

  @commands.command(name='claim')
  async def claim_daily_hoyolab(self, ctx):
    client = self.gs_client
    client.set_cookies(d)
    name = ""
    value = ""
    icon = check

    try:
      reward = await client.claim_daily_reward()

    except genshin.AlreadyClaimed:
      print("Already claimed")
      name = "Reward already claimed"
      value = f"{ctx.author.display_name}, you already claimed your reward for today, comeback tomorrow!"

    else:
      print("Claimed Successfully")
      name = "Reward claimed succesfully"
      value = f"{ctx.author.display_name}, you claimed\n{reward.amount}x {reward.name}"
      icon = reward.icon
      print(icon)
      
    signed_in, claimed_rewards = await client.get_reward_info()
    embed5 = discord.Embed(title=f"★ Hoyolab Daily Login ★", description="Claim your daily ingame items!", color=0xebd234)
    embed5.set_author(name="Genshin Stats")
    embed5.add_field(name=stripes(50), value='\u200b', inline=False)
    embed5.add_field(name=name, value=value, inline=False)
    embed5.add_field(name="Status", value=f"Total claimed rewards: {claimed_rewards}", inline=False)
    embed5.set_image(url=img)
    embed5.set_thumbnail(url=icon)
    await ctx.send(ctx.author.mention, embed=embed5)
  
def setup(client):
  client.add_cog(genshin_stats(client, genshin.GenshinClient()))