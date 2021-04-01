import json
import os
import pytz
import requests
from datetime import datetime
from geopy import distance
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def handler(event, context):
    state = event['state'] if 'state' in event else 'NE'
    url = 'https://www.vaccinespotter.org/api/v0/states/{state}.json'.format(state=state)
    r = requests.get(url)

    if r.status_code == 200:
        json_data = json.loads(r.text)
        locations = json_data['features']

        nearby_locations = []
        search_coordinates = (event['latitude'], event['longitude'])
        for location in locations:
            if location['properties']['provider'] != 'hyvee':
                location_coordinates = (location['geometry']['coordinates'][1], location['geometry']['coordinates'][0])
                if distance.distance(search_coordinates, location_coordinates).miles <= event['radius']:
                    nearby_locations.append(location)

        locations_with_openings = []
        # Return at least one location when testing
        if len(nearby_locations) and 'test' in event and event['test']:
            locations_with_openings.append(nearby_locations[0])

        for location in nearby_locations:
            if location['properties']['appointments_available']:
                locations_with_openings.append(location)

        if len(locations_with_openings):
            print('## Openings Available')
            print(locations_with_openings)

            try:
                # build the Slack message
                blocks = [get_title_block()]
                for location in locations_with_openings:
                    blocks.append(get_location_block(location))
                    blocks.append(get_actions_block(location))
                    blocks.append(get_divider_block())
                blocks.append(get_time_block())

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
            'text': ':alert: <!here> *Vaccines Available* :alert:\n\nThe following locations have COVID-19 vaccination appointments :covid-19: :syringe: available now!'
        }
    }


def get_location_block(location):
    name = '{name} {provider}'.format(name=location['properties']['name'], provider=location['properties']['provider_brand_name'])
    return {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': '*{name}*\n{address}\n{city}, {state} {zip}'.format(name=name,
                                                                      address=location['properties']['address'],
                                                                      city=location['properties']['city'],
                                                                      state=location['properties']['state'],
                                                                      zip=location['properties']['postal_code'])
        }
    }


def get_actions_block(location):
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
                'url': location['properties']['url']
            }
        ]
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
