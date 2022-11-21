from PIL import Image, ImageFont, ImageDraw
import io

mask = Image.open("img/mug_shot/mask.png")
mask2 = Image.open("img/mug_shot/mask2.png")

def count_keys(d):
  keys = 0
  if type(d) == dict:
    for key in d.keys():
      if isinstance(d[key], (list, tuple, dict)):
        k = count_keys(d[key])
        keys += k
      else:
        keys += 1
  return keys

def inv(d):
  column = 8
  count = -(-count_keys(d)//column)
  if count == 0:
    raise ValueError("Empty Inventory")
  else:
    inventory = Image.new("RGBA", (256*column, 296*count))
    x = 0
    y = 0
    for rarity in dict(reversed(list(d.items()))):
      for char in d[rarity]:
        img1 = Image.open(f"img/mug_shot/{rarity}/{char}.png")
        bg = Image.open(f"img/mug_shot/{rarity}_bg.png").convert("RGBA")
        final = Image.new("RGBA", (256, 296))
        final.paste("white", (0, 0), mask)
        final.paste(Image.alpha_composite(bg, img1), (0, 0), mask2)
        draw = ImageDraw.Draw(final)
        text = char.split('.')[0]
        cons = str(f"C{d[rarity][char]-1}")
        font = ImageFont.truetype(r'zh-cn.ttf', 50)
        draw.text(
          (240 - (font.getlength(cons)), 185),
          cons,
          font=font,
          align="center",
          stroke_fill="black",
          stroke_width=3
        )
        font = ImageFont.truetype(r'zh-cn.ttf', 36)
        draw.text(
          (256 / 2 - (font.getlength(text) / 2), 247),
          text.title(),
          fill="#5c5c5c",
          font=font,
          align="center"
        )
        inventory.paste(final, (256*x, 296*y))
        x += 1
        if x > column-1:
          x = 0
          y += 1
    width, height = inventory.size
    final = io.BytesIO()
    inventory.resize((width//3, height//3)).save(final, format="png", compress_type=0)
    final.seek(0)
    
    return final
