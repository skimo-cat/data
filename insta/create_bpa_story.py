import os
import datetime
import json
from PIL import Image, ImageFont, ImageDraw
import geopandas as gpd
import matplotlib.pyplot as plt
from io import BytesIO

WIDTH = 1080
HEIGHT = 1920

img = Image.new('RGB', (WIDTH, HEIGHT), color=(0x2C, 0x29, 0x29))
d = ImageDraw.Draw(img)

fnt = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Regular.ttf'), 35)
fnt_supersmall = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Regular.ttf'), 25)
fnt_supersmall2 = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Regular.ttf'), 30)
fnt_bigger = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Regular.ttf'), 50)
fnt_bold = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Bold.ttf'), 120)
fnt_bold_h2 = ImageFont.truetype(os.path.join(os.getcwd(), 'fonts/montserrat/Montserrat-Bold.ttf'), 40)

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


# Adding title and basic info
#text_aligned("Perill d'allaus", y=1870, _font=fnt_supersmall)
X = 480
text_aligned('Perill d\'allaus', under=False, y=110, _font=fnt_bold, linewidth=6)
text_aligned('Llegeix amb atenció el BPA oficial', y=240, x=X, _font=fnt_supersmall)
text_aligned('Planifica amb eines com ATESMAPS', y=280, x=X, _font=fnt_supersmall)
text_aligned('Porta sempre el material de seguretat', y=320, x=X, _font=fnt_supersmall)

now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

# Load GeoJSON data with avalanche zones
geojson_file = 'shapes/zones.geojson'
gdf = gpd.read_file(geojson_file)

data = json.load(open('bpa-sample.json'))

# Step 3: Create a small Matplotlib figure for the map
my_dpi = 300
fig, ax = plt.subplots(figsize=(1450/my_dpi, 1000/my_dpi), dpi=my_dpi)

# Match zones from GeoJSON with their danger level in `perill.json`
def get_danger_color(danger_level):
    # You can adjust the color scheme to match your preference
    if danger_level == 1:
        return 'green'
    elif danger_level == 2:
        return 'yellow'
    elif danger_level == 3:
        return 'orange'
    elif danger_level == 4:
        return 'red'
    elif danger_level == 5:
        return 'purple'
    else:
        return 'gray'

# Add color to each zone based on danger level
#gdf['danger_level'] = 1#gdf['zone_id'].map(lambda zone: danger_data.get(str(zone), {}).get('danger', 0))

for idx, row in gdf.iterrows():
    curr_data = None
    for obj in data:
        if row['name'] in obj['nom_zona']:
            curr_data = obj
    if not curr_data is None:
        curr_danger = curr_data['grau_perill_primari']
        if curr_danger is None:
            curr_danger = 0
        else:
            curr_danger = int(curr_danger)
    else:
        curr_danger = 0
    gdf.loc[idx, 'danger_level'] = int(curr_danger)
    gdf.loc[idx, 'color'] = get_danger_color(int(curr_danger))
    textcolor = 'white' if curr_danger < 2 else 'black'
    gdf.loc[idx, 'textcolor'] = textcolor

# Plot the zones with danger levels
gdf.plot(ax=ax, color=gdf['color'], edgecolor='black', linewidth=1)

# Annotate the name of each region
for idx, row in gdf.iterrows():
    plt.annotate(text=row['name'], xy=row['geometry'].centroid.coords[0], color=row['textcolor'], fontsize=8, ha='center')

# Add data from 'andorra_borders.geojson' to the map
# borders = gpd.read_file('shapes/andorra_borders.geojson')
# Plot with black borderline
#borders.plot(ax=ax, color='gray', linewidth=1, edgecolor='black')
# plt.annotate(text='Andorra', xy=(1.57, 42.54), color='white', fontsize=8, ha='center')

#france = gpd.read_file('france.geojson')
#france.plot(ax=ax, color='#2c2929', linewidth=1, edgecolor='black')

# Remove axis for a clean look
ax.set_axis_off()

# Save the Matplotlib figure to a BytesIO object as a PNG
buf = BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
buf.seek(0)

# Open the Matplotlib image as a Pillow image
map_image = Image.open(buf)

# Paste the map onto the Instagram story image (adjust position and size)
position = (-20, 270)  # Adjust positioning based on your layout
img.paste(map_image, position, map_image)

# Create list of regios
regions = gdf['name'].unique()
regions = list(regions) + ['Andorra']
print(regions)


SEPARATOR_PX = 130
START_Y = 850
START_X = 250
for idx, region in enumerate(regions):
    curr_data = None
    for obj in data:
        if region in obj['nom_zona']:
            curr_data = obj
    #print(curr_data)

    if not curr_data is None:
        curr_danger = curr_data['grau_perill_primari']
    else:
        curr_danger = 0
    imgs = {
        0: 'images/9_PasdinfoV1.png',
        1: 'images/1_transparent.png',
        2: 'images/2_transparent.png',
        3: 'images/3_transparent.png',
        4: 'images/4_transparent.png',
        5: 'images/5_transparent.png',
    }

    img_danger = Image.open(imgs[int(curr_danger)])
    # Make 100px x 100px
    img_danger = img_danger.resize((80*2, 56*2))
    img.paste(img_danger, (70, START_Y + 50 + idx*SEPARATOR_PX - 50), img_danger)

    if idx != 0:
        # print separator line
        d.line([(50, START_Y + idx*SEPARATOR_PX- 10), (WIDTH - 50, START_Y + idx*SEPARATOR_PX- 10)], fill=(255,255,255), width=3)
    text_aligned(region, y=START_Y + idx*SEPARATOR_PX, x=START_X, divide=1, _font=fnt_bold_h2)
    # description of the risk
    if not curr_data is None:
        desc = curr_data['perill_text']
        if desc is None:
            desc = "Sense dades"
    else:
        desc = "Sense dades"
    text_aligned(desc, y=START_Y + idx*SEPARATOR_PX + 50, x=START_X, divide=1, _font=fnt_supersmall, fill='white')


# Save the final story
img.save('avalanche_story.png')
buf.close()

print("Instagram story saved as 'avalanche_story.png'")