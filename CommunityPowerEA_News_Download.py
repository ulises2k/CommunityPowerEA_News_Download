# Community Power News Download
# Original Idea: Alan Wong (forex-factory-web-scraper)
# Modified by @ulises2k
# v1.0 - 03/08/2022
#
import cloudscraper
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import re
import time
import csv
import calendar
import sys
import os
from os.path import expanduser
from os.path import exists

def getEventsCalendar(start_date, file_path):

    # Used to hold event time as not all event times have a time if multiple news events start at the same time
    event_time_holder = ''  # Holds event time of previous news event if it does not have one

    # Need cloudscraper to bypass cloudflare
    scraper = cloudscraper.create_scraper()

    # specify the url
    url = 'https://www.forexfactory.com/' + start_date

    # query the website and return the html to the variable ‘page’
    page = scraper.get(url).text

    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(page, 'html.parser')
    # Take out the <div> of name and get its value

    # Find the table containing all the data
    table = soup.find('table', class_='calendar__table')

    year = int(start_date[-4:])

    rows = table.find_all('tr', class_='calendar__row')
    for row in rows:

        if 'calendar__expand' in row.get('class'):
            continue

        if 'calendar__row--new-day' in row.get('class'):
            event_time_holder = ''

        if 'calendar__row--grey' in row.get('class'):
            calendar__date = row.find('td', class_='calendar__date').text.strip()
            if len(calendar__date) != 0:
                matchObj = re.search('([a-zA-Z]{3})([a-zA-Z]{3}) ([0-9]{1,2})', calendar__date)
                day_of_week = matchObj.group(1)
                month = strToNumMonth(matchObj.group(2))
                day = format(int(matchObj.group(3)), "02")
            print('-------------------------------------------------------------------------------')
            print("Day:" + str(day) + " Month:" + str(month) + " Year:" + str(year))
            print(row.text)


            calendar__time = row.find('td', class_='calendar__time').text.strip()
            calendar__currency = row.find('td', class_='calendar__currency').text.strip()
            calendar__impact = row.find('td', class_='calendar__impact').find('div', class_='calendar__impact-icon').find('span')['class'][0]
            calendar__event = row.find('td', class_='calendar__event').text.strip()
            calendar__actual = row.find('td', class_='calendar__actual').text.strip()
            calendar__forecast = row.find('td', class_='calendar__forecast').text.strip()
            calendar__previous = row.find('td', class_='calendar__previous').text.strip()

            currency = calendar__currency
            impact = calendar__impact
            event = calendar__event
            previous = calendar__previous
            forecast = calendar__forecast
            actual = calendar__actual
            event_time = calendar__time

            if impact == 'high':
                impact = '3'
            elif impact == 'medium':
                impact = '2'
            elif impact == 'low':
                impact = '1'
            else:
                impact = '0'

            try:
                # Regex to match time in the format HH:MMam/pm
                matchObj = re.search('([0-9]+)(:[0-9]{2})([a|p]m)', event_time)
                if(matchObj != None):
                    # Matches the first group in the regex which is the hour in HH format
                    event_time_hour = matchObj.group(1)
                    # Matches the second group in the regex which is the minutes in :MM format
                    event_time_minutes = matchObj.group(2)
                    # Matches the third group in the regex which is either 'am' or 'pm'
                    am_or_pm = matchObj.group(3)
                elif(re.search('All Day', event_time)):
                    event_time_hour = '12'
                    event_time_minutes = ':00'
                    am_or_pm = 'am'
                    event = event + " (All Day)"
                elif(re.search('Day [0-9]+', event_time)):
                    event_time_hour = '12'
                    event_time_minutes = ':00'
                    am_or_pm = 'am'
                    event = event + " (" + event_time + ")"
                else:
                    # else no time and use previous events time and write to file
                    # date_time;currency;impact;name;previous;forecast;actual;actual_time;revised;revised_time
                    with open(file_path, 'a') as file:
                        file.write('{};{};{};{};{};{};{};{};{};{}\n'.format(event_date_time, currency, impact, event, previous, forecast, actual, '', '', ''))
                    continue

                event_date = str(year) + '.' + month + '.' + day

                # If the event time is not empy and not 'All day' then we have found a time
                if event_time != '' and event_time != 'All Day' and not ('Day' in event_time):
                    event_time_24hs = datetime.strftime(datetime.strptime(event_time_hour + event_time_minutes + " " + am_or_pm, '%I:%M %p'), "%H:%M")

                    # Set the event_time_holder to this event_time so any subsequent events also have the same time as this event
                    event_time_holder = event_time_24hs

                    # As forex factory only provides a time for the first event
                    event_date_time = '{} {}'.format(event_date, event_time_holder + ':00')
                else:
                    if event_time_holder == '':
                        event_time_holder = '00:00'

                    # event_time_holder remains the same and should have the value of the first event which was assigned a time
                    event_date_time = '{} {}'.format(event_date, event_time_holder + ':00')

            except Exception as e:
                print("There was an error: " + e)

            # date_time;currency;impact;name;previous;forecast;actual;actual_time;revised;revised_time
            with open(file_path, 'a') as file:
                file.write('{};{};{};{};{};{};{};{};{};{}\n'.format(event_date_time, currency, impact, event, previous, forecast, actual, '', '', ''))


def strToNumMonth(month):
    #
    # Function to convert Str Month into an Int
    #
    if(month == 'Jan'):
        return '01'
    elif(month == "Feb"):
        return '02'
    elif(month == "Mar"):
        return '03'
    elif(month == "Apr"):
        return '04'
    elif(month == "May"):
        return '05'
    elif(month == "Jun"):
        return '06'
    elif(month == "Jul"):
        return '07'
    elif(month == "Aug"):
        return '08'
    elif(month == "Sep"):
        return '09'
    elif(month == "Oct"):
        return '10'
    elif(month == "Nov"):
        return '11'
    elif(month == "Dec"):
        return '12'
    return None


if __name__ == "__main__":
    #years = range(2022, 2023, 1)
    #months = ['Aug']

    years = range(2007, 2023, 1)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    abs_path = os.path.abspath(__file__)
    cwd = os.path.dirname(abs_path)
    parent_dir = os.path.dirname(cwd)


    for y in years:
        for m in months:

            file_path = expanduser("~") + '\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\News\\FF\\' + str(y) + '.' + str(strToNumMonth(m)) + '.01.csv'

            if exists(file_path + '.old'):
                os.remove(file_path + '.old')

            if exists(file_path):
                os.rename(file_path, file_path + '.old')

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'a+') as file:
                # Needs to write an empty line so that file is opened and getEventsCalendar can append to the file
                file.write('')
            getEventsCalendar("calendar?month=" + m + "." + str(y), file_path)


# https://www.forexfactory.com/calendar?month=Aug.2022
