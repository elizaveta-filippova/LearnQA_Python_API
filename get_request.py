import requests


def get_request_text(your_url):
    return requests.get(your_url).text


url = 'https://playground.learnqa.ru/api/get_text'
print(get_request_text(your_url=url))
