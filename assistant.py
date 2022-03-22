import speech
import re
from flask import request
import requests
import spacy

WEATHER_APP_ID = '557ae81d232ad0146c0e60fc98903f31'

close_tab = False
wait_for_geolocation = False


def answer(user_message_text: str) -> str:
    answer_text = recognize_user_intention(user_message_text)
    speech.save_assistant_speech(answer_text)
    return answer_text


def recognize_user_intention(user_message_text: str) -> str:
    global close_tab, wait_for_geolocation

    # Greeting
    if re.findall(r"hello", user_message_text):
        return "Hello!"
    if re.findall(r"hi", user_message_text):
        return "Hi!"

    # Farewell
    if re.findall(r"bye", user_message_text):
        close_tab = True
        return "Bye!"

    # Weather forecast
    if wait_for_geolocation:
        try:
            wait_for_geolocation = False
            return get_weather(user_message_text)
        except KeyError:
            wait_for_geolocation = True
            return "Please enter your location again"
    if re.findall(r"weather", user_message_text):
        try:
            geopolitical_entity = get_geopolitical_entity_from_text(user_message_text)
            if geopolitical_entity is None:
                geopolitical_entity = get_user_geolocation()
        except KeyError:
            wait_for_geolocation = True
            return "Sorry, couldn't get location. Please enter it manually"
        return get_weather(geopolitical_entity)

    return user_message_text


def get_user_geolocation() -> str:
    url = f'http://ip-api.com/json/{request.remote_addr}'
    response = requests.get(url=url)
    json_response = response.json()
    geopolitical_entity = json_response["city"]
    return geopolitical_entity


def get_geopolitical_entity_from_text(text) -> str:
    nlp = spacy.load('en_core_web_lg')
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            geopolitical_entity = ent.text
            return ' '.join(word.capitalize() for word in geopolitical_entity.split())


def get_weather(geopolitical_entity) -> str:
    url = 'http://api.openweathermap.org/data/2.5/find'
    params = {'q': geopolitical_entity, 'units': 'metric', 'lang': 'en', 'APPID': WEATHER_APP_ID}
    response = requests.get(url=url, params=params)
    json_response = response.json()["list"][0]
    return f'''Weather in {geopolitical_entity}:
    {json_response['weather'][0]['description'].capitalize()}
    Temperature: {json_response['main']['temp']}
    Pressure: {json_response['main']['pressure']}'''
