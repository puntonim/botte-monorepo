import json
import os
import re
from collections.abc import Iterator

import pytest
from _pytest.fixtures import SubRequest
from _pytest.unittest import TestCaseFunction
from aws_parameter_store_client import aws_parameter_store_client
from vcr.cassette import Cassette
from vcr.errors import CannotOverwriteExistingCassetteException

from botte_be.conf.settings import _TestSettings, settings
from botte_be.views.views_utils import powertools_logger

IS_VCR_EPISODE_OR_ERROR = True  # False to record new cassettes.
IS_VCR_ENABLED = True


def pytest_collection_modifyitems(items: list[TestCaseFunction]):
    """
    Enable vcr for all tests.
    By marking all tests with `vcr`.

    Pytest markers:
        novcr
            Use this marker to exclude vcr on a function/class/module:
            `@pytest.mark.novcr` for functions and classes
            `pytestmark = pytest.mark.novcr` for modules.
        slow
            Slow tests are skipped by default. Use this marker for slow tests.
            Same syntax as documented in `novcr`.
            Then, to run only the slow tests:
            $ pytest -m slow tests/
        withlogs
            Logging is disabled in tests by default. Use this marker to enable logging.
            Same syntax as documented in `novcr`.
            Then, use the test fixture `caplog`.
            See example in tests/views/test_endpoint_introspection_view.py::test_health.
    """
    for item in items:
        if "slow" in item.keywords and (
            not item.config.getoption("-m") or item.config.getoption("-m") != "slow"
        ):
            item.add_marker("skip")
        if "novcr" in item.keywords:
            continue
        item.add_marker("vcr")


def pytest_configure(config):
    config.addinivalue_line("markers", "withlogs: enable logs")
    config.addinivalue_line("markers", "novcr: disable vcr")
    config.addinivalue_line("markers", "slow: slow test")


@pytest.fixture(autouse=True, scope="function")
def test_settings_fixture(monkeypatch, request):
    # Copy all test settings to settings.
    attr_names = [
        attr
        for attr in dir(_TestSettings)
        if not callable(getattr(_TestSettings, attr)) and not attr.startswith("__")
    ]
    for attr_name in attr_names:
        attr_value = getattr(_TestSettings, attr_name)
        setattr(settings, attr_name, attr_value)


_ORIGINAL_LOG_LEVEL = None


@pytest.fixture(autouse=True, scope="function")
def logging_fixture(request):
    """
    Logging is disabled in tests by default. Use the pytest marker `withlogs` to enable
    logging. Mark the test function/class/module with:
        `@pytest.mark.withlogs` for functions and classes
        `pytestmark = pytest.mark.withlogs` for modules.
    Then, use the fixture `caplog`.
    See example in tests/views/test_endpoint_introspection_view.py::test_health.
    """
    global _ORIGINAL_LOG_LEVEL
    if _ORIGINAL_LOG_LEVEL is None:
        _ORIGINAL_LOG_LEVEL = powertools_logger.logger.logger_handler.level

    if "withlogs" in request.keywords:
        powertools_logger.logger.logger_handler.level = _ORIGINAL_LOG_LEVEL
        yield
        return
    else:
        powertools_logger.logger.logger_handler.level = 100
        yield
        return
    yield


def is_vcr_episode_or_error():
    global IS_VCR_EPISODE_OR_ERROR
    if "IS_VCR_EPISODE_OR_ERROR" in os.environ:
        IS_VCR_EPISODE_OR_ERROR = os.getenv(
            "IS_VCR_EPISODE_OR_ERROR", ""
        ).lower().strip() in ("true", "yes")
    return IS_VCR_EPISODE_OR_ERROR


def get_record_mode() -> str:
    return "none" if is_vcr_episode_or_error() else "new_episodes"


def is_vcr_enabled() -> bool:
    global IS_VCR_ENABLED
    if "IS_VCR_ENABLED" in os.environ:
        IS_VCR_ENABLED = os.getenv("IS_VCR_ENABLED", "").lower().strip() in (
            "true",
            "yes",
        )
    return IS_VCR_ENABLED


def get_match_on() -> tuple:
    """
    The default behavior for request matching is:
      ['method', 'scheme', 'host', 'port', 'path', 'query'].
    We also want to match on body.
    """
    return ("method", "scheme", "host", "port", "path", "query", "body")


def before_record_request(request):
    """
    Use this to redact sensitive info in the REQUEST, when the info is NOT:
    - NOT a request HTTP header: otherwise you should redact it with `filter_headers`
       in vcr_config();
    - NOT a request query param: otherwise you should redact it with
       `filter_query_parameters` in vcr_config().
    """
    # Redact Telegram secret in the url (but it's not a query param).
    if "api.telegram.org/bot" in request.uri:
        request.uri = re.sub(
            r"api.telegram.org/bot([^/]+)",
            "api.telegram.org/bot**REDACTED**",
            request.uri,
        )

    return request


