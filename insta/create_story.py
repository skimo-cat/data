import os
import datetime
import json
from PIL import Image, ImageFont, ImageDraw

img = Image.new('RGB', (1080, 1920), color='black')

fnt = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/Neuton-Light.ttf'), 35)
fnt_bold = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/Neuton-Bold.ttf'), 120)
fnt_emoji = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/Symbola.ttf'), 120)

d = ImageDraw.Draw(img)
d.text((10,10), 'Gruix neu: X', fonts=fnt, fill=(255,255,255))
d.text((350,70), '❄️',font=fnt_emoji, fill=(255,255,255))
d.text((365,70), 'Nevades', font=fnt_bold, fill=(255,255,255))

d.line([(330, 220), (790, 220)], fill=(255,255,255), width=10)


now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

img.save('story.png')
