import requests

response = requests.get("https://playground.learnqa.ru/api/long_redirect")
redirects_count = len(response.history)

print(f'Происходит {redirects_count} редирект(а). Итоговый URL: {response.url}')
