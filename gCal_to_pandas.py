from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from quickstart import get_credentials
import datetime

import pandas as pd

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow()
    look_back_max = 365
    last_year = (now - datetime.timedelta(days=364)).isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting 10 events from the last year')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=last_year, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        # for k in event:
        #     detail_str = str(k) + ": " + str(event[k])
        #     print(detail_str)

def events_per_interval(interval = 7, look_back_max = 365):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    events_per_interval = []

    now = datetime.datetime.utcnow()
    search_start = (now - datetime.timedelta(days=look_back_max))
    intervals = int(look_back_max/interval)
    interval_start = search_start
    interval_end = search_start + datetime.timedelta(days=interval)
    for i in range(intervals):
        # add this before using in the API request
        # .isoformat() + 'Z' # 'Z' indicates UTC time
        interval_str = 'Getting events for ' + str(interval_start) + ' to ' + str(interval_end)
        print(interval_str)
        eventsResult = service.events().list(
            calendarId='primary',
            timeMin=interval_start.isoformat() + 'Z',
            timeMax=interval_end.isoformat() + 'Z',
            #maxResults=10,
            singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
        num_events = len(events)
        end_str = str(num_events) + " events found"
        print(end_str)

        line = [i, interval_start, interval_end, num_events]
        events_per_interval.append(line)
        interval_start = interval_start + + datetime.timedelta(days=interval)
        interval_end = interval_end + datetime.timedelta(days=interval)
    return pd.DataFrame(events_per_interval, columns = ['Interval', 'Interval Start', 'Interval End', 'Events'])

if __name__ == '__main__':
    # main()
    events = events_per_interval()
