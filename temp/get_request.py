from json.decoder import JSONDecodeError
import requests


url = "https://playground.learnqa.ru/api/get_text"
response = requests.get(url=url)
print(response.text)

try:
    parsed_response_text = response.json()
    print(parsed_response_text)
except JSONDecodeError:
    print('Response is not in JSON format')
