import requests


class TestFirstAPI:

    def test_hello_call(self):
        url = "https://playground.learnqa.ru/api/hello"
        name = 'Elizaveta'
        data = {"name": name}

        response = requests.get(url=url, params=data)

        assert response.status_code == 200, "Wrong response code"

        response_dict = response.json()

        assert "answer" in response_dict, "There is no field 'answer' in the response"
