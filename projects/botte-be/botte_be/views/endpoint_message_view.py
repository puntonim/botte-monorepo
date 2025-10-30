from json import JSONDecodeError
from typing import Any

import log_utils as logger
import telebot
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_utils import aws_lambda_utils

from ..conf import settings
from .views_utils import lambda_static_init

# Objects declared outside the Lambda's handler method are part of Lambda's
# *execution environment*. This execution environment is sometimes reused for subsequent
# function invocations. Note that you can not assume that this always happens.
# Typical use cases: database connection and log init. The same db connection can be
# re-used in some subsequent function invocations. It is recommended though to add
# logic to check if a connection already exists before creating a new one.
# The execution environment also provides 512 MB of *disk space* in the /tmp directory.
# Again, this can be re-used in some subsequent function invocations.
# See: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html#static-initialization

# This Lambda is configured with 0 retries. So do raise exceptions in the view.

lambda_static_init()

logger.info("ENDPOINT MESSAGE: LOADING")


@aws_lambda_utils.redact_http_headers(headers_names=("authorization",))
@logger.get_adapter().inject_lambda_context(log_event=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    """
    Handler for the Lambda function triggered by an API Gateway event: HTTP POST.
    It sends a Telegram message from the registered bot to the target user (me), with
     the text given in the request body.
    It requires authentication via the header Authorization.

    Args:
        event: an AWS event, eg. API Gateway event.
        context: the context passed to the Lambda.

    The `event` is a dict (that can be casted to `APIGatewayProxyEventV2`) like:
        {
            "level": "INFO",
            "location": "/opt/python/aws_lambda_powertools/logging/logger.py::decorate::535",
            "message": {
                "version": "2.0",
                "routeKey": "POST /message",
                "rawPath": "/message",
                "rawQueryString": "",
                "headers": {
                    "accept": "*/*",
                    "authorization": "t**REDACTED**",
                    "content-length": "25",
                    "content-type": "application/x-www-form-urlencoded",
                    "host": "5t325uqwq7.execute-api.eu-south-1.amazonaws.com",
                    "user-agent": "curl/8.1.2",
                    "x-amzn-trace-id": "Root=1-68fd27e3-0154aa97179fe9f44f0e832b",
                    "x-forwarded-for": "151.55.108.219",
                    "x-forwarded-port": "443",
                    "x-forwarded-proto": "https"
                },
                "requestContext": {
                    "accountId": "477353422995",
                    "apiId": "5t325uqwq7",
                    "authorizer": {
                        "lambda": {
                            "ts": "2025-10-25T19:15:25.345039+00:00"
                        }
                    },
                    "domainName": "5t325uqwq7.execute-api.eu-south-1.amazonaws.com",
                    "domainPrefix": "5t325uqwq7",
                    "http": {
                        "method": "POST",
                        "path": "/message",
                        "protocol": "HTTP/1.1",
                        "sourceIp": "151.55.108.219",
                        "userAgent": "curl/8.1.2"
                    },
                    "requestId": "TBMrkhH5su8EM6g=",
                    "routeKey": "POST /message",
                    "stage": "$default",
                    "time": "25/Oct/2025:19:41:23 +0000",
                    "timeEpoch": 1761421283238
                },
                "body": "eyJ0ZXh0IjogIkhlbGxvIFdvcmxkIDMifQ==",
                "isBase64Encoded": true
            },
            "timestamp": "2025-10-25 19:41:24,205+0000",
            "service": "Botte BE @ v0.1.0",
            "cold_start": true,
            "function_name": "botte-be-prod-endpoint-message",
            "function_memory_size": "256",
            "function_arn": "arn:aws:lambda:eu-south-1:477353422995:function:botte-be-prod-endpoint-message",
            "function_request_id": "ee961041-03bd-4835-b517-1c9ef2ecd356",
            "xray_trace_id": "1-68fd27e3-27c03ef15a875d3c1992d664"
        }

    The `context` is a `LambdaContext` instance with properties similar to:
        {
            "level": "INFO",
            "location": "/var/task/botte/views/endpoint_message_view.py::lambda_handler::31",
            "message": "MESSAGE: START",
            "timestamp": "2023-10-25 19:54:21,099+0000",
            "service": "botte v0.1.0",
            "cold_start": true,
            "function_name": "botte-prod-endpoint-message",
            "function_memory_size": "256",
            "function_arn": "arn:aws:lambda:eu-south-1:477353422995:function:botte-prod-endpoint-message",
            "function_request_id": "6567717d-657e-4063-bd0a-7dade193500c",
            "xray_trace_id": "1-6539726c-3981d7366d95997859c39cb8"
        }
    More info here: https://docs.aws.amazon.com/lambda/latest/dg/python-context.html

    Example:
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
    logger.info("ENDPOINT MESSAGE: START")

    api_event = APIGatewayProxyEventV2(event)

    if not api_event.body:
        return aws_lambda_utils.BadRequest400Response("Body required").to_dict()

    try:
        body: dict = api_event.json_body
    except JSONDecodeError:
        return aws_lambda_utils.BadRequest400Response(
            "Body must be JSON encoded"
        ).to_dict()

    # `text` POST body param.
    text = body.get("text")
    if not text:
        return aws_lambda_utils.BadRequest400Response(
            "Body parameter 'text' required"
        ).to_dict()

    # `sender_app` POST body param: it's optional and just used for logging purpose
    #  (logging is done in the lambda_handler() decorator).
    # sender_app = body.get("sender_app")

    bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, threaded=False)
    message = bot.send_message(text=text, chat_id=settings.PUNTONIM_CHAT_ID)
    response_body = message.json

    return aws_lambda_utils.Ok200Response(response_body).to_dict()
