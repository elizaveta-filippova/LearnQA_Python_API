import requests


class TestHomeworkHeader:

    def test_header_homework(self):

        url = "https://playground.learnqa.ru/api/homework_header"
        expected_header = {
            'header': 'x-secret-homework-header',
            'value': 'Some secret value'
        }

        response = requests.get(url=url)
        assert response.status_code == 200, "The request wasn't executed successfully"
        assert response.headers, "No headers in the response"
        assert expected_header['header'] in response.headers, f"The response has no " \
                                                              f"{expected_header['header']} header"

        actual_header_value = response.headers.get(expected_header['header'])
        expected_header_value = expected_header['value']
        assert actual_header_value == expected_header_value, "The actual header value is not equal " \
                                                             "to the expected one"
