import speech
import weather
import translate
import currency_rate
import search

import re

close_tab = False
link_to_search = ""
search_in_the_internet = True


def answer(user_message_text: str) -> str:
    answer_text = recognize_user_intention(user_message_text)
    speech.save_assistant_speech(answer_text)
    return answer_text


def recognize_user_intention(user_message_text: str) -> str:
    global close_tab, search_in_the_internet, link_to_search

    close_tab = False
    search_in_the_internet = False
    link_to_search = ""

    # Text translation
    if re.findall(r"translat", user_message_text) \
            or translate.get_language_names_from_text(user_message_text.lower()):
        return translate.translate_text(user_message_text.lower())

    # Weather forecast

    # Determine the location
    if weather.wait_for_geolocation:
        try:
            weather.wait_for_geolocation = False
            return weather.get_weather(user_message_text)
        except KeyError:
            weather.wait_for_geolocation = True
            return "Please enter your location again"

    if re.findall(r"weather", user_message_text):
        return weather.get_weather(user_message_text)

    # Currency rate
    if len(re.findall(r"[A-Z]{3}", user_message_text)) == 2:
        currencies = re.findall(r"[A-Z]{3}", user_message_text)
        return currency_rate.get_rate(*currencies)

    # Greeting
    if re.findall(r"\s(hello)\s", ' ' + user_message_text + ' '):
        return "Hello!"
    if re.findall(r"\s(hi)\s", ' ' + user_message_text + ' '):
        return "Hi!"

    # Farewell
    if re.findall(r"bye", user_message_text):
        close_tab = True
        return "Bye!"

    search_in_the_internet = True
    link_to_search = ""

    if re.findall("video", user_message_text) or re.findall("youtube", user_message_text):
        search.search_youtube(user_message_text)
        return user_message_text + '\n' + link_to_search

    answer_text = search.search(user_message_text)

    return answer_text + '\n' + link_to_search
