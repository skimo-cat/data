import requests
import datetime
import json

BASE_URL = 'https://lauegi.smartyplanet.com/smartis/smarti/ajax/{_from} 0:00/{_to} 23:59/{{"canals":[{{"smarti":{smarti},"canal":{canal}}}]}}/rang/0/1?text_smarti=0'
INCREMENTS_FILE = 'docs/increment.json'

estacions = {
    'comalada': {
        'name': 'Baqueira',
        'smarti': 771,
        'canal': 642
    },
}


# from/to: 2019-01-01
def get_data(smarti, canal, _from, _to):
    url = BASE_URL.format(
        smarti=smarti,
        canal=canal,
        _from=_from,
        _to=_to
    )
    r = requests.get(url)
    if r.status_code != 200:
        return None
    if r.json()['error_data'] == True:
        return None
    return r.json()


now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
yeasterday = now - datetime.timedelta(days=1)
week_ago = now - datetime.timedelta(days=7)
year_ago = now - datetime.timedelta(days=365)

strftime_format = '%Y-%m-%d'

increments = {}

for k in estacions.keys():
    # today
    data = get_data(
        estacions[k]['smarti'],
        estacions[k]['canal'],
        now.strftime(strftime_format),
        now.strftime(strftime_format)
    )

    try:
        today_value = float(data['canals'][0]['valors'][-1]['value'])
    except:
        print(f"Error getting today data for {k}")
        continue
        today_value = None

    # yesterday
    data = get_data(
        estacions[k]['smarti'],
        estacions[k]['canal'],
        yeasterday.strftime(strftime_format),
        yeasterday.strftime(strftime_format)
    )

    try:
        yesterday_value = float(data['canals'][0]['valors'][-1]['value'])
    except:
        print(f"Error getting yesterday data for {k}")
        yesterday_value = None

    # week ago
    data = get_data(
        estacions[k]['smarti'],
        estacions[k]['canal'],
        week_ago.strftime(strftime_format),
        week_ago.strftime(strftime_format)
    )

    try:
        week_ago_value = float(data['canals'][0]['valors'][-1]['value'])
    except:
        print(f"Error getting week ago data for {k}")
        week_ago_value = None

    # year ago
    data = get_data(
        estacions[k]['smarti'],
        estacions[k]['canal'],
        year_ago.strftime(strftime_format),
        year_ago.strftime(strftime_format)
    )

    try:
        year_ago_value = float(data['canals'][0]['valors'][-1]['value'])
    except:
        print(f"Error getting year ago data for {k}")
        year_ago_value = None

    if yesterday_value is not None or today_value is not None or week_ago_value is not None or year_ago_value is not None:
        increments[k] = {
            'name': estacions[k]['name']
            }

    if today_value is not None:
        increments[k]['gruix'] = int(today_value)

    if yesterday_value is not None:
        increments[k]['yesterday'] = int(today_value - yesterday_value)

    if week_ago_value is not None:
        increments[k]['week_ago'] = int(today_value - week_ago_value)

    if year_ago_value is not None:
        increments[k]['year_ago'] = int(today_value - year_ago_value)


with open(INCREMENTS_FILE, 'r') as f:
    raw_data = f.read()
    original_data = json.loads(raw_data)

    for k in increments.keys():
        original_data[k] = increments[k]

with open(INCREMENTS_FILE, 'w') as f:
    f.write(json.dumps(original_data))