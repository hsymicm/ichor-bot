import discord
import datetime, pytz, re, time, os, json, sys
from discord.ext import commands
from discord import app_commands
from AnilistPython import Anilist
from encrypt import load, save
import asyncio

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
      
# Misc
cleanr = re.compile('<.*?>') 
tz = pytz.timezone("Asia/Jakarta")
anilist_thumb = 'https://anilist.co/img/icons/android-chrome-512x512.png'

# Truncate a long string
def truncate(data, length, suffix='..'):
  return (
    (' '.join(data[:length+1].split(' ')[0:-1]) + suffix) 
    if len(data) > length else data
  )

# Html tags cleaner
def clean_tags(data):
  return re.sub(cleanr, '', data)

# Dictionary cleaner
def clean_dict(dict):
  return { k: ('-' if v == None or v == "null" else v) for k, v in dict.items() }

# Date format checker
def check_date(date, format):
  try:
    datetime.datetime.strptime(date, format)
    return date
  except ValueError:
    return "-"

def check_null(data):
  return True if data in [None, "null", "-"] else False
  
# Embed page function
def embeds(author, color, page, content, split, page_title ,title=None, thumb=None):
  strings = ""
  for count, item in enumerate(content[page-1],1):
    strings += f"{count+split*(page-1)}.\t{item}\n"
  if title is None:
    title = f"{author.name}'s Watchlist"
  embed = discord.Embed(
    title=title,
    description=strings,
    color=color
  )
  embed.set_author(name=page_title)
  embed.set_footer(text=f"Page {page}/{len(content)}")
  if thumb is not None:
    embed.set_thumbnail(url=thumb)
  return embed

