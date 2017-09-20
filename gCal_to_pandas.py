from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from quickstart import get_credentials
import datetime
import pytz
import pandas as pd
import matplotlib.pyplot as plt

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
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        print(calendar_list_entry['id'])
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break

    now = datetime.datetime.utcnow()
    look_back_max = 365
    last_year = (now - datetime.timedelta(days=364)).isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting 10 events from the last year')
    eventsResult = service.events().list(
        calendarId='primary',
        timeMin=last_year, maxResults=10, singleEvents=True,
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

def events_per_interval(interval = 7, look_back_max = 365, cal_ID = 'primary'):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    events_per_interval = []
    # now = datetime.datetime.utcnow()
    today = datetime.datetime.now().date()
    midnight = datetime.datetime.combine(today, datetime.time(0, 0))
    # search_end = midnight.astimezone(pytz.utc)
    search_start = (midnight - datetime.timedelta(days=look_back_max))
    intervals = int(look_back_max/interval)
    interval_start = search_start
    interval_end = search_start + datetime.timedelta(days=0.99*interval)
    for i in range(intervals):
        # add this before using in the API request
        # .isoformat() + 'Z' # 'Z' indicates UTC time
        interval_str = 'Getting events for ' + str(interval_start) + ' to ' + str(interval_end)
        print(interval_str)
        eventsResult = service.events().list(
            calendarId=cal_ID,
            timeMin=interval_start.isoformat() + 'Z',
            timeMax=interval_end.isoformat() + 'Z',
            #maxResults=10,
            singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        labels = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            labels.append(event['summary'])
        num_events = len(events)
        end_str = str(num_events) + " events found"
        print(end_str)

        line = [i, interval_start, interval_end, num_events, labels]
        events_per_interval.append(line)
        interval_start = interval_start + + datetime.timedelta(days=interval)
        interval_end = interval_end + datetime.timedelta(days=interval)
    return pd.DataFrame(events_per_interval, columns = ['interval_Num', 'start', 'end', 'num_Events', 'events'])

if __name__ == '__main__':
    # main()
    holidays = events_per_interval(interval = 1, cal_ID = 'en.usa#holiday@group.v.calendar.google.com')
    # acquire holidays on a daily basis for entire look_back_interval
    # prepare label sequence, plot on (0,x) where x is day
    # daily_events = events_per_interval(interval=1)
    # weekly_events = events_per_interval()
    # biweekly_events = events_per_interval(interval=14)
    # monthly_events = ....
    # quarterly_events = ....
    # labels = ['point{0}'.format(i) for i in range(N)]
    #
    # plt.subplots_adjust(bottom = 0.1)
    # plt.scatter(
    #     data[:, 0], data[:, 1], marker='o', c=data[:, 2], s=data[:, 3] * 1500,
    #     cmap=plt.get_cmap('Spectral'))
    #
    # for label, x, y in zip(labels, data[:, 0], data[:, 1]):
    #     plt.annotate(
    #         label,
    #         xy=(x, y), xytext=(-20, 20),
    #         textcoords='offset points', ha='right', va='bottom',
    #         bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
    #         arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

    # plt.plot(7*weekly_events['Interval'], weekly_events['Events'])
    # plt.plot(14*biweekly_events['Interval'], biweekly_events['Events'])
    # plt.show()
