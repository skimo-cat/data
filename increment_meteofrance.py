import requests
import datetime
import json
from bs4 import BeautifulSoup

# Month from 0 to 11
METEOCIEL_URL = 'https://www.meteociel.fr/temps-reel/obs_villes.php?code2={codi_estacio}&jour2={dia}&mois2={mes}&annee2={any}'
INCREMENTS_FILE = 'docs/increment.json'

ESTACIONS = {
    'puigmal': 66067402,
}

NOM_ESTACIONS = {
    'puigmal': 'Puigmal',
}

def get_today_d_m_y():
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    return now.day, (now.month-1), now.year

def get_yesterday_d_m_y():
    yesterday = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(days=1)
    return yesterday.day, (yesterday.month-1), yesterday.year

def get_week_ago_d_m_y():
    week_ago = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(days=7)
    return week_ago.day, (week_ago.month-1), week_ago.year

def get_year_ago_d_m_y():
    year_ago = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(days=365)
    return year_ago.day, (year_ago.month-1), year_ago.year

def parse_data_from_src(src):
    data = []
    for d in src.split('&'):
        if d.startswith('data'):
            data.append(int(d.split('=')[1]))
    # Data is in reverse order
    data.reverse()
    return data

def get_gn(codi_estacio):
    ret = {}

    # Get today data
    d, m, y = get_today_d_m_y()
    r = requests.get(METEOCIEL_URL.format(codi_estacio=codi_estacio, dia=d, mes=m, any=y))
    soup = BeautifulSoup(r.text, 'html.parser')
    # Find the image which alt starts with Courbe de la hauteur de neige
    gn_img = soup.find('img', alt=lambda x: x and x.startswith('Courbe de la hauteur de neige'))
    # get the src attribute
    gn_src = gn_img['src']
    data = parse_data_from_src(gn_src)
    ret['gruix'] = float(data[-1])

    # Get yesterday data
    try:
        d, m, y = get_yesterday_d_m_y()
        r = requests.get(METEOCIEL_URL.format(codi_estacio=codi_estacio, dia=d, mes=m, any=y))
        soup = BeautifulSoup(r.text, 'html.parser')
        # Find the image which alt starts with Courbe de la hauteur de neige
        gn_img = soup.find('img', alt=lambda x: x and x.startswith('Courbe de la hauteur de neige'))
        # get the src attribute
        gn_src = gn_img['src']
        data = parse_data_from_src(gn_src)
        ret['yesterday'] = ret['gruix'] - data[-1]
    except:
        print("Error getting yesterday data")

    # Get week ago data
    try:
        d, m, y = get_week_ago_d_m_y()
        r = requests.get(METEOCIEL_URL.format(codi_estacio=codi_estacio, dia=d, mes=m, any=y))
        soup = BeautifulSoup(r.text, 'html.parser')
        # Find the image which alt starts with Courbe de la hauteur de neige
        gn_img = soup.find('img', alt=lambda x: x and x.startswith('Courbe de la hauteur de neige'))
        # get the src attribute
        gn_src = gn_img['src']
        data = parse_data_from_src(gn_src)
        ret['week_ago'] = ret['gruix'] - data[-1]
    except:
        print("Error getting week ago data")

    # Get year ago data
    try:
        d, m, y = get_year_ago_d_m_y()
        r = requests.get(METEOCIEL_URL.format(codi_estacio=codi_estacio, dia=d, mes=m, any=y))
        soup = BeautifulSoup(r.text, 'html.parser')
        # Find the image which alt starts with Courbe de la hauteur de neige
        gn_img = soup.find('img', alt=lambda x: x and x.startswith('Courbe de la hauteur de neige'))
        # get the src attribute
        gn_src = gn_img['src']
        data = parse_data_from_src(gn_src)
        ret['year_ago'] = ret['gruix'] - data[-1]
    except:
        print("Error getting year ago data")

    return ret


increments = {}
for estacio in ESTACIONS:
    print(f"Getting data for {estacio}...")
    ret = get_gn(ESTACIONS[estacio])
    ret['name'] = NOM_ESTACIONS[estacio]
    increments[estacio] = ret


with open(INCREMENTS_FILE, 'r') as f:
    raw_data = f.read()
    original_data = json.loads(raw_data)

    for k in increments.keys():
        original_data[k] = increments[k]

with open(INCREMENTS_FILE, 'w') as f:
    f.write(json.dumps(original_data))