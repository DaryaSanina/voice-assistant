import os
from dotenv import load_dotenv

import requests

path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(path):
    load_dotenv(path)
    CURRENCY_RATE_APP_ID = os.environ.get('CURRENCY_RATE_APP_ID')


def get_rate(base_currency, target_currency):
    url = f'https://v6.exchangerate-api.com/v6/{CURRENCY_RATE_APP_ID}/pair/{base_currency}/{target_currency}'
    response = requests.get(url=url)
    json_response = response.json()

    if json_response["result"] == "error" and json_response["error-type"] == "unsupported-code":
        return "Unknown currency"

    try:
        rate = json_response['conversion_rate']
        return f"1 {base_currency} = {rate} {target_currency}"
    except KeyError:
        return json_response
