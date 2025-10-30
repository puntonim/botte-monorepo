import re
import subprocess
import sys
from pathlib import Path

import pytest
import settings_utils

CURR_DIR = Path(__file__).parent
ROOT_DIR = CURR_DIR.parent


@pytest.fixture(scope="session")
def monkeysession(request):
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def base_url(request) -> str:
    try:
        output = subprocess.run("sls info", shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print(
            "The command `sls info` returned an error -  we need it in order to"
            " find out the base url"
        )
        sys.exit(1)
    text = output.stderr.decode()
    match = re.search(r"GET - (\S+)/version", text, re.M)
    if not match:
        print("Couldn't parse the base url from the output of `sls info`")
        sys.exit(1)
    base_url = match.group(1)
    print(f"\n\n> Base url, detected by Serverless: {base_url}\n")
    return base_url


@pytest.fixture(scope="session")
def http_auth_header(request) -> dict:
    token = settings_utils.get_string_from_env_or_aws_parameter_store(
        env_key="API_AUTHORIZER_TOKEN",
        param_store_key_path="/botte-be/prod/api-authorizer-token",
        default="XXX",
        param_store_cache_ttl=60 * 5,
    )

    return {"Authorization": token}
