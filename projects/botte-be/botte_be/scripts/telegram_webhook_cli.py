"""
Script to manage the Telegram webhook configuration for @realbottebot.

Usage:
 $ make webhook-configure
 $ make webhook-info
 Which is equivalent to:
 $ poetry run telegram-webhook configure|info
 Also, with the virtual env activated:
 $ telegram-webhook configure|info
"""

import argparse
import json

import aws_lambda_client
import requests
import settings_utils
import text_utils

_CONFIGURE_CMD = "configure"
_INFO_CMD = "info"

# Argparse docs: https://docs.python.org/3/library/argparse.html
# Argparse tutorial: https://docs.python.org/3/howto/argparse.html#argparse-tutorial
parser = argparse.ArgumentParser(
    prog="telegram-webhook", description="Configure the Telegram webhook for Botte."
)

# Add the main command: summaries or details.
parser.add_argument(
    "command",
    help="configure: to setup the webhook; info: to get info about the existing webhook.",
    choices=[_CONFIGURE_CMD, _INFO_CMD],
    type=str,
)


Col = text_utils.FormatForConsole


def main():
    print(f"\n{Col.BOLD}{Col.UNDERLINE}TELEGRAM WEBHOOK CONFIGURATION{Col.ENDC}\n")
    args = parser.parse_args()

    if args.command == _CONFIGURE_CMD:
        return _configure()
    elif args.command == _INFO_CMD:
        return _info()


def _info():
    print("This is the current webhook configuration just read from Telegram:")
    url = f"https://api.telegram.org/bot{_get_telegram_token()}/getWebhookInfo"
    response = requests.get(url=url)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=4))


def _configure():
    # To configure the webhook on the Telegram side, make this request:
    # $ curl https://api.telegram.org/bot<TOKEN>/setWebhook \
    #    -F "url=https://0uneqyoes2.execute-api.eu-south-1.amazonaws.com/telegram-webhook" \
    #    -F "secret_token=<API_AUTHORIZER_TOKEN>"
    # And to DELETE the webhook:
    # $ curl https://api.telegram.org/bot<TOKEN>/setWebhook \
    #    -F "url="
    # Docs: https://core.telegram.org/bots/api#setwebhook

    print("I am about to write a new configuration for the webhook to Telegram:")
    url = f"https://api.telegram.org/bot{_get_telegram_token()}/setWebhook"
    url += f"?url={_get_lambda_url()}"
    url += f"&secret_token={_get_api_authorizer_token()}"
    response = requests.get(url=url)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=4))


# Read the Telegram token from Param Store.
def _get_telegram_token():
    return settings_utils.get_string_from_env_or_aws_parameter_store(
        env_key="TELEGRAM_TOKEN",
        param_store_key_path="/botte-be/prod/telegram-token",
        default="XXX",
        param_store_cache_ttl=60,
    )


# Read the API Auth token from Param Store.
def _get_api_authorizer_token():
    return settings_utils.get_string_from_env_or_aws_parameter_store(
        env_key="API_AUTHORIZER_TOKEN",
        param_store_key_path="/botte-be/prod/api-authorizer-token",
        default="XXX",
        param_store_cache_ttl=60,
    )


def _get_lambda_url():
    base_url, url_path, method = aws_lambda_client.AwsLambdaClient().get_url(
        "botte-be-prod-endpoint-telegram-webhook"
    )
    return base_url + url_path
