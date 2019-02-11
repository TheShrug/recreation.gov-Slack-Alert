from datetime import datetime
import requests
import json
from slackclient import SlackClient

with open('config.json') as config_file:
    config = json.loads(config_file.read())


def scan_all_campsites():
    year = config['year']
    for campsite_id in config['campsites']:
        for i in range(int(config['start_month']), int(config['end_month']) + 1):
            month = format(i, '02d')
            scan_campsite(campsite_id, year, month)


def found_availabilities(availabilities):

    message = ''
    for availability in availabilities:
        message += '<!channel> Availability at campground <https://www.recreation.gov/camping/campgrounds/' + availability[0] + '|' + availability[0] + '>:<https://www.recreation.gov/camping/campsites/' + availability[1] + '|' + availability[1] + '> on ' + availability[2] + '\n'

    slack_token = config['slack_token']
    channel = config['slack_channel']
    sc = SlackClient(slack_token)
    print(sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message,
        as_user=False
    ))


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
            if date_parse.weekday() == 5 and availability == 'Available':
                available_campsites.append((id, key, date_parse.strftime('%Y-%m-%d')))


available_campsites = []
scan_all_campsites()

if available_campsites.__len__() > 0:
    found_availabilities(available_campsites)


