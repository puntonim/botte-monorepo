"""
** BOTTE LAMBDA CLIENT **
=========================

Use this client to interact with Botte, in AWS services inside the same AWS account
 (and with the right permission to invoke the Lambda).

```py
import botte_lambda_client

client = botte_lambda_client.BotteLambdaClient()
response, status_code = client.send_message("Hello world", sender_app="BOTTE_LAMBDA_CLIENT")
assert response["text"] == "Hello world"
assert status_code == 200
```
"""

import json

import aws_lambda_client

__all__ = [
    "BotteLambdaClient",
    "BotteLambdaNotFound",
    "BaseBotteLambdaClientException",
]

# Any of these 3 works:
LAMBDA_NAME = "477353422995:function:botte-be-prod-message"
# LAMBDA_NAME = "arn:aws:lambda:eu-south-1:477353422995:function:botte-be-prod-message"
# LAMBDA_NAME = "botte-be-prod-message"


class BotteLambdaClient:
    def send_message(self, text: str, sender_app: str = "BOTTE_LAMBDA_CLIENT"):
        """
        Args:
            text (str): the text of the message to send.
            sender_app (str): just an identifier, default: "BOTTE_LAMBDA_CLIENT".
        """

        client = aws_lambda_client.AwsLambdaClient()
        payload = {"text": text, "sender_app": sender_app}
        try:
            response = client.invoke(LAMBDA_NAME, payload=payload)
        except aws_lambda_client.LambdaNotFound as exc:
            raise BotteLambdaNotFound(LAMBDA_NAME) from exc

        status_code = response.get("StatusCode")

        # Decode the response body.
        payload = response.get("Payload")
        payload = payload.read()
        payload = payload.decode()
        payload = json.loads(payload)
        if "statusCode" in payload:
            status_code = payload.get("statusCode")
        body = payload.get("body")
        body = json.loads(body)

        return body, status_code


class BaseBotteLambdaClientException(Exception): ...


class BotteLambdaNotFound(BaseBotteLambdaClientException):
    def __init__(self, lambda_name):
        self.lambda_name = lambda_name
        super().__init__(f"Botte BE Lambda not found with name: {lambda_name}")
