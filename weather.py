import requests
import datetime
import re
import os
from dotenv import load_dotenv
from flask import request

from global_variables import nlp

# Get weather API key
path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(path):
    load_dotenv(path)
    WEATHER_APP_ID = os.environ.get('WEATHER_APP_ID')

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]
wait_for_geolocation = False


def get_user_geolocation() -> tuple:
    # Make a request
    url = f'http://ip-api.com/json/{request.remote_addr}'
    response = requests.get(url=url)
    json_response = response.json()

    coords = [json_response["lat"], json_response["lon"]]
    city = json_response["city"]
    return coords, city


def get_geopolitical_entity_from_text(text) -> str:
    doc = nlp(text)

    for entity in doc.ents:  # Iterate through all recognized entities (like names, places etc.)
        if entity.label_ == "GPE":  # This is a geopolitical entity
            geopolitical_entity = entity.text

            # Capitalize the name of the geopolitical entity
            return ' '.join(word.capitalize() for word in geopolitical_entity.split())


def get_geopolitical_entity_coords(geopolitical_entity):
    # Make a request
    url = 'http://geocode-maps.yandex.ru/1.x/'
    params = {'apikey': '40d1649f-0493-4b70-98ba-98533de7710b', 'geocode': geopolitical_entity,
              'format': 'json'}
    response = requests.get(url, params)
    json_response = response.json()

    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    coords = toponym["Point"]["pos"].split()
    return coords


def get_delta_days_from_text(text) -> (int, str):
    doc = nlp(text)

    for entity in doc.ents:  # Iterate through all recognized entities (like names, places etc.)
        if entity.label_ == "DATE":  # The entity is a date
            if entity.text == "tomorrow":
                return 1, entity.text  # The date is the next day

            if entity.text.lower() in WEEKDAYS:
                # Get the index of the day of the week from the message
                forecast_weekday_int = WEEKDAYS.index(entity.text)

                # Get the index of current day of the week
                cur_weekday_int = datetime.date.today().weekday()

                return (forecast_weekday_int - cur_weekday_int) % 7

            else:
                year_pattern = r"\D*(\d{4})\D*"
                year = re.findall(year_pattern, entity.text)

                month_pattern = r"[a-zA-Z]*"
                month = re.findall(month_pattern, entity.text)

                day_pattern = r"\D*(\d{1,2})\D*"
                day = re.findall(day_pattern, entity.text)

                if not month or not day:
                    return 0, ''

                # Get the index of the month from the message
                month = MONTHS.index([month_.lower() for month_ in month
                                      if month_.lower() in MONTHS][0]) + 1

                day = int(day[0])

                if not year:
                    # If prediction date within current year is current date or later
                    if datetime.date(datetime.date.today().year, month, day) \
                            >= datetime.date.today():
                        year = datetime.date.today().year
                    else:
                        year = datetime.date.today().year + 1
                else:
                    year = int(year[0])

                forecast_date = datetime.date(year, month, day)
                cur_date = datetime.date.today()
                return (forecast_date - cur_date).days, entity.text

    return 0, ''


def get_weather(user_message_text) -> str:
    global wait_for_geolocation

    # Determine the location
    try:
        geopolitical_entity = get_geopolitical_entity_from_text(user_message_text)

        # If the user hasn't entered their location in the message
        if geopolitical_entity is None:
            coords, geopolitical_entity = get_user_geolocation()
        else:
            coords = get_geopolitical_entity_coords(geopolitical_entity)

    except KeyError:  # Couldn't get the user's location
        wait_for_geolocation = True
        return "Sorry, couldn't get your location. Please enter it manually"

    # Determine the day delta
    delta_days = get_delta_days_from_text(user_message_text)[0]

    if delta_days == 0:  # Get current weather
        # Make a request
        url = 'http://api.openweathermap.org/data/2.5/find'
        params = {'q': geopolitical_entity, 'units': 'metric', 'lang': 'en', 'APPID': WEATHER_APP_ID}
        response = requests.get(url=url, params=params)
        json_response = response.json()["list"][-1]

        # Get the weather
        description = json_response['weather'][0]['description']
        temperature = json_response['main']['temp']
        pressure = json_response['main']['pressure']

    elif delta_days < 7:  # Get weather forecast
        # Make a request
        url = 'http://api.openweathermap.org/data/2.5/onecall'
        params = {'lat': coords[0], 'lon': coords[1], 'units': 'metric',
                  'lang': 'en', 'APPID': WEATHER_APP_ID}
        response = requests.get(url=url, params=params)
        json_response = response.json()["daily"][delta_days]

        # Get the weather
        description = json_response['weather'][0]['description']
        temperature = json_response['temp']['day']
        pressure = json_response['pressure']

    else:
        return "Sorry, I can predict weather only a week ahead :("

    # Return the forecast
    return f"Weather in {geopolitical_entity}, " \
           f"{datetime.date.today() + datetime.timedelta(days=delta_days)}: " \
           f"{description.capitalize()}; " \
           f"Temperature: {temperature}°C; " \
           f"Pressure: {pressure}hPa"
