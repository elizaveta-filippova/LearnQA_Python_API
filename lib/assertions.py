from requests import Response
import json


class Assertions:

    @staticmethod
    def assert_json_value_by_name(response: Response, name,
                                  expected_value, error_message):
        try:
            response_as_dict = response.json()
        except json.decoder.JSONDecodeError:
            assert False, f"Response is not in JSON format, response text is '{response.text}'"

        assert name in response_as_dict, f"Response JSON doesn't have key '{name}'"
        assert response_as_dict[name] == expected_value, error_message

    @staticmethod
    def assert_json_has_key(response: Response, name):
        try:
            response_as_dict = response.json()
        except json.decoder.JSONDecodeError:
            assert False, f"Response is not in JSON format, response text is '{response.text}'"

        assert name in response_as_dict, f"Response JSON doesn't have key '{name}'"

    @staticmethod
    def assert_json_has_keys(response: Response, names: list):
        try:
            response_as_dict = response.json()
        except json.decoder.JSONDecodeError:
            assert False, f"Response is not in JSON format, response text is '{response.text}'"

        for name in names:
            assert name in response_as_dict, f"Response JSON doesn't have key '{name}'"

    @staticmethod
    def assert_json_has_not_key(response: Response, name):
        try:
            response_as_dict = response.json()
        except json.decoder.JSONDecodeError:
            assert False, f"Response is not in JSON format, response text is '{response.text}'"

        assert name not in response_as_dict, f"Response JSON shouldn't have key '{name}'. But it's present"

    @staticmethod
    def assert_json_has_not_keys(response: Response, names: list):
        try:
            response_as_dict = response.json()
        except json.decoder.JSONDecodeError:
            assert False, f"Response is not in JSON format, response text is '{response.text}'"

        for name in names:
            assert name not in response_as_dict, f"Response JSON shouldn't have key '{name}'. But it's present"

    @staticmethod
    def assert_code_status(response: Response, expected_status_code):
        assert response.status_code == expected_status_code, \
            f"Unexpected status code. Expected status code: {expected_status_code}. " \
            f"Actual status_code: {response.status_code}."

    @staticmethod
    def assert_response_content(response: Response, expected_content):
        response_content = response.content
        if isinstance(response_content, bytes):
            response_content = response_content.decode("utf-8")

        assert response_content == expected_content, \
            f"Unexpected response content. Expected response content: '{expected_content}', " \
            f"actual response content: '{response_content}"



