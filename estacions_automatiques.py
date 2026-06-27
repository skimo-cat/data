from bs4 import BeautifulSoup
import datetime
import json
import requests
import shutil

URL_METEOCAT = 'https://www.meteo.cat/observacions/xema/dades?codi={codi}&dia={year}-{mes:02d}-{dia:02d}T00:00Z'

CONTENT_NAMES_10 = [
    'avg_temp', # C
    'max_temp', # C
    'min_temp', # C
    'rel_hum',  # %
    'prec',     # mm
    'snow_thickness',  # cm
    'avg_wind_speed',  # km/h
    'avg_wind_dir',    # degrees
    'max_wind_speed',  # km/h
    'solar_irradiance' # W/m^2
]

CONTENT_NAMES_11 = [
    'avg_temp', # C
    'max_temp', # C
    'min_temp', # C
    'rel_hum',  # %
    'prec',     # mm
    'snow_thickness',  # cm
    'avg_wind_speed',  # km/h
    'avg_wind_dir',    # degrees
    'max_wind_speed',  # km/h
    'pressure',        # hPa
    'solar_irradiance' # W/m^2
]

CONTENT_NAMES_NO_GC = [
    'avg_temp', # C
    'max_temp', # C
    'min_temp', # C
    'rel_hum',  # %
    'prec',     # mm
    'avg_wind_speed',  # km/h
    'avg_wind_dir',    # degrees
    'max_wind_speed',  # km/h
    'solar_irradiance' # W/m^2
]

with open('docs/estacions.json', 'r') as f:
    estacions = json.loads(f.read())

# TODO: Make async
now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
data_estacions = {'time': now.timestamp(), 'data': {}}
for est in estacions:
    # For now only stations with snow thickness are considered
    #if not est['GN']:
    #    continue


    raw_content = requests.get(
        URL_METEOCAT.format(
            dia=now.day,
            mes=now.month,
            year=now.year,
            codi=est['codi']
        )
    )

    soup = BeautifulSoup(raw_content.content, 'html.parser')


    try:
        tbody = soup.find(class_='tblperiode')

        has_gn = False
        tags = tbody.find_all('span', class_='tooltip')
        print(f"tooltips: {len(list(tags))}")
        for e in tags:
            if e.text == 'GN':
                has_gn = True
                break

        if not has_gn:
            print(f"Estació {est['name']} NO té GN")
            continue

        print(f"Estació {est['name']} té GN")

        data = []

        for idx, elem in enumerate(tbody.find_all('td')):
            period = idx//(len(list(tags))-1)
            i = idx%(len(list(tags))-1)
            if i == 0:
                data.append({'period': period})
            """
            if i == 0:
                print("")
                print(f"Period {period}: ", end="")
            print(elem.text, " ", end="");
            """
            # float o '(s/d)'
            val = elem.text
            try:
                val = float(val)
            except ValueError:
                val = None

            if (len(list(tags)) == 11):
                data[period][CONTENT_NAMES_10[i]] = val
            elif (len(list(tags)) == 12):
                data[period][CONTENT_NAMES_11[i]] = val
            else:
                print(f"Invalid tag number ({len(list(tags))})")
                continue
            
        data_estacions['data'][est['short-name']] = {'data': data, 'name': est['name']}

    except:
        print(f"Estació {est['name']} no té dades")
        continue

#with open(f'docs/{now.day}-{now.month}-{now.year}.json', 'w') as f:
#    f.write(json.dumps(data_estacions))

gruix_neu = {}
for est_n in data_estacions['data'].keys():
    for i in data_estacions['data'][est_n]['data'][::-1]:
        if i['snow_thickness'] is None:
            continue
        else:
            gruix_neu[est_n] = {
                    'gruix': i['snow_thickness'],
                    }
            for e in estacions:
                if e['short-name'] == est_n:
                    gruix_neu[est_n]['lat'] = e['lat']
                    gruix_neu[est_n]['lon'] = e['lon']
                    break
            break


with open(f'docs/GN.json', 'w') as f:
    f.write(json.dumps(gruix_neu))

#print(data_estacions['data']['certascan'])
print(gruix_neu)
