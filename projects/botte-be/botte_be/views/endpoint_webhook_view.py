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

logger.info("ENDPOINT TELEGRAM WEBHOOK: LOADING")

# Do not assign bot here with `telebot.TeleBot(settings.TELEGRAM_TOKEN, threaded=False)`
#  otherwise the test settings and vcr.py will not be able to catch it on time.
#  But still use a module-level var so it can be re-used across subsequent fn invoc.
bot: telebot.TeleBot | None = None


@aws_lambda_utils.redact_http_headers(
    headers_names=("x-telegram-bot-api-secret-token",)
)
@logger.get_adapter().inject_lambda_context(log_event=True)
def lambda_handler(event: dict[str, Any], context: LambdaContext) -> dict:
    """
    Handler for the Lambda function triggered by an API Gateway event: HTTP POST
     sent by Telegram as configured webhook for user commands.
    It sends a Telegram message from the registered bot (@realbottebot) to the target
     user (me, @puntonim) with the text given in the request body.
    It requires authentication via the header `X-Telegram-Bot-Api-Secret-Token` used by
     Telegram webhook.

    Args:
        event: an AWS event, eg. API Gateway event.
        context: the context passed to the Lambda.

    The `event` is a dict (that can be casted to `APIGatewayProxyEventV2`) like:
        {
            "version": "2.0",
            "routeKey": "POST /telegram-webhook",
            "rawPath": "/telegram-webhook",
            "rawQueryString": "",
            "headers": {
                "accept-encoding": "gzip, deflate",
                "content-length": "348",
                "content-type": "application/json",
                "host": "0uneqyoes2.execute-api.eu-south-1.amazonaws.com",
                "x-amzn-trace-id": "Root=1-691af53b-7f08661e2ad1bee150eeb0ae",
                "x-forwarded-for": "91.108.5.183",
                "x-forwarded-port": "443",
                "x-forwarded-proto": "https",
                "x-telegram-bot-api-secret-token": "t**REDACTED**"
            },
            "requestContext": {
                "accountId": "477353422995",
                "apiId": "0uneqyoes2",
                "authorizer": {
                    "lambda": {
                        "ts": "2025-11-17T10:04:11.283434+00:00"
                    }
                },
                "domainName": "0uneqyoes2.execute-api.eu-south-1.amazonaws.com",
                "domainPrefix": "0uneqyoes2",
                "http": {
                    "method": "POST",
                    "path": "/telegram-webhook",
                    "protocol": "HTTP/1.1",
                    "sourceIp": "91.108.5.183",
                    "userAgent": ""
                },
                "requestId": "ULtBbh1BMu8EMxg=",
                "routeKey": "POST /telegram-webhook",
                "stage": "$default",
                "time": "17/Nov/2025:10:13:15 +0000",
                "timeEpoch": 1763374395989
            },
            "body": "{\"update_id\":876674393,\n\"message\":{\"message_id\":34426,\"from\":{\"id\":2137200685,\"is_bot\":false,\"first_name\":\"Paolo\",\"username\":\"puntonim\",\"language_code\":\"en\"},\"chat\":{\"id\":2137200685,\"first_name\":\"Paolo\",\"username\":\"puntonim\",\"type\":\"private\"},\"date\":1763374395,\"text\":\"/echo Hello Botte!\",\"entities\":[{\"offset\":0,\"length\":5,\"type\":\"bot_command\"}]}}",
            "isBase64Encoded": false
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
        $ curl -X POST https://0uneqyoes2.execute-api.eu-south-1.amazonaws.com/message \
           -H 'x-telegram-bot-api-secret-token: XXX' \
           -d '{"text": "Hello World"}'
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
    # Commands webhook example: https://github.com/eternnoir/pyTelegramBotAPI/blob/master/examples/serverless/aws_lambda_function.py

    # To configure the webhook on the Telegram side, make this request:
    # $ make webhook-configure

    logger.info("ENDPOINT TELEGRAM WEBHOOK: START")

    api_event = APIGatewayProxyEventV2(event)

    if not api_event.body:
        return aws_lambda_utils.BadRequest400Response("Body required").to_dict()

    try:
        body: dict = api_event.json_body
    except JSONDecodeError:
        return aws_lambda_utils.BadRequest400Response(
            "Body must be JSON encoded"
        ).to_dict()

    update = telebot.types.Update.de_json(body)
    bot = _init_bot()
    try:
        bot.process_new_updates([update])
    except Exception:
        # This Lambda should never fail, otherwise Telegram keeps delivering the webhook
        #  triggering this Lambda every minute.
        logger.exception("Exception while processing the Telegram webhook")

    # Respond to the user directly - within the 200 response we are about to send -
    #  seems NOT to work!!!
    # But no worries, we just send a regular message instead.
    # Docs: https://core.telegram.org/bots/faq#how-can-i-make-requests-in-response-to-updates
    # response_body = {
    #     "method": "sendMessage",
    #     "chat_id": settings.PUNTONIM_CHAT_ID,
    #     "text": "Ok, one sec...",
    #     "reply_to_message_id": body["message"]["message_id"],
    # }

    return aws_lambda_utils.Ok200Response().to_dict()


def _init_bot():
    # TODO this code could be moved to a `domain` dir, but since this project doesn't
    #  have such a dir yet, then I'll keep it here. When I happen to add more logic,
    #  like if I integrate handle_shared_link() with kbee, then I will create a first
    #  domain.

    global bot
    if bot:
        return bot

    bot = telebot.TeleBot(settings.TELEGRAM_TOKEN, threaded=False)

    # IMP: all message handlers are tested in the order they were added.
    #  So leave the catch-all as last one.

    # Handle /start and /help commands to @realbottebot.
    @bot.message_handler(commands=["help", "start"], content_types=["text"])
    def welcome(message: telebot.types.Message):
        """
        The event sent to this Lambda has `event.body` like:
            {
                "update_id": 876674396,
                "message": {
                    "message_id": 34435,
                    "from": {
                        "id": 2137200685,
                        "is_bot": false,
                        "first_name": "Paolo",
                        "username": "puntonim",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 2137200685,
                        "first_name": "Paolo",
                        "username": "puntonim",
                        "type": "private"
                    },
                    "date": 1763378501,
                    "text": "/start",
                    "entities": [
                        {
                            "offset": 0,
                            "length": 6,
                            "type": "bot_command"
                        }
                    ]
                }
            }
        """
        if message.chat.id != int(settings.PUNTONIM_CHAT_ID):
            raise UnknownChatId(message.chat.id)
        bot.reply_to(
            message,
            "Hi there, I am Botte.\nI am here to echo your kind words back to you.",
        )

    # Handle /echo commands to @realbottebot.
    @bot.message_handler(commands=["echo"], content_types=["text"])
    def echo(message: telebot.types.Message):
        """
        The event sent to this Lambda has `event.body` like:
            {
                "update_id": 876674393,
                "message": {
                    "message_id": 34426,
                    "from": {
                        "id": 2137200685,
                        "is_bot": false,
                        "first_name": "Paolo",
                        "username": "puntonim",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 2137200685,
                        "first_name": "Paolo",
                        "username": "puntonim",
                        "type": "private"
                    },
                    "date": 1763374395,
                    "text": "/echo Hello Botte!",
                    "entities": [
                        {
                            "offset": 0,
                            "length": 5,
                            "type": "bot_command"
                        }
                    ]
                }
            }
        """
        if message.chat.id != int(settings.PUNTONIM_CHAT_ID):
            raise UnknownChatId(message.chat.id)
        bot.reply_to(message, message.text)
        # Regular message, not a reply:
        # bot.send_message(message.chat.id, "Got it: " + message.text)

    # Example of an actual complex command from the old Botte in patatrack-monorepo.
    # @bot.message_handler(regexp="confirm_\\S+", content_types=["text"])
    # def confirm(message: telebot.types.Message):
    #     """
    #     Entrypoint for any confirm user command.
    #     At the moment we support one command only.
    #
    #     1. Confirm Pending Trade user command
    #     -------------------------------------
    #     /confirm_ptid_15
    #     /confirm_ptid_15 fees 0.33
    #     """
    #     text = message.text  # Eg. "/confirm_ptid_15 fees 0.33".
    #     domain = CommandConfirmDomain(text)
    #     try:
    #         text = domain.handle_command()
    #     except domain_exceptions.FormatError:
    #         text = "Format error! Supported formats:\n"
    #         text += "/confirm_ptid_15\n"
    #         text += "/confirm_ptid_15 fees 0.33\n"
    #     except domain_exceptions.SubcommandUnknown:
    #         text = "Subcommand unknown! Supported formats:\n"
    #         text += "/confirm_ptid_15\n"
    #         text += "/confirm_ptid_15 fees 0.33\n"
    #     except domain_exceptions.PtidInvalid as exc:
    #         text = f"Invalid ptid: {exc.ptid}"
    #     except domain_exceptions.ExtraArgUnknown as exc:
    #         text = f"Extra arg unknown: {exc.extra_arg}"
    #     except domain_exceptions.FeesValueNonFloat as exc:
    #         text = f"Invalid fees value: {exc.value}"
    #
    #     bot.reply_to(message, text)

    # Handle links shared with @realbottebot.
    # Note: the content_type "url" does not work.
    @bot.message_handler(content_types=["text"])
    def handle_shared_link(message: telebot.types.Message):
        """
        The event sent to this Lambda has `event.body` like:
            {
                "update_id": 876674395,
                "message": {
                    "message_id": 34434,
                    "from": {
                        "id": 2137200685,
                        "is_bot": false,
                        "first_name": "Paolo",
                        "username": "puntonim",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 2137200685,
                        "first_name": "Paolo",
                        "username": "puntonim",
                        "type": "private"
                    },
                    "date": 1763378364,
                    "text": "https://youtu.be/eytD1MZUHNY?si=sOdAbx3kEpjNSLDF",
                    "entities": [
                        {
                            "offset": 0,
                            "length": 48,
                            "type": "url"
                        }
                    ],
                    "link_preview_options": {
                        "url": "https://youtu.be/eytD1MZUHNY?si=sOdAbx3kEpjNSLDF"
                    }
                }
            }
        """
        if message.chat.id != int(settings.PUNTONIM_CHAT_ID):
            raise UnknownChatId(message.chat.id)

        # Check if the type is "url".
        is_url_found = False
        for entity in message.entities:
            if entity.to_dict().get("type") == "url":
                is_url_found = True

        if not is_url_found:
            bot.reply_to(
                message, "I support only the command /echo and the sharing of links"
            )
        else:
            bot.reply_to(
                message, "Thanks! Soon I will start collecting links for kbee..."
            )

    return bot


class BaseEndpointWebhookException(Exception):
    pass


class UnknownChatId(BaseEndpointWebhookException):
    def __init__(self, chat_id):
        self.chat_id = chat_id
        super().__init__(f"Not a chat id with @puntonim: {chat_id}")
