from unittest import mock

import pytest

from botte_http_client import (
    AuthError,
    BotteHttpClient,
    Error404,
    ParamNotFoundInAwsParamStore,
)


class TestIntrospection:
    def test_health(self):
        client = BotteHttpClient()
        response = client.get_health()
        assert response.data == "2025-10-31T17:13:26.330895+00:00"

    def test_version(self):
        client = BotteHttpClient()
        response = client.get_version()
        assert response.data == {
            "appName": "Botte BE",
            "app": "1.0.0",
            "python": "3.13.7 (main, Sep 26 2025, 14:01:44) [GCC 11.5.0 20240719 (Red Hat 11.5.0-5)]",
            "boto3": "1.40.4",
            "botocore": "1.40.4",
            "pydantic": [
                "pydantic version: 2.11.7",
                "pydantic-core version: 2.33.2",
                "pydantic-core build: profile=release pgo=false",
                "python version: 3.13.7 (main, Sep 26 2025, 14:01:44) [GCC 11.5.0 20240719 (Red Hat 11.5.0-5)]",
                "platform: Linux-5.10.244-267.968.amzn2.x86_64-x86_64-with-glibc2.34",
                "related packages: pydantic-settings-2.9.1 typing_extensions-4.14.0",
                "commit: unknown",
            ],
            "sqlite3": "3.40.0",
        }

    def test_unhealth(self):
        client = BotteHttpClient()
        response = client.get_unhealth()
        assert response.data == {"message": "Internal Server Error"}


class TestSendMessage:
    def setup_method(self):
        self.text = "Hello world from botte http client pytests!"

    def test_happy_flow(self):
        client = BotteHttpClient()
        response = client.send_message(self.text)
        assert response.data["text"] == self.text

    def test_auth_error(self):
        client = BotteHttpClient(botte_be_api_auth_token="XXX")
        with pytest.raises(AuthError):
            client.send_message(self.text)

    def test_base_url_error(self):
        client = BotteHttpClient()
        with pytest.raises(Error404):
            client.send_message(
                self.text,
                base_url="https://5t325uqwq7.execute-api.eu-south-1.amazonaws.com/XXX",
            )

    def test_param_api_auth_token_not_found_in_param_store(self):
        with mock.patch(
            "botte_http_client.http_client.BOTTE_BE_API_AUTHORIZER_TOKEN_PATH_IN_PARAM_STORE",
            "/XXX",
        ):
            client = BotteHttpClient()
            with pytest.raises(ParamNotFoundInAwsParamStore):
                client.send_message(self.text)
