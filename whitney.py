import requests
import json
from slackclient import SlackClient

with open('config.json') as config_file:
    config = json.loads(config_file.read())


def scan_permits():
    year = config['year']
    permit = config['permit']
    date = config['permit_date']
    scan_permit(permit['id'], permit['sub_id'], date)


def scan_permit(id, sub_id, date):
    print('scanning permit', id, sub_id, 'for year', date["year"], 'and month', date["month"])
    url = 'https://www.recreation.gov/api/permits/' + id + '/availability/month'
    date_string_scan = date["year"] + '-' + date["month"] + '-01T00:00:00.000Z'
    date_string_date = date["year"] + '-' + date["month"] + '-' + date["day"] + 'T00:00:00Z'
    params = {'start_date': date_string_scan, 'commercial_acct' : 'false', 'is_lottery' : 'false'}
    headers = {
        "User-Agent": "Trying to find a campsite"
    }
    request = requests.get(url, headers=headers, params=params)

    availability_on_date = json.loads(request.text)['payload']['availability'][sub_id]['date_availability'][date_string_date]

    print(availability_on_date, date_string_date)

    if(availability_on_date['remaining'] > 0):
        message = '<!channel> ' + str(availability_on_date['remaining']) + '/' + str(availability_on_date['total']) + ' available permits for <https://www.recreation.gov/permits/' + str(id) + '/registration/detailed-availability?type=overnight-permit&date=' + str(date["month"]) + '/' + str(date["day"]) + '/' + str(date["year"]) + '|' + str(id) + '> on ' + str(date["month"]) + '/' + str(date["day"]) + '/' + str(date["year"]) + '\n'
        slack_token = config['slack_token_pandola']
        channel = config['slack_channel_pandola']
        sc = SlackClient(slack_token)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=message,
            as_user=False
        )


scan_permits()