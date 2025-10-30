"""
A very basic settings manager. I chose this because this app requires only a few
 settings and no special features.

A better alternative, in case the app requires more settings and advanced features,
 is Dynaconf.
"""

from pathlib import Path

import settings_utils

CURR_DIR = Path(__file__).parent
ROOT_DIR = CURR_DIR.parent.parent


class _Settings:
    """
    Settings class that can be used in 2 ways:
     - directly as a class: in this case name it `settings`;
     - as an instance: in this case name it _Settings and define a global var
        `settings = _Settings()`.

    The advantage of the instance is that I can define attrs that are methods using
     the decorator @property, so their value is lazily computed.
     This is useful when using `settings_utils.get_string_from_env_or_aws_parameter_store()`
     that must be invoked lazily, otherwise vcr.py can't catch it.

    Usage:
        from conf import settings
        print(setting.APP_NAME)
    """

    APP_NAME = "Botte BE"
    IS_TEST = False

    # The token to be used in every HTTP request received by Botte.
    DO_ENABLE_API_AUTHORIZER = True
    API_AUTHORIZER_TOKEN = settings_utils.get_string_from_env(
        "API_AUTHORIZER_TOKEN", "XXX"
    )

    # You can get it by sending a message to @JsonDumpBot.
    PUNTONIM_CHAT_ID = "2137200685"

    # Telegram token: read from env vars (when running in AWS Lambda) or from
    #  Param Store (in dev or when recording tests, which is better than using a local
    #  file with the secret in plain-text).
    # Mind that it needs to be a @property for lazily evaluation, so vcr.py can catch
    #  it on time.
    # And that in order to use @property we had to make `settings` an instance,
    #  unlike other projects where `settings` is this class (now renamed _Settings).
    # And also, mind that in conftest.py we have to use the fixture clear_cache_for_aws_param_store_client()
    #  to clear AWS Param Store client cache, to make its HTTP interactions
    #  deterministic (otherwise vcr.py fails).
    @property
    def TELEGRAM_TOKEN(self):
        return settings_utils.get_string_from_env_or_aws_parameter_store(
            env_key="TELEGRAM_TOKEN",
            param_store_key_path="/botte-be/prod/telegram-token",
            default="XXX",
            param_store_cache_ttl=60,
        )


class _TestSettings:
    IS_TEST = True


settings = _Settings()
