"""
** BOTTE HTTP CLIENT **
=======================

This Botte HTTP client is the preferred client to interact with Botte, when the
 consumer:
 - has Internet access
 - and is NOT running inside AWS infra or NOT the same AWS account as Botte (otherwise prefer `botte-lambda-client`)

Note: when the consumer is running in AWS infra (fi. Lambda), the preferred client
 should be [botte-lambda-client](../botte-lambda-client).

```py
import botte_http_client

client = botte_http_client.BotteHttpClient()
response = client.send_message("Hello world!")
assert response.data["text"] == "Hello world!"
```
"""

from functools import cached_property
from typing import Any

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
]

# Note: these might change in case of Botte Backend destroy and re-deploy.
BOTTE_BE_BASE_URL = "https://0uneqyoes2.execute-api.eu-south-1.amazonaws.com"


class BotteHttpClient:
    def __init__(self, base_url: str = BOTTE_BE_BASE_URL):
        """
        Args:
            base_url (str): base url of the Botte Backend Lambda, optional.
        """
        self.base_url = base_url

    def get_health(self):
        url = f"{self.base_url}/health"
        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if response.status_code == 404:
                raise Error404(f"The url returned 404: {url}") from exc
            raise

        return SendHealthResponse(response)

    def get_unhealth(self):
        url = f"{self.base_url}/unhealth"
        response = requests.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            if response.status_code != 500:
                raise NotError500(response.status_code) from exc

        return SendUnhealthResponse(response)

    def get_version(self):
        url = f"{self.base_url}/version"
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
        botte_be_api_auth_token: str,
        sender_app: str = "BOTTE_HTTP_CLIENT",
    ):
        """
        Args:
            text (str): the text of the message to send.
            botte_be_api_auth_token (str): HTTP auth token for Botte HTTP interface.
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
        url = f"{self.base_url}/message"
        headers = {"authorization": botte_be_api_auth_token}
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

    # Note: I commented out this code, because if the consumer has access to
    #  Param Store, then it means that has access to AWS infra, so it should
    #  use Botte Lambda Client instead.
    # @property
    # def _botte_be_api_auth_token(self):
    #     if not self.__botte_be_api_auth_token:
    #         client = aws_parameter_store_client.AwsParameterStoreClient()
    #         try:
    #             value = client.get_secret(
    #                 path="/botte-be/prod/api-authorizer-token",
    #                 cache_ttl=60 * 5,
    #             )
    #         except aws_parameter_store_client.ParameterNotFound as exc:
    #             raise ParamNotFoundInAwsParamStore(
    #                 path="/botte-be/prod/api-authorizer-token"
    #             ) from exc
    #         self.__botte_be_api_auth_token = value
    #
    #     return self.__botte_be_api_auth_token


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
