import os
import datetime
import json
from PIL import Image, ImageFont, ImageDraw

WIDTH = 1080
HEIGHT = 1920

img = Image.new('RGB', (WIDTH, HEIGHT), color=(0x2C, 0x29, 0x29))
d = ImageDraw.Draw(img)

#fnt = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/Neuton-Light.ttf'), 35)
#fnt_bold = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/Neuton-Bold.ttf'), 120)
fnt = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Regular.ttf'), 35)
fnt_supersmall = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Regular.ttf'), 25)
fnt_bigger = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Regular.ttf'), 50)
fnt_bold = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Bold.ttf'), 120)
fnt_bold_mid = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Bold.ttf'), 70)
fnt_bold_small = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Bold.ttf'), 50)
fnt_emoji = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/Symbola.ttf'), 120)

def text_aligned(txt, fill='white', under=False, x=None, y=None, divide=2, _font=fnt, linewidth=10):
    _, _, w, h = d.textbbox((0, 0), txt, font=_font)
    if x is None:
        x = (WIDTH-w)/divide
    if y is None:
        y = (HEIGHT-h)/divide

    d.text((x, y), txt, font=_font, fill=fill)
    if under:
        d.line([(x, y + h + 20), (x + w, y + h + 20)], fill=(255,255,255), width=linewidth)

    return w, h

def create_box_half(x1, y1, x2, y2):
    d.rectangle([(x1, y1), (x2, y2)], fill=(0x3d, 0x36, 0x36), outline=None)


#d.text((10,10), 'Gruix neu: X', fonts=fnt, fill=(255,255,255))
#d.text((350,70), '❄️',font=fnt_emoji, fill=(255,255,255))
#d.text((365,70), 'Nevades', font=fnt_bold, fill=(255,255,255))

text_aligned("skimo.cat | Dades d'estacions automàtiques", y=1870, _font=fnt_supersmall)
text_aligned('Gruixos de neu', under=True, y=140, _font=fnt_bold, linewidth=6)
text_aligned('Increment de neu durant el ultims 7 dies', y=290)

now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

y = 380
left = 50
elements = 0
box_width = 460
box_height = 320
box_gap = 50

with open('../docs/increment.json') as f:
    data = json.load(f)

    key = 'week_ago'

    # Order keys from higher increment to lower, taking into account that the key can be missing
    keys = sorted(data.keys(), key=lambda x: abs(data[x][key]) if key in data[x].keys() else 0, reverse=True)

    # Order keys from higher increment to lower, taking the absolute value (converting negative to positive values) taking into account that the key can be missing


    for k in keys:
        if elements >= 8:
            # All boxes are full
            break
        #if 'year_ago' not in data[k].keys():
        if key not in data[k].keys():
            continue
        if 'gruix' not in data[k].keys():
            continue
        name = data[k]['name']
        if len(name) > 10:
            name = name[:10]
        week_ago = data[k][key]
        #week_ago = data[k]['year_ago']
        gruix = data[k]['gruix']

        increment = week_ago

        s = ''
        if increment > 0:
            s = '+'
        s += str(int(increment)) + ' cm'

        fill = 'white'
        emoji = ''
        if increment > 5:
            fill = 'green'
            emoji += '️↗️'
        if increment > 10:
            emoji += '️↗️'
        if increment > 15:
            emoji += '️↗️'
        if increment > 20:
            emoji += '️↗️'
        if increment < -5:
            fill = 'red'
            emoji += '️↘️'
        if increment < -10:
            emoji += '️↘️'
        if increment < -15:
            emoji += '️↘️'
        if increment < -20:
            emoji += '️↘️'
        if increment < 5 and increment > -5:
            emoji += '️='

        curr_y = y + 15
        if elements % 2 == 0:
            curr_x = left
            create_box_half(left, y, left+box_width, y+box_height)
           # w, h = text_aligned(name, x=left, y=y, _font=fnt_bigger)
           # text_aligned(f'{gruix}cm ({s})', x=left+w+50, y=y, _font=fnt_bold_small)
        else:
            curr_x = left+box_width+box_gap
            create_box_half(left+box_width+box_gap, y, left+box_width*2+box_gap, y+box_height)

        # Center name into the box
        title = name + ' ' + emoji
        _, _, w, h = d.textbbox((0, 0), title, font=fnt_bigger)
        w, h = text_aligned(title, x=curr_x + (box_width-w)/2, y=curr_y, _font=fnt_bigger)

        # Center gruix into the box
        gruix_txt = f'{int(gruix)}cm'
        _, _, w2, h2 = d.textbbox((0, 0), gruix_txt, font=fnt_bold_mid)
        _, h3 = text_aligned(gruix_txt, x=curr_x+(box_width-w2)/2, y=curr_y+h+30, _font=fnt_bold_mid)


        # Center increment into the box
        _, _, w, h = d.textbbox((0, 0), 'Increment', font=fnt)
        w, h = text_aligned('Increment:', x=curr_x+(box_width-w)/2, y=curr_y+h+h3+70, _font=fnt)
        _, _, w, h = d.textbbox((0, 0), s, font=fnt_bold_small)
        text_aligned(s, x=curr_x+(box_width-w)/2, y=curr_y+h+h3+100, _font=fnt_bold_small, fill=fill)

        #w4, _ = text_aligned('Increment:', x=left+50+w2+w3+20, y=y+h+20, _font=fnt)

        #text_aligned(s, x=left + 50+w2+w3+20+w4+20, y=y+h+20, _font=fnt_bold_small)

        if elements % 2 == 1:
            y += box_height + box_gap
        elements += 1

print(elements)

img.save('story.png')
