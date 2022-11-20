import requests


class TestHomeworkCookie:

    def test_homework_cookie(self):

        url = "https://playground.learnqa.ru/api/homework_cookie"
        expected_cookie = {
            'cookie': 'HomeWork',
            'value': 'hw_value'
        }

        response = requests.get(url=url)
        assert response.status_code == 200, "The request wasn't executed successfully"
        assert response.cookies, "No cookies in the response"
        assert expected_cookie['cookie'] in response.cookies, f"The response has no " \
                                                              f"{expected_cookie['cookie']} cookie"

        actual_cookie_value = response.cookies.get(expected_cookie['cookie'])
        expected_cookie_value = expected_cookie['value']
        assert actual_cookie_value == expected_cookie_value, "The actual cookie value is not equal " \
                                                             "to the expected one"
