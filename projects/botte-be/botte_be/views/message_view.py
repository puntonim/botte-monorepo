from typing import Any

import log_utils as logger
import telebot
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

logger.info("MESSAGE: LOADING")


@logger.get_adapter().inject_lambda_context(log_event=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    """
    Handler for the Lambda function triggered by a direct invocation (not via API
     Gateway event) with a dict payload.
    It sends a Telegram message from the registered bot to the target user (me), with
     the text given in the request body.

    Args:
        event: a dict, the payload.
        context: the context passed to the Lambda.

    The `event` is a dict like:
        {
            "text": "Hello world from aws-lambda-client pytests!",
            "sender_app": "AWS_LAMBDA_CLIENT"  # sender_app is optional.
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
    """
    logger.info("MESSAGE: START")

    # `text` event param.
    text = event.get("text")
    if not text:
        # This is a Lambda direct invocation interface, but it returns the same response
        #  as the HTTP interface.
        return aws_lambda_utils.BadRequest400Response(
            "Payload parameter 'text' required"
        ).to_dict()

    # `sender_app` event param: it's optional and just used for logging purpose
    #  (logging is done in the lambda_handler() decorator).
    # sender_app = event.get("sender_app")

    bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, threaded=False)
    message = bot.send_message(text=text, chat_id=settings.PUNTONIM_CHAT_ID)
    response_body = message.json

    # This is a Lambda direct invocation interface, but it returns the same response
    #  as the HTTP interface.
    return aws_lambda_utils.Ok200Response(response_body).to_dict()
