from datetime import datetime
import requests
import json
import pickle
import collections
from slackclient import SlackClient

with open('config.json') as config_file:
    config = json.loads(config_file.read())

Site = collections.namedtuple('Site', 'campground, campsite, date')


def scan_all_campsites():
    year = config['year']
    for campsite_id in config['campsites']:
        for i in range(int(config['start_month']), int(config['end_month']) + 1):
            month = format(i, '02d')
            scan_campsite(campsite_id, year, month)


def found_availabilities(availabilities):
    message = ''
    for availability in availabilities:
        message += '<!channel> New availability at campground <https://www.recreation.gov/camping/campgrounds/' + availability.campground + '|' + availability.campground + '>:<https://www.recreation.gov/camping/campsites/' + availability.campsite + '|' + availability.campsite + '> on ' + availability.date + '\n'

    slack_token = config['slack_token']
    channel = config['slack_channel']
    sc = SlackClient(slack_token)
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message,
        as_user=False
    )


def scan_campsite(id, year, month):
    print('scanning campsite', id, year, month)
    url = 'https://www.recreation.gov/api/camps/availability/campground/' + id + '/month'
    params = {'start_date': year + '-' + month + '-01T00:00:00.000Z'}
    headers = {
        "User-Agent": "Trying to find a campsite"
    }
    request = requests.get(url, headers=headers, params=params)

    campsites = json.loads(request.text)['campsites']
    for campsite in campsites.items():
        key = campsite[0]
        availabilities = campsite[1]['availabilities']
        for date, availability in availabilities.items():
            date_parse = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
            site = Site(id, key, date_parse.strftime('%Y-%m-%d'))
            if date_parse.weekday() == int(config['dayofweek']) and availability == 'Available' and site_not_in_pickle(site):
                add_site_to_pickle(site)
                newly_available_campsites.append(site)


def site_not_in_pickle(site):
    try:
        availabilities_pickle = pickle.load(open('availabilities.pickle', 'rb'))
        print(availabilities_pickle)
    except(EOFError, FileNotFoundError) as e:
        availabilities_pickle = set()
        pickle.dump(availabilities_pickle, open('availabilities.pickle', 'wb'))
    if site in availabilities_pickle:
        return False
    else:
        return True


def add_site_to_pickle(site):
    availabilities_pickle = pickle.load(open('availabilities.pickle', 'rb'))
    availabilities_pickle.add(site)
    pickle.dump(availabilities_pickle, open('availabilities.pickle', 'wb'))


newly_available_campsites = []
scan_all_campsites()

if newly_available_campsites.__len__() > 0:
    found_availabilities(newly_available_campsites)
