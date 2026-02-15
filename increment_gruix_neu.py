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
yesterday = now - datetime.timedelta(days=1)

def get_data_estacions(t):
    data_estacions = {'time': now.timestamp(), 'data': {}}
    for est in estacions:
        # For now only stations with snow thickness are considered
        #if not est['GN']:
        #    continue


        print(f"({est['name']}) Getting data for {t.day}-{t.month}-{t.year}...")
        raw_content = requests.get(
            URL_METEOCAT.format(
                dia=t.day,
                mes=t.month,
                year=t.year,
                codi=est['codi']
            )
        )


        soup = BeautifulSoup(raw_content.content, 'html.parser')

        try:


            tbody = soup.find(class_='tblperiode')
            # get the tbody tag, and then the first tr
            first_row = tbody.find('tr')
            # count all th with scope="col"
            tags = first_row.find_all('th', scope='col')


            has_gn = False
            gn_idx = 0
            #tags = tbody.find_all('span', class_='tooltip')
            for i, e in enumerate(tags):
                if i == 0:
                    continue
                i -= 1
                try:
                    text = e.find('span').text
                    if text == 'GN':
                        gn_idx = i
                        has_gn = True
                        break
                except:
                    print(f"({est['name']}) Exception: {e}")
                    continue

            if not has_gn:
                continue

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

                if i == gn_idx:
                    data[period]['snow_thickness'] = val
                    continue

                if (len(list(tags)) == 11):
                    data[period][CONTENT_NAMES_10[i]] = val
                elif (len(list(tags)) == 12):
                    data[period][CONTENT_NAMES_11[i]] = val
                else:
                    if i == 0:
                        print(f"({est['name']}) Invalid tag number ({len(list(tags))})")
                    continue
                
            data_estacions['data'][est['short-name']] = {'data': data, 'name': est['name'], 'updated_at': now.timestamp()}
        except Exception as e:
            print(f"({est['name']}) Exception: {e}")
            continue
    return data_estacions

#with open(f'docs/{now.day}-{now.month}-{now.year}.json', 'w') as f:
#    f.write(json.dumps(data_estacions))
today_data = get_data_estacions(now)
yesterday_data = get_data_estacions(yesterday)
one_year_ago_data = get_data_estacions(now-datetime.timedelta(days=365))
one_week_ago_data = get_data_estacions(now-datetime.timedelta(days=7))

gruixos_neu = {}

for sn in today_data['data'].keys():
    if (sn not in yesterday_data['data'].keys()):
        continue
    try:
        today_periods = len(today_data['data'][sn]['data'])
        tdata = today_data['data'][sn]['data'][today_periods-1]['snow_thickness']
        ydata = yesterday_data['data'][sn]['data'][today_periods-1]['snow_thickness']
    except:
        continue
    if tdata is None or ydata is None:
        try:
            today_periods = len(today_data['data'][sn]['data'])
            tdata = float(today_data['data'][sn]['data'][today_periods-3]['snow_thickness'])
            ydata = float(yesterday_data['data'][sn]['data'][today_periods-3]['snow_thickness'])
        except:
            continue
    snow_diff = tdata - ydata
    gruixos_neu[sn] = {}
    gruixos_neu[sn]['gruix'] = tdata
    gruixos_neu[sn]['name'] = today_data['data'][sn]['name']
    gruixos_neu[sn]['yesterday'] = snow_diff
    print(f'diff yasterday {sn}={snow_diff}')

for sn in today_data['data'].keys():
    if (sn not in one_year_ago_data['data'].keys()):
        continue
    try:
        today_periods = len(today_data['data'][sn]['data'])
        tdata = today_data['data'][sn]['data'][today_periods-1]['snow_thickness']
        ydata = one_year_ago_data['data'][sn]['data'][today_periods-1]['snow_thickness']
    except:
        continue
    if tdata is None or ydata is None:
        try:
            today_periods = len(today_data['data'][sn]['data'])
            tdata = float(today_data['data'][sn]['data'][today_periods-3]['snow_thickness'])
            ydata = float(one_year_ago_data['data'][sn]['data'][today_periods-3]['snow_thickness'])
        except:
            continue
    snow_diff = tdata - ydata

    if sn not in gruixos_neu.keys():
        gruixos_neu[sn] = {}
        gruixos_neu[sn]['name'] = today_data['data'][sn]['name']
        gruixos_neu[sn]['gruix'] = tdata
    gruixos_neu[sn]['year_ago'] = snow_diff

    print(f'diff one year ago {sn}={snow_diff}')

for sn in today_data['data'].keys():
    if (sn not in one_week_ago_data['data'].keys()):
        print(f'no one week ago data for {sn}')
        continue
    try:
        today_periods = len(today_data['data'][sn]['data'])
        tdata = today_data['data'][sn]['data'][today_periods-1]['snow_thickness']
        ydata = one_week_ago_data['data'][sn]['data'][today_periods-1]['snow_thickness']
    except Exception as e:
        print(f'Exception 1: {e}')
        continue
    if tdata is None or ydata is None:
        try:
            today_periods = len(today_data['data'][sn]['data'])
            tdata = float(today_data['data'][sn]['data'][today_periods-3]['snow_thickness'])
            ydata = float(one_week_ago_data['data'][sn]['data'][today_periods-3]['snow_thickness'])
        except Exception as e:
            print(f'Exception 2: {e}')
            continue
    snow_diff = tdata - ydata

    if sn not in gruixos_neu.keys():
        gruixos_neu[sn] = {}
        gruixos_neu[sn]['name'] = today_data['data'][sn]['name']
        gruixos_neu[sn]['gruix'] = tdata
    gruixos_neu[sn]['week_ago'] = snow_diff

    print(f'diff one week ago {sn}={snow_diff}')

print(gruixos_neu)
with open("docs/increment.json", 'w') as f:
    f.write(json.dumps(gruixos_neu))
