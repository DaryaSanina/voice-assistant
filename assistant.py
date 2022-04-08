import events
import speech
import weather
import translate
import currency_rate
import search

import re
from googletrans import Translator

close_tab = False
link_to_search = ""
search_in_the_internet = True

translator = Translator()


def answer(user_message_text: str, user_language="english") -> str:
    if user_language != "english":  # Translate the message into English
        user_message_text = translator.translate(text=user_message_text, src=user_language).text

    answer_text = recognize_user_intention(user_message_text)

    if user_language != "english":  # Translate the assistant's answer into the user's language
        answer_text = translator.translate(text=answer_text, dest=user_language).text

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

    # Getting list of events
    if re.findall(r"plans|events", user_message_text):
        answer_text = "Here are the events you have planned:"
        for event in events.events:
            answer_text += f"\n\nName: {event['name']}\nDate: {event['date']}\nTime: {event['time']}\n Place: {event['place']}"
        return answer_text

    # Saving an event
    if re.findall(r"plan|event", user_message_text) \
            or weather.get_geopolitical_entity_from_text(user_message_text) \
            or weather.get_delta_days_from_text(user_message_text)[0] \
            or events.get_time_from_text(user_message_text)[0]:
        events.add_event(user_message_text)
        return f"""Name: {events.events[-1].name}
        Date: {events.events[-1].date}
        Time: {events.events[-1].time}
        Place: {events.events[-1].place}"""

    # Greeting
    if re.findall(r"\s(hello)\s", ' ' + user_message_text + ' '):
        return "Hello!"
    if re.findall(r"\s(hi)\s", ' ' + user_message_text + ' '):
        return "Hi!"

    # Farewell
    if re.findall(r"bye", user_message_text):
        close_tab = True
        return "Bye!"

    # Searching in the internet
    search_in_the_internet = True
    link_to_search = ""

    # Searching in YouTube
    if re.findall("video", user_message_text) or re.findall("youtube", user_message_text):
        search.search_youtube(user_message_text)
        return user_message_text + '\n' + link_to_search

    answer_text = search.search(user_message_text)

    return answer_text + '\n' + link_to_search
