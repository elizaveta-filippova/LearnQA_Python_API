import requests


class TestHomeworkCookie:

    def test_homework_cookie(self):
        url = "https://playground.learnqa.ru/api/homework_cookie"
        domain = ".playground.learnqa.ru"

        response = requests.get(url=url)
        assert response.cookies, "No cookies in the response"

        actual_cookie_dict = response.cookies.get_dict(domain=domain)
        assert actual_cookie_dict, f"No cookies for {domain}"

        expected_cookie_dict = {'HomeWork': 'hw_value'}
        assert actual_cookie_dict == expected_cookie_dict, "Method returned wrong cookie"
