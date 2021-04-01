import json
import os
import pytz
import requests
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def handler(event, context):
    url = 'https://www.hy-vee.com/my-pharmacy/api/graphql'
    query = '''
        query SearchPharmaciesNearPointWithCovidVaccineAvailability($latitude: Float!, $longitude: Float!, $radius: Int! = 10) {
          searchPharmaciesNearPoint(latitude: $latitude, longitude: $longitude, radius: $radius) {
            distance
            location {
              locationId
              name
              nickname
              phoneNumber
              businessCode
              isCovidVaccineAvailable
              covidVaccineEligibilityTerms
              address {
                line1
                line2
                city
                state
                zip
                latitude
                longitude
                __typename
              }
              __typename
            }
            __typename
          }
        }
    '''
    variables = {
        'radius': event['radius'],
        'latitude': event['latitude'],
        'longitude': event['longitude']
    }
    r = requests.post(url, json={'query': query, 'variables': variables})

    locations_with_openings = []
    if r.status_code == 200:
        json_data = json.loads(r.text)
        locations = json_data['data']['searchPharmaciesNearPoint']

        if len(locations) and 'test' in event and event['test']:
            locations_with_openings.append(locations[0])

        for location in locations:
            if location['location']['isCovidVaccineAvailable']:
                locations_with_openings.append(location)

        if len(locations_with_openings):
            print('## Openings Available')
            print(locations_with_openings)

            try:
                # build the Slack message
                blocks = [get_title_block()]
                for location in locations_with_openings:
                    blocks.append(get_location_block(location['location']))
                    blocks.append(get_divider_block())
                blocks.append(get_time_block())
                blocks.append(get_actions_block())

                # send the Slack message
                client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
                slack_response = client.chat_postMessage(channel=event['channel'], blocks=blocks)

                # log the Slack Response
                print('## Slack Response')
                print(slack_response)
            except SlackApiError as e:
                # Log error message
                print('## Slack Message Error')
                print(e.response['error'])

        else:
            print('## No Openings Available')

def get_title_block():
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': ':alert: <!here> *Vaccines Available* :alert:\n\nThe following :hyvee: locations have COVID-19 vaccination appointments :covid-19: :syringe: available now!'
        }
    }

def get_location_block(location):
    name = location['nickname'] if location['nickname'] else location['name']
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': '*{name}*\n{line1}\n{city}, {state} {zip}'.format(name=name, line1=location['address']['line1'], city=location['address']['city'], state=location['address']['state'], zip=location['address']['zip'])
        }
    }

def get_divider_block():
    return {
        'type': 'divider'
    }

def get_time_block():
    cst = pytz.timezone('US/Central')
    dt = datetime.now(cst)

    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': '_Posted {date} CST_'.format(date=dt.strftime('%d %b %Y %I:%M:%S %p'))
        }
    }

def get_actions_block():
    return {
        'type': 'actions',
        'elements': [
            {
                'type': 'button',
                'text': {
                    'type': 'plain_text',
                    'emoji': True,
                    'text': 'Register Now'
                },
                'style': 'primary',
                'url': 'https://www.hy-vee.com/my-pharmacy/covid-vaccine-consent'
            }
        ]
    }
