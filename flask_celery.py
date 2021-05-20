
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'

parameters = {
    'symbol': 'OCTA',
    'aux': 'logo'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '0132fa52-e5f7-428b-8287-0f8a7a84f44e',
}

session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    print(data)
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
