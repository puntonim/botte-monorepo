"""
** BOTTE HTTP CLIENT **
=======================

Use this client to interact with Botte, via HTTP.\
Do not use this in AWS services, but rather prefer `botte-lambda-client`.

```py
import botte_http_client

client = botte_http_client.BotteHttpClient()
response = client.send_message("Hello world!")
assert response.data["text"] == "Hello world!"
```
"""

from functools import cached_property
from typing import Any

import aws_parameter_store_client
import requests

__all__ = [
    "BotteHttpClient",
    "SendMessageResponse",
    "SendHealthResponse",
    "SendUnhealthResponse",
    "SendVersionResponse",
    "BaseBotteHttpClientException",
    "AuthError",
    "Error404",
    "NotError500",
    "ParamNotFoundInAwsParamStore",
]

# Note: these might change in case of Botte Backend destroy and re-deploy.
BOTTE_BE_BASE_URL = "https://5t325uqwq7.execute-api.eu-south-1.amazonaws.com"
BOTTE_BE_API_AUTHORIZER_TOKEN_PATH_IN_PARAM_STORE = (
    "/botte-be/prod/api-authorizer-token"
)


class BotteHttpClient:
    def __init__(self, botte_be_api_auth_token: str | None = None):
        self.__botte_be_api_auth_token = botte_be_api_auth_token

    def get_health(self, base_url: str = BOTTE_BE_BASE_URL):
        url = f"{base_url}/health"
        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if response.status_code == 404:
                raise Error404(f"The url returned 404: {url}") from exc
            raise

        return SendHealthResponse(response)

    def get_unhealth(self, base_url: str = BOTTE_BE_BASE_URL):
        url = f"{base_url}/unhealth"
        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if response.status_code != 500:
                raise NotError500(response.status_code) from exc

        return SendUnhealthResponse(response)

    def get_version(self, base_url: str = BOTTE_BE_BASE_URL):
        url = f"{base_url}/version"
        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if response.status_code == 404:
                raise Error404(f"The url returned 404: {url}") from exc
            raise

        return SendVersionResponse(response)

    def send_message(
        self,
        text: str,
        base_url: str = BOTTE_BE_BASE_URL,
        sender_app: str = "BOTTE_HTTP_CLIENT",
    ):
        """
        Args:
            text (str): the text of the message to send.
            base_url (str): base url of the Botte Backend Lambda, optional.
            sender_app (str): just an identifier, default: "BOTTE_HTTP_CLIENT".

        Curl example:
            $ curl -X POST https://5t325uqwq7.execute-api.eu-south-1.amazonaws.com/message \
               -H 'Authorization: XXX' \
               -d '{"text": "Hello World", "sender_app": "CURL_TEST"}'  # sender_app is optional.
            {
              "message_id": 8,
              "from": {
                "id": 6570886232,
                "is_bot": true,
                "first_name": "Botte",
                "username": "realbottebot"
              },
              "chat": {
                "id": 2137200685,
                "first_name": "Paolo",
                "username": "punto...",
                "type": "private"
              },
              "date": 1698264386,
              "text": "Hello World"
            }
        """
        url = f"{base_url}/message"
        headers = {"authorization": self._botte_be_api_auth_token}
        data = dict(
            text=text,
            sender_app=sender_app,  # Optional.
        )
        response = requests.post(url, headers=headers, json=data)

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if response.status_code == 403:
                raise AuthError("The Botte BE Auth token is invalid") from exc
            elif response.status_code == 404:
                raise Error404(f"The url returned 404: {url}") from exc
            raise

        return SendMessageResponse(response)

    @property
    def _botte_be_api_auth_token(self):
        if not self.__botte_be_api_auth_token:
            client = aws_parameter_store_client.AwsParameterStoreClient()
            try:
                value = client.get_secret(
                    path=BOTTE_BE_API_AUTHORIZER_TOKEN_PATH_IN_PARAM_STORE,
                    cache_ttl=60 * 5,
                )
            except aws_parameter_store_client.ParameterNotFound as exc:
                raise ParamNotFoundInAwsParamStore(
                    path=BOTTE_BE_API_AUTHORIZER_TOKEN_PATH_IN_PARAM_STORE
                ) from exc
            self.__botte_be_api_auth_token = value

        return self.__botte_be_api_auth_token


class BaseJsonResponse:
    def __init__(self, raw_response: requests.Response):
        # `raw_response` is the raw HTTP response received by `requests` lib.
        self.raw_response = raw_response

    @cached_property
    def data(self):
        # `data` is the JSON content included in the raw HTTP response.
        return self.raw_response.json()


class SendMessageResponse(BaseJsonResponse):
    """
    Example:
        {
          "message_id": 8,
          "from": {
            "id": 6570886232,
            "is_bot": true,
            "first_name": "Botte",
            "username": "realbottebot"
          },
          "chat": {
            "id": 2137200685,
            "first_name": "Paolo",
            "username": "punto...",
            "type": "private"
          },
          "date": 1698264386,
          "text": "Hello World"
        }
    """

    # IMP: do NOT assign values to INSTANCE attrs here at class-level, but only type
    #  annotations. If you assign values they become CLASS attrs.
    data: dict[str, Any]


class SendHealthResponse(BaseJsonResponse):
    # IMP: do NOT assign values to INSTANCE attrs here at class-level, but only type
    #  annotations. If you assign values they become CLASS attrs.
    data: str


class SendUnhealthResponse(BaseJsonResponse):
    # IMP: do NOT assign values to INSTANCE attrs here at class-level, but only type
    #  annotations. If you assign values they become CLASS attrs.
    data: dict[str, str]


class SendVersionResponse(BaseJsonResponse):
    # IMP: do NOT assign values to INSTANCE attrs here at class-level, but only type
    #  annotations. If you assign values they become CLASS attrs.
    data: dict[str, Any]


class BaseBotteHttpClientException(Exception): ...


class AuthError(BaseBotteHttpClientException): ...


class Error404(BaseBotteHttpClientException):
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"404 error for: {url}")


class NotError500(BaseBotteHttpClientException):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(
            f"We were expecting a 500 error, instead we got: {status_code}"
        )


class ParamNotFoundInAwsParamStore(BaseBotteHttpClientException):
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Param not found in param store: {path}")
