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
exception_message = "Что-то пошло не так..."

first_response = create_job_and_get_response(url=url)

if "token" in first_response and "seconds" in first_response:
    token = first_response["token"]
    seconds = first_response["seconds"]
else:
    raise Exception(exception_message)

second_response = create_job_and_get_response(url=url, token=token)

if "status" in second_response and second_response["status"] == "Job is NOT ready":
    print(f"Запущен процесс создания задачи. Подождите {seconds} секунд...")
else:
    raise Exception(exception_message)

time.sleep(seconds)

third_response = create_job_and_get_response(url=url, token=token)

if "status" in third_response:
    status = third_response["status"]
else:
    raise Exception(exception_message)

if "result" in third_response and status == "Job is ready":
    result = third_response["result"]
    print(f"Задача создана. Статус: {status}. Результат: {result}")
elif "error" in third_response:
    error = third_response["error"]
    print(f"Ошибка! {error}")
else:
    raise Exception(exception_message)
