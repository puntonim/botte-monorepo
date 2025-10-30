from typing import Any

import datetime_utils
import log_utils as logger
from aws_lambda_powertools.utilities.data_classes.api_gateway_authorizer_event import (
    APIGatewayAuthorizerEventV2,
    APIGatewayAuthorizerResponseV2,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

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

logger.info("AUTHORIZER: LOADING")


# Use `log_event=False` so the secret in the header does not end up in CloudWatch logs.
@logger.get_adapter().inject_lambda_context(log_event=False)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    """
    Authorizer for Lambda functions.
    Docs:
     - https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-lambda-authorizer.html
     - https://www.serverless.com/framework/docs/providers/aws/events/http-api#lambda-request-authorizers

    Args:
        event: an AWS event, eg. API Gateway event.
        context: the context passed to the Lambda.

    The `event` is a dict (that can be casted to `APIGatewayProxyEventV2`) like:
        {
            "level": "INFO",
            "location": "/opt/python/aws_lambda_powertools/logging/logger.py::decorate::535",
            "message": {
                "version": "2.0",
                "type": "REQUEST",
                "routeArn": "arn:aws:execute-api:eu-south-1:477353422995:5t325uqwq7/$default/POST/message",
                "identitySource": [
                    "XXX"
                ],
                "routeKey": "POST /message",
                "rawPath": "/message",
                "rawQueryString": "",
                "headers": {
                    "accept": "*/*",
                    "authorization": "XXX",
                    "content-length": "23",
                    "content-type": "application/x-www-form-urlencoded",
                    "host": "5t325uqwq7.execute-api.eu-south-1.amazonaws.com",
                    "user-agent": "curl/8.1.2",
                    "x-amzn-trace-id": "Root=1-68fd21b8-153b863817c4f914038b8279",
                    "x-forwarded-for": "151.55.108.219",
                    "x-forwarded-port": "443",
                    "x-forwarded-proto": "https"
                },
                "requestContext": {
                    "accountId": "477353422995",
                    "apiId": "5t325uqwq7",
                    "domainName": "5t325uqwq7.execute-api.eu-south-1.amazonaws.com",
                    "domainPrefix": "5t325uqwq7",
                    "http": {
                        "method": "POST",
                        "path": "/message",
                        "protocol": "HTTP/1.1",
                        "sourceIp": "151.55.108.219",
                        "userAgent": "curl/8.1.2"
                    },
                    "requestId": "TBI06jAhsu8EKfQ=",
                    "routeKey": "POST /message",
                    "stage": "$default",
                    "time": "25/Oct/2025:19:15:04 +0000",
                    "timeEpoch": 1761419704689
                }
            },
            "timestamp": "2025-10-25 19:15:05,222+0000",
            "service": "Botte BE @ v0.1.0",
            "cold_start": true,
            "function_name": "botte-be-prod-authorizer",
            "function_memory_size": "128",
            "function_arn": "arn:aws:lambda:eu-south-1:477353422995:function:botte-be-prod-authorizer",
            "function_request_id": "0877525f-d440-4132-bfba-eff4584a0662",
            "xray_trace_id": "1-68fd21b8-59a9d41c1483a041440a1687"
        }

    The `context` is a `LambdaContext` instance with properties similar to:
        {
            "level": "INFO",
            "location": "/var/task/botte/views/authorizer_view.py::lambda_handler::98",
            "message": "AUTHORIZER: START",
            "timestamp": "2023-10-25 19:54:20,357+0000",
            "service": "botte v0.1.0",
            "cold_start": true,
            "function_name": "botte-prod-authorizer-main",
            "function_memory_size": "128",
            "function_arn": "arn:aws:lambda:eu-south-1:477353422995:function:botte-prod-authorizer-main",
            "function_request_id": "5de23c7a-5dfe-4d9e-bcfe-aa56ba51d492",
            "xray_trace_id": "1-6539726b-2921daaa0f088fe4082887d3"
        }
    More info here: https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """
    logger.info("AUTHORIZER: START")

    api_event = APIGatewayAuthorizerEventV2(event)

    is_authorized = False
    if not settings.DO_ENABLE_API_AUTHORIZER:
        is_authorized = True
    else:
        for header_name in (
            # Used by regular HTTP requests to Botte, it's API_AUTHORIZER_TOKEN env
            #  var and in Parameter Store.
            "Authorization".lower(),
            # Used by Telegram webhook, see commands_webhook_view.py and README.md
            #  in patatrack-monorepo/projects/botte to know how to register a webhook
            #  at Telegram.
            "X-Telegram-Bot-Api-Secret-Token".lower(),
        ):
            # `api_event.headers.get()` is case-insensitive.
            header_value = api_event.headers.get(header_name)
            if header_value == settings.API_AUTHORIZER_TOKEN:
                is_authorized = True
                # Note: I tried to redact the secret here so that the next Lambda
                #  will not see the secret (and so it will not end up in CloudWatch
                #  logs), but it doesn't work.
                # event["headers"]["authorization"] = "**REDACTED**"
                break

    context = dict(ts=datetime_utils.now_utc().isoformat())
    response = APIGatewayAuthorizerResponseV2(
        authorize=is_authorized, context=context
    ).asdict()
    return response
