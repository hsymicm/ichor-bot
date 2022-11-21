from PIL import Image
import os
import random
import time
import io
#import numpy as np

# Array List Item
card_4s = [
  ('img/card_4s/' + filename) 
  for filename in os.listdir('img/card_4s/') 
  if os.path.isfile(
    os.path.join(
      'img/card_4s/', filename
    ))]
card_rateoff = [
  ('img/card_5s/rateoff/' + filename) 
  for filename in os.listdir('img/card_5s/rateoff/') 
  if os.path.isfile(
    os.path.join(
      'img/card_5s/rateoff/', filename
    ))]
wep_5s = [
  ('img/card_5s/wep_5s/' + filename) 
  for filename in os.listdir('img/card_5s/wep_5s/') 
  if os.path.isfile(
    os.path.join(
      'img/card_5s/wep_5s/', filename
    ))]
wep_rateoff_5s = [
  ('img/card_5s/wep_5s/rateoff_wep/' + filename) 
  for filename in os.listdir('img/card_5s/wep_5s/rateoff_wep/') 
  if os.path.isfile(
    os.path.join(
      'img/card_5s/wep_5s/rateoff_wep/', filename
    ))]
wep_4s = [
  ('img/card_4s/wep_4s/' + filename) 
  for filename in os.listdir('img/card_4s/wep_4s/') 
  if os.path.isfile(
    os.path.join(
      'img/card_4s/wep_4s/', filename
    ))]
wep_exclusive_4s = [
  ('img/card_4s/wep_exclusive_4s/' + filename) 
  for filename in os.listdir('img/card_4s/wep_exclusive_4s/') 
  if os.path.isfile(
    os.path.join(
      'img/card_4s/wep_exclusive_4s/', filename
    ))]
wep_3s = [
  ('img/wep_3s/' + filename) 
  for filename in os.listdir('img/wep_3s/') 
  if os.path.isfile(
    os.path.join(
      'img/wep_3s/', filename
    ))]

def concatimg(arr):
  # start_time_merge = time.time()
  new_img = Image.new("RGBA", (1000, 600))
  for j, i in enumerate(arr):
    new_img.paste(Image.open(i), (100*j, 0))
  # print("Merge image :\n--- %s ms ---" % ((time.time() - start_time_merge)*1000))
  return new_img

def saveImg(arr):
  # Merge Array & Save Output
  imgs = concatimg(arr)
  width, height = imgs.size
  # start_time_io = time.time()
  final = io.BytesIO()
  imgs.resize((width//2, height//2)).save(final, format='png', compress_level=0)
  final.seek(0)
  # print("IO :\n--- %s ms ---" % ((time.time() - start_time_io)*1000))
  
  return (final, arr)

def gachaWep(inp):
  limited = f"img/card_5s/wep_5s/{inp}.png"
  if limited not in wep_5s:
    limited = f"img/card_5s/wep_5s/rateoff_wep/{inp}.png"
    
  pull = []
  for i in range(9):
    s3=wep_3s[random.randint(0, len(wep_3s)-1)]
    s4=random.choices(
      population=[
        random.choice(wep_4s), 
        random.choice(wep_exclusive_4s),
        random.choice(card_4s)
        ], 
      weights=[35,50,15], 
      k=1)[0]
    s5r=random.choice(wep_rateoff_5s)
    pull.append(
      random.choices(
        population=[s3, s4, limited, s5r], 
        weights=[90, 8, 0.7, 1.3], 
        k=1)[0])
  pull.insert(
    random.randint(0, 8), 
    random.choices(
      population=[
        random.choice(wep_4s), 
        random.choice(wep_exclusive_4s),
        random.choice(card_4s)
        ], 
      weights=[35,50,15],  
      k=1)[0])
  
  for i in range(10):
      if pull[i] in card_4s + wep_4s + wep_exclusive_4s:
        pull.insert(0, pull.pop(i))
  for i in range(10):
    if pull[i] == limited or pull[i] in wep_rateoff_5s:
      pull.insert(0, pull.pop(i))

  return saveImg(pull)
  
def gachaChar(inp):
  limited = f"img/card_5s/{inp}.png"

  # start_time_gacha = time.time()
  # Randomizer
  pull= []
  for i in range(9):
    s3=wep_3s[random.randint(0, len(wep_3s)-1)]
    s4=random.choices(
      population=[
        random.choice(card_4s), 
        random.choice(wep_4s)
        ], 
      weights=[70,30], 
      k=1)[0]
    s5r=random.choice(card_rateoff)
    pull.append(
      random.choices(
        population=[s3, s4, limited, s5r], 
        weights=[90, 8, 1, 1], 
        k=1)[0])
  pull.insert(
    random.randint(0, 8), 
    random.choices(
      population=[
        random.choice(card_4s), 
        random.choice(wep_4s)
        ],
      weights=[70,30], 
      k=1)[0])

  # print("gacha :\n--- %s ms ---" % ((time.time() - start_time_gacha)*1000))
  # start_time_sort = time.time()
  # Sorting Array
  for i in range(10):
    if pull[i] in card_4s + wep_4s:
      pull.insert(0, pull.pop(i))
  for i in range(10):
    if pull[i] == limited or pull[i] in card_rateoff:
      pull.insert(0, pull.pop(i))
  # print("Sort :\n--- %s ms ---" % ((time.time() - start_time_sort)*1000))

  return saveImg(pull)