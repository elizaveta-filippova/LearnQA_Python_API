import requests


def send_request(request, url, method=None):
    if request == "GET":
        return requests.get(url=url,
                            params={"method": f"{method}"})
    elif request == "POST":
        return requests.post(url=url,
                             data={"method": f"{method}"})
    elif request == "PUT":
        return requests.put(url=url,
                            data={"method": f"{method}"})
    elif request == "DELETE":
        return requests.delete(url=url,
                               data={"method": f"{method}"})

    elif request == "HEAD":
        return requests.head(url=url,
                             data={"method": f"{method}"})
    else:
        return requests.get(url=url)


url = "https://playground.learnqa.ru/ajax/api/compare_query_type"
method_types = ["GET", "POST", "PUT", "DELETE", "HEAD"]
results_list = []

for r in method_types:
    for mt in method_types:
        response = send_request(request=r, url=url, method=mt)
        results_list.append({"request": r,
                             "method_in_params": mt,
                             "status_code": response.status_code,
                             "text": response.text})
    response = send_request(request=r, url=url)
    results_list.append({"request": r,
                         "method_in_params": "none",
                         "status_code": response.status_code,
                         "text": response.text})
unsupported_request = []
right_method_for_request = []
no_method = []
for result in results_list:
    if result['request'] != result['method_in_params'] and result['text'] == '{"success":"!"}' \
            or result['request'] == result['method_in_params'] \
            and (result['status_code'] == '400' or result['text'] == 'Wrong method provided'):
        print(f"Неверный ответ сервера: для сочетания запроса "
              f"{result['request']} и метода в параметрах {result['method_in_params']} "
              f"не должно быть ответа сервера {result['status_code']} {result['text']}")
    if result['request'] == 'HEAD':
        unsupported_request.append(result)
    if result['request'] == result['method_in_params']:
        right_method_for_request.append(result)
    if result['method_in_params'] == 'none':
        no_method.append(result)
print(f''' Пример правильного сочетания запроса и метолда в параметрах: {right_method_for_request[0]} 
           Пример запроса не из списка: {unsupported_request[0]}
           Пример запроса без параметра method: {no_method[0]} 
      ''')
