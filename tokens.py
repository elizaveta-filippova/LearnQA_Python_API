import time
from json import JSONDecodeError

import requests


def create_job_and_get_response(url, token=None):
    if token:
        params = {"token": f"{token}"}
        response = requests.get(url=url, params=params)
    else:
        response = requests.get(url=url)
    try:
        response_dict = response.json()
        return response_dict
    except JSONDecodeError:
        print("Ответ не в формате JSON")


url = "https://playground.learnqa.ru/ajax/api/longtime_job"
first_response = create_job_and_get_response(url=url)
token = first_response["token"]
seconds = first_response["seconds"]
status = create_job_and_get_response(url=url, token=token)["status"]
if status and status == "Job is NOT ready":
    print(f"Звпущен процесс создания задачи. Подождите {seconds} секунд...")
else:
    raise Exception("Что-то пошло не так...")

time.sleep(seconds)

second_response = create_job_and_get_response(url=url, token=token)
status = second_response["status"]
if not status:
    raise Exception("Что-то пошло не так...")
if second_response["result"] and status == "Job is ready":
    result = second_response["result"]
    print(f"Задача создана. Статус: {status}. Результат: {result}")
else:
    error = second_response["error"]
    print(f"Ошибка! {error}")