def before_record_response(response):
    """
    Use this to redact sensitive info in the RESPONSE.
    There is no other way to edit headers or content in the response.
    """
    # Decode JSON body.
    try:
        data = json.loads(response["body"]["string"].decode())
    except json.JSONDecodeError:
        return response

    if not data:
        return response

    # Redact access token (general rule).
    if "access_token" in data:
        data["access_token"] = "**REDACTED**"

    # Redact AWS Parameter Store secrets.
    if isinstance(data, dict):
        value = data.get("Parameter", {}).get("Value")
        # Special case: redact the Telegram token, but keep the part before ":" (which is
        #  the userid) otherwise the telebot lib fails.
        if (
            value
            and data.get("Parameter", {}).get("Name", "").endswith("telegram-token")
            and ":" in value
        ):
            data["Parameter"]["Value"] = value[: value.find(":") + 1] + "**REDACTED**"

        elif value and data.get("Parameter", {}).get("Type") == "SecureString":
            data["Parameter"]["Value"] = value[:1] + "**REDACTED**"

    # Re-encode JSON body.
    response["body"]["string"] = json.dumps(data).encode()
    return response


@pytest.fixture(scope="session")
def vcr_config():
    """
    Configure VCR.

    - Set the record mode.
    - Ignore some headers and hosts.
    - The default behavior for request matching is:
      ['method', 'scheme', 'host', 'port', 'path', 'query'].
      We also want to match on body.
    """

    if not is_vcr_enabled():
        # Disable VCR.
        return {"before_record": lambda *args, **kwargs: None}

    return {
        ## Filter REQUEST headers.
        "filter_headers": (
            ("Authorization", "**REDACTED**"),
            # ("User-Agent", "**REDACTED**"),
            ("X-Amz-Security-Token", "**REDACTED**"),
            ("X-Amz-Content-SHA256", "**REDACTED**"),
            "X-Amz-Date",
            "X-Amz-Target",
            "amz-sdk-invocation-id",
            "amz-sdk-request",
        ),
        #
        ## Filter REQUEST query param like in:
        #  requests.get('http://api.com/getdata?api_key=secretstring')
        # "filter_query_parameters": ("api_key",),
        #
        ## Filter REQUEST POST data like in:
        #  requests.post('http://api.com/postdata', data={'api_key': 'secretstring'})
        # "filter_post_data_parameters": (
        #     # Reborn automator.
        #     ("mail", "**REDACTED**"),
        #     ("pass", "**REDACTED**"),
        #     ("codice_sessione", "**REDACTED**"),
        # ),
        "decode_compressed_response": True,
        "ignore_hosts": ("localhost",),
        "record_mode": get_record_mode(),
        "match_on": get_match_on(),
        "before_record_request": before_record_request,
        "before_record_response": before_record_response,
    }


@pytest.fixture(autouse=True, scope="function")
def assert_all_played(request: SubRequest, vcr: Cassette) -> Iterator:
    """
    Ensure that all episodes have been played in the current test.
    Only if the current test has a cassette.
    """
    yield
    if is_vcr_enabled() and is_vcr_episode_or_error() and vcr:
        assert vcr.all_played


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call():
    """
    Enrich `CannotOverwriteExistingCassetteException` original exception with some
    useful info.
    """
    try:
        outcome = yield
        outcome.get_result()
    except Exception as exc:
        if isinstance(exc, CannotOverwriteExistingCassetteException) or isinstance(
            getattr(exc, "kwargs", dict()).get("error"),
            CannotOverwriteExistingCassetteException,
        ):
            args = list(exc.args)
            args[0] += "\nUse IS_VCR_EPISODE_OR_ERROR=no to record a new episode."
            exc.args = tuple(args)
        raise


@pytest.fixture(autouse=True, scope="function")
def clear_cache_for_aws_param_store_client():
    """
    Clear the Python in-memory cache (for time) used by AWS Param Store client.
    Which is used in settings.py by `settings_utils.get_string_from_env_or_aws_parameter_store()`.
    Without clearing the cache the HTTP interactions are not deterministic and vcr.py
     raises exceptions for episodes not recorded or not played.
    """
    aws_parameter_store_client.cache.clear_cache()


@pytest.fixture(scope="session")
def monkeysession(request):
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


# @pytest.fixture(autouse=True, scope="function")
# def mock_aws_credentials(monkeypatch, request):
#     """
#     Boto3 requires existing credentials.
#     """
#     if "nomoto" not in request.keywords:
#         # See: http://docs.getmoto.org/en/latest/docs/getting_started.html#example-on-usage
#         monkeypatch.setenv("AWS_ACCESS_KEY_ID", "pytesting")
#         monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "pytesting")
#         monkeypatch.setenv("AWS_SECURITY_TOKEN", "pytesting")
#         monkeypatch.setenv("AWS_SESSION_TOKEN", "pytesting")
#         monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-south-1")