# Class Otaku
class otaku (commands.Cog):
  def __init__(self, client, anilist):
    self.client = client
    self.anilist = anilist
    self.userDict = {}
    self.yellow = 0xebd234

  # Create Starting Search Embed
  def create_search_embed(self, author, inp):
    embed = discord.Embed(
      title=f"Searching \"{inp}\", please wait!", 
      color=self.yellow
    )
    embed.set_author(name=author)
    return embed

  @app_commands.command(name="search", description="Search anime/manga titles.")
  @app_commands.choices(type=[
    app_commands.Choice(name="Anime", value="anime"),
    app_commands.Choice(name="Manga", value="manga"),
  ])
  @app_commands.describe(title="Input anime/manga title.")
  @app_commands.checks.cooldown(12, 300, key=lambda i: (i.guild_id, i.user.id))
  async def search(self, interaction: discord.Interaction, type: app_commands.Choice[str], title: str) -> None:
    await interaction.response.defer()

    msg = await interaction.followup.send(
        interaction.user.mention, 
        embed=self.create_search_embed(f"{type.name} Search",  title),
        wait=True
      )

    try:
      with HiddenPrints():
        if(type.value == 'manga'):
          data = clean_dict(self.anilist.get_manga(title))
        else:
          data = clean_dict(self.anilist.get_anime(title))
  
      name = data['name_english'] if data['name_english'] != "-" else data['name_romaji']
      desc = truncate(clean_tags(data['desc']), 125)
      score = round(int(data['average_score'])/10, 2) if data['average_score'] != "-" else "-"
      thumb = data['cover_image']
      banner = data['banner_image']
      genre = data['genres'] if len(data['genres']) != 0 else "-"
      status = data['release_status' if type.value == "manga" else 'airing_status'].lower().capitalize().replace("_", " ")
  
      if(type.value == 'manga'):
        volume = data['volumes']
        format = data['release_format'].lower().capitalize().replace("_", " ")
      else:
        eps = data['airing_episodes']
        next_ep = data['next_airing_ep']
        date = data['starting_time'].split('/')
        date = date[-1] if date != None else "-"
        season = data['season']
        if check_null(season) or check_null(date):
          season = "-"
        else:
          season = f"{season.lower().capitalize()} {'' if check_null(date) else date.split('/')[-1]}"

      embed = discord.Embed(
        title=name, 
        description=desc, 
        color=self.yellow
      )
      embed.set_author(name=f"{type.name} Search")
      if thumb != "-":
        embed.set_thumbnail(url=thumb)
      if banner != "-":
        embed.set_image(url=banner)
  
      embed.add_field(
        name="Format" if type.value == "manga" else "Season",
        value=format if type.value == "manga" else season,
        inline=True)
      
      embed.add_field(name="Score", value=f"{score}/10", inline=True)
      
      embed.add_field(
        name="Volume" if type.value == "manga" else "Episodes",
        value=volume if type.value == "manga" else eps,
        inline=True)
      
      embed.add_field(name="Genre", value=', '.join(genre), inline=False)
      embed.add_field(name="Status", value=status, inline=True)

      if type.value == 'anime':
        if next_ep != "-":
          embed.add_field(
            name="Next Episode", 
            value=f"Episode {next_ep['episode']}\n{datetime.datetime.fromtimestamp(int(next_ep['airingAt']), tz = tz).strftime('%d/%m/%Y - %I:%M %p')}",
          inline=False
          )
        
      await msg.edit(embed=embed)
      
    # Error Exceptions
    except Exception as e:
      # Editted Embed
      embed_fail = discord.Embed(
        title=f"An Error Occured, {e}.", 
        color=self.yellow
      )
      embed_fail.set_author(name=f"{type.name} Search")
      await msg.edit(embed=embed_fail)
      print(e)
    
  @commands.group(invoke_without_command=True)
  async def mylist(self, ctx):
    author = 'Anime List'
    if ctx.invoked_subcommand is None:
      # Fetching List Embed
      embed_fetch = discord.Embed(
        title=f"Fetching list..", 
        color=self.yellow
      )
      embed_fetch.set_thumbnail(url=anilist_thumb)
      embed_fetch.set_author(name=author)
      message = await ctx.send(ctx.author.mention, embed=embed_fetch)

      # Fetching user list from database
      root = load('myAnimeList.json')
      db = root['user']
      uid = str(ctx.author.id)
      
      try:
        # list and error checking
        if uid not in db:
          db[uid] = {'mylist':[]}
      
        items = db[uid]['mylist']
        save('myAnimeList.json', root)
        
        if len(items) == 0:
          raise Exception("No watchlist.")
          
        split = 4
        split_arr = [items[i:i + split] for i in range(0, len(items), split)]

        # Properties for page system
        cur_page = 1
        pages = len(split_arr)

        # Embed list
        embed_list = embeds(
          ctx.author, 
          self.yellow, 
          cur_page, 
          split_arr, 
          split, 
          author,
          None,
          anilist_thumb
        )
        await message.edit(embed=embed_list)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        # Checking user reaction
        def check(reaction, user):
          return (
          user == ctx.author and 
          str(reaction.emoji) in ["◀️", "▶️"] and 
          reaction.message == message
        )

        # Loop with a timeout
        while True:
          try:
            # wait_for
            reaction, user = await self.client.wait_for(
              "reaction_add", 
              timeout=60, 
              check=check
            )

            # Next page
            if str(reaction.emoji) == "▶️" and cur_page != pages:
              cur_page += 1
              embed_list = embeds(
                ctx.author, 
                self.yellow, 
                cur_page, 
                split_arr, 
                split,
                author,
                None,
                anilist_thumb
              )
              await message.edit(embed=embed_list)
              await message.remove_reaction(reaction, user)

            # Previous page
            elif str(reaction.emoji) == "◀️" and cur_page > 1:
              cur_page -= 1
              embed_list = embeds(
                ctx.author, 
                self.yellow, 
                cur_page, 
                split_arr, 
                split, 
                author,
                None,
                anilist_thumb
              )
              await message.edit(embed=embed_list)
              await message.remove_reaction(reaction, user)

            else:
              await message.remove_reaction(reaction, user)

          # If user doesn't react in x seconds loop stops
          except asyncio.TimeoutError:
            break

      except Exception as e:
        # Editted Embed
        embed_fail = discord.Embed(
          title=f"An Error Occured, {e}.", 
          color=self.yellow
        )
        embed_fail.set_thumbnail(url=anilist_thumb)
        embed_fail.set_author(name=author)
        await message.edit(embed=embed_fail)
        
      save('myAnimeList.json', root)
      
  # Sub commands
  @mylist.command(name='add')
  async def _add(self, ctx, *, inp):
    author = 'Add Title'
    root = load('myAnimeList.json')
    db = root['user'] 
    uid = str(ctx.author.id)
    
    try:
      # Searching
      aniDict = clean_dict(self.anilist.get_anime(inp))
  
      # Processing Information
      name_romaji = aniDict['name_romaji']
      name_english = aniDict['name_english']
      if name_english != "-":
        name = name_english
      else:
        name = name_romaji
        
      # Appending
      if uid not in db:
        db[uid] = {'mylist':[]}
      elif name in db[uid]['mylist']:
        raise Exception("Duplicate Titles")
      db[uid]['mylist'].append(name)

      # Embed
      embed_add = discord.Embed(
        title=name,
        description="Has been added to your list 🧾",
        color=self.yellow
      )
      
      embed_add.set_thumbnail(url=anilist_thumb)
      embed_add.set_author(name=author)
      await ctx.send(ctx.author.mention, embed=embed_add)
      
    except Exception as e:
      embed_fail = discord.Embed(
        title=f"An Error Occured, {e}.", 
        color=self.yellow
      )
      embed_fail.set_thumbnail(url=anilist_thumb)
      embed_fail.set_author(name=author)
      await ctx.send(ctx.author.mention, embed=embed_fail)
      print(e)
      
    save('myAnimeList.json', root)

  @mylist.command(name='remove')
  async def _remove(self, ctx):
    author = "Remove Title"
    title = f"Choose a number to remove from your watchlist"
    # Fetching List Embed
    embed_fetch = discord.Embed(
      title=f"Fetching list..", 
      color=self.yellow
    )
    embed_fetch.set_thumbnail(url=anilist_thumb)
    embed_fetch.set_author(name=author)
    message = await ctx.send(ctx.author.mention, embed=embed_fetch)

    # Fetching user list from database
    root = load('myAnimeList.json')
    db = root['user']
    uid = str(ctx.author.id)
    
    try:
      # list and error checking
      if uid not in db:
        db[uid] = {'mylist':[]}
    
      items = db[uid]['mylist']
      save('myAnimeList.json', root)
      
      if len(items) == 0:
        raise Exception("No watchlist.")
        
      split = 4
      total_items = len(items)
      split_arr = [items[i:i + split] for i in range(0, total_items, split)]

      # Properties for page system
      cur_page = 1
      pages = len(split_arr)

      # Embed list
      embed_list = embeds(
        ctx.author, 
        self.yellow, 
        cur_page, 
        split_arr, 
        split, 
        author,
        title,
        anilist_thumb
      )
      await message.edit(embed=embed_list)
      await message.add_reaction("◀️")
      await message.add_reaction("▶️")

      # Checking user reaction
      def check_reaction(reaction, user):
        return (
          user == ctx.author and 
          str(reaction.emoji) in ["◀️", "▶️"] and 
          reaction.message == message
        )
        
      def check_msg(m):
        try:
          choose = int(m.content)
          return (
              choose in range(1, total_items + 1)
              and m.channel.id == ctx.channel.id
          )
        except:
          return False
          
      # Loop with a timeout
      while True:
        
          timeout = 60

          # Tasks wait for message and adding reaction
          tasks = [
            asyncio.create_task(
              self.client.wait_for(
                'message',
                timeout=timeout, 
                check=check_msg
              ),
              name='msgs'
            ),
            asyncio.create_task(
              self.client.wait_for(
                "reaction_add", 
                timeout=timeout, 
                check=check_reaction
              ),
              name='reaction'
            )
          ]

          # Task results
          done, pending = await asyncio.wait(
            tasks, 
            return_when=asyncio.FIRST_COMPLETED
          )
          finished: asyncio.Task = list(done)[0]

          # Task Error handling
          for task in pending:
            try:
              task.cancel
            except asyncio.CancelledError:
              pass

          # Actions
          action = finished.get_name()
        
          # Timeout Handling
          try:
            result = finished.result()
          except asyncio.TimeoutError:
            # Editted Embed
            embed_timeout = discord.Embed(
              title="Remove command has timed out",
              color=self.yellow
            )
            embed_timeout.set_thumbnail(url=anilist_thumb)
            embed_timeout.set_author(name="Anime List")
            await message.edit(embed=embed_timeout)
            return
          
          if action == 'reaction':
            reaction, user = result

            # Next page
            if str(reaction.emoji) == "▶️" and cur_page != pages:
              cur_page += 1
              embed_list = embeds(
                ctx.author, 
                self.yellow, 
                cur_page, 
                split_arr, 
                split, 
                author,
                title,
                anilist_thumb
              )
              await message.edit(embed=embed_list)
              await message.remove_reaction(reaction, user)

            # Previous page
            elif str(reaction.emoji) == "◀️" and cur_page > 1:
              cur_page -= 1
              embed_list = embeds(
                ctx.author, 
                self.yellow, 
                cur_page, 
                split_arr, 
                split, 
                author,
                title, 
                anilist_thumb
              )
              await message.edit(embed=embed_list)
              await message.remove_reaction(reaction, user)
  
            else:
              await message.remove_reaction(reaction, user)
            
          elif action == 'msgs':
            load('myAnimeList.json')
            m = result
            name = items.pop(int(m.content)-1)
            
            # Editted Embed
            embed_remove = discord.Embed(
              title=f"{name}", 
              description='Has been removed from your watchlist.',
              color=self.yellow
            )
            embed_remove.set_thumbnail(url=anilist_thumb)
            embed_remove.set_author(name="Anime List")
            await message.edit(embed=embed_remove)
            save('myAnimeList.json', root)
            return
        
      # Saving
      save('myAnimeList.json', root)
      
    except Exception as e:
      # Editted Embed
      embed_fail = discord.Embed(
        title=f"An Error Occured, {e}.", 
        color=self.yellow
      )
      embed_fail.set_thumbnail(url=anilist_thumb)
      embed_fail.set_author(name=author)
      await message.edit(embed=embed_fail)
      print(e)

      # Fail save
      save('myAnimeList.json', root)


  # Update Command
  @commands.command(name="update")
  async def updateCommand(self, ctx):
    # gets list of anime
    with open('Schedules/AiringList.txt') as f:
      anime_list = f.read().splitlines() 
      
    # Create embed
    embed = discord.Embed(title=f"Updating Schedule...", color=0xebd234)
    embed.set_author(name="Schedule")
    embed.add_field(name="Progress", value='0.00%', inline=True)
    message = await ctx.send(embed=embed)

    #for progress %
    prog = 1
    total = len(anime_list)
    
    schedule = {}
    for i in anime_list:
      # update embed
      progress = round(prog/total*100,2)
      embed1 = discord.Embed(title=f"Updating Schedule...", color=0xebd234)
      embed1.set_author(name="Schedule")
      embed1.add_field(name="Progress", value=f'{progress}%', inline=True)
      await message.edit(embed=embed1)

      # get airing day of anime
      try:
        anime_dict = self.anilist.get_anime(i)
        title = anime_dict['name_romaji']
        unix_time = anime_dict['next_airing_ep']['airingAt']
        unix_int = int(unix_time) + 25200
        day = datetime.datetime.utcfromtimestamp(unix_int).strftime('%A')
        airTime = datetime.datetime.utcfromtimestamp(unix_int).strftime('%H:%M')
      except Exception as e:
        # reports error
        embed3 = discord.Embed(title=f"Updating Schedule...", color=0xebd234)
        embed3.set_author(name="Schedule")
        embed3.add_field(name="Progress", value=f'an error has occured, {e}', inline=True)
        await message.edit(embed=embed3)
        return

      # build dictionary
      entry = {}
      entry['title'] = title
      entry['airTime'] = airTime
      
      if(day not in schedule.keys()):
        schedule[day] = []
  
      schedule[day].append(entry)
 
      print(anime_dict['name_romaji'], day)
      prog += 1
      
      time.sleep(1)

    # make json file
    with open("Schedules/schedule.json", 'w') as outfile:
      json.dump(schedule, outfile)

    # Update Success
    embed2 = discord.Embed(title=f"Updating Schedule...", color=0xebd234)
    embed2.set_author(name="Schedule")
    embed2.add_field(name="Progress", value='Update Successful', inline=True)
    await message.edit(embed=embed2)

  @commands.command(name="schedule")
  async def scheduleCommand(self, ctx):
    # Create embed
    embed = discord.Embed(title=f"Please Wait...", color=0xebd234)
    embed.set_author(name="Schedule")
    message = await ctx.send(embed=embed)
    
    # Gets the anime for the day
    day = datetime.datetime.now().strftime('%A')
    schedule = []
    with open(f'Schedules/schedule.json') as f:
      schedule = json.load(f)

      scheduleDay = schedule[day]

    embed1 = discord.Embed(title=f'{day}\'s schedule', color=0xebd234)
    for i in scheduleDay:
      embed1.add_field(name=i['title'], value=i['airTime'], inline=False)
    
    embed1.set_thumbnail(url=anilist_thumb)
    await message.edit(embed = embed1)

# Cog Setup
async def setup(client):
  await client.add_cog(otaku(client, Anilist()))
