import numpy as np
import time
import json
import requests

chunks = [
    # Aiguestortes
    [
        # sw lat/lon
        [42.410880, 0.671115],

        # ne lat/lon
        [42.652629, 1.146639]
    ],
    # Aran
    [
        [42.620937, 0.647919], [42.846083, 1.183090]
    ],
# Pallars
    [
        [42.629471, 1.023201], [42.770720, 1.516951]
    ],
#Andorra
    [
        [42.418831, 1.324753], [42.674559, 1.843355]
    ],
# Cerdanya
    [
        [42.390966, 1.649324], [42.606226, 2.425650]
    ],
# Ter
    [
        [42.294035, 1.902037], [42.449619, 2.339498]
    ],

]

step_lat = 0.01
step_lon = 0.02
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


data = []

def id_in_data(rid):
    for x in data:
        if rid == x['id']:
            return True
    return False

for chunk in chunks:
    from_lat = chunk[0][0]
    to_lat   = chunk[1][0]
    from_lon = chunk[0][1]
    to_lon   = chunk[1][1]
    for lat in np.arange(from_lat, to_lat, step_lat):
        for lon in np.arange(from_lon, to_lon, step_lon):
            time.sleep(0.5)
            url = f'https://ca.wikiloc.com/wikiloc/find.do?event=popularWaypoints&sw={lat},{lon}&ne={lat+step_lat},{lon+step_lon}&z=20'
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                print(f'({r.status_code}) Error fetching url: {url}')
                continue

            rdata = r.json()
            for entry in rdata:
                if entry['pictogramId'] == 31:
                    # Refu
                    lat = entry['location']['lat']
                    lon = entry['location']['lon']
                    name = entry['name']
                    rid = entry['id']
                    if id_in_data(rid):
                        continue
                    data.append({
                        'name': name,
                        'lat': lat,
                        'lon': lon,
                        'id': rid
                    })

            print('Number of refus:', len(data))

# Remove wikiloc IDS
for idx, x in enumerate(data):
    x['id'] = idx

with open('refus.js', 'w+') as f:
    f.write(json.dumps(data))
