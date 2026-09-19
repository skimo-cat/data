import os
import datetime
import json
from PIL import Image, ImageFont, ImageDraw
import geopandas as gpd
import matplotlib.pyplot as plt
from io import BytesIO
import subprocess

WIDTH = 1080
HEIGHT = 1920


fnt = ImageFont.truetype(os.path.join(os.getcwd(), 'insta/fonts/montserrat/Montserrat-Regular.ttf'), 35)
fnt_supersmall = ImageFont.truetype(os.path.join(os.getcwd(), 'insta/fonts/montserrat/Montserrat-Regular.ttf'), 25)
fnt_supersmall2 = ImageFont.truetype(os.path.join(os.getcwd(), 'insta/fonts/montserrat/Montserrat-Regular.ttf'), 30)
fnt_bigger = ImageFont.truetype(os.path.join(os.getcwd(), 'insta/fonts/montserrat/Montserrat-Regular.ttf'), 50)
fnt_bold = ImageFont.truetype(os.path.join(os.getcwd(), 'insta/fonts/montserrat/Montserrat-Bold.ttf'), 120)
fnt_bold_h2 = ImageFont.truetype(os.path.join(os.getcwd(), 'insta/fonts/montserrat/Montserrat-Bold.ttf'), 40)

def text_aligned(txt, fill='white', under=False, x=None, y=None, divide=2, _font=fnt, linewidth=10, d=None):
    _, _, w, h = d.textbbox((0, 0), txt, font=_font)
    if x is None:
        x = (WIDTH-w)/divide
    if y is None:
        y = (HEIGHT-h)/divide

    d.text((x, y), txt, font=_font, fill=fill)
    if under:
        d.line([(x, y + h + 20), (x + w, y + h + 20)], fill=(255,255,255), width=linewidth)

    return w, h

wcs_to_process = {
    #'pico-aneto': 'Cim de l\'Aneto',
    'bonaigua': 'Bonaigua',
    'porte-la-vignole': 'Porté',
    'niu-aliga': 'Niu de l\'Àliga',
    'boi-taull': 'Boí Taüll',
}

def generate_frame(webp_path, wc_name, framenum):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0x2C, 0x29, 0x29))
    d = ImageDraw.Draw(img)

    text_aligned(f'{wc_name}', under=False, y=150, _font=fnt_bold, linewidth=6, d=d)

    datestr_epoch = webp_path.split('/')[-1].split('-')[-1].split('.')[0]
    datestr = datetime.datetime.utcfromtimestamp(int(datestr_epoch)).strftime('%d/%m/%Y %H:%M')

    text_aligned(datestr, y=300, _font=fnt_supersmall2, d=d)


    pic = Image.open(webp_path)
# Scale the pic image to maixumum 1000 height (if necessary), then, crop it to a maximum width of 1080
    aspect_ratio = pic.width / pic.height
    pic = pic.resize((int(1000 * aspect_ratio), 1200), resample=Image.LANCZOS)
    if pic.width > 1080:
        pic = pic.crop((0, 0, 1080, pic.height))

    img.paste(pic, (0, 400))

    img.save(f'frames/{framenum}.png')

def clean_frames():
    for f in os.listdir('frames'):
        os.remove(f'frames/{f}')

def is_wc(filename, wc):
    filename_wcname = filename.split('/')[-1].split('.')[0].split('-')[:-1]
    if type(filename_wcname) == list:
        filename_wcname = '-'.join(filename_wcname)

    return filename_wcname in wc and filename.endswith('.webp')

clean_frames()

frame = 0
for wc, wc_name in wcs_to_process.items():
    # Get all elements in ../img/img/{wc}*.webp
    wc_files = [f for f in os.listdir(f'../img/img/') if is_wc(f, wc)][10:]
    wc_files.sort()
    for wc_file in wc_files:
        generate_frame(f'../img/img/{wc_file}', wc_name, frame)
        frame += 1

os.system('rm out.mp4')

# Now, we have all the frames in the `frames` folder. We can create a video with ffmpeg:
# ffmpeg -framerate 1 -i frames/%d.png -c:v libx264 -r 30 -pix_fmt yuv420p out.mp4
# This will create a video with 1 frame per second, and 30 frames per second in the output video.
# The video will be named `out.mp4`. You can adjust the parameters to match your needs.

# If you want to create a GIF instead, you can use ImageMagick:
# convert -delay 100 -loop 0 frames/*.png out.gif

subprocess.run(['ffmpeg', '-framerate', '5', '-i', 'frames/%d.png', '-c:v', 'libx264', '-r', '30', '-pix_fmt', 'yuv420p', 'out.mp4'])