from unittest import mock

import pytest
from oauth2 import oauth2
from requests import Response


FAKE_OAUTH_PROVIDER_NAME = "fakeprovider"


def _var_get_replacement(*args, **kwargs):
    values = {
        oauth2.OAUTH2_TOKEN_KEY: {
            FAKE_OAUTH_PROVIDER_NAME: {
                "access_token": "fakeaccess",
                "refresh_token": "fakerefresh",
            }
        },
        oauth2.OAUTH2_AUTH_KEY: {FAKE_OAUTH_PROVIDER_NAME: "fakeauthtoken"},
        oauth2.OAUTH2_PROVIDERS_KEY: {
            FAKE_OAUTH_PROVIDER_NAME: {
                "client_id": "fakeclient",
                "client_secret": "fakesecret",
            }
        },
    }
    return values[args[0]]


@pytest.fixture
def oauth_provider_var_mock():
    with mock.patch("oauth2.oauth2.Variable") as MockVariable:
        MockVariable.get.side_effect = _var_get_replacement
        yield MockVariable


def _make_response(*args, **kwargs):
    """
    Mock the request used during license URL validation. Most times the results of this
    function are expected to end with a `/`, so if the URL provided does not we add it.
    """
    response: Response = mock.Mock(spec=Response)
    if args:
        response.ok = True
        url = args[0]
        if isinstance(url, str) and not url.endswith("/"):
            url += "/"
        response.url = url
    return response


@pytest.fixture(autouse=True)
def requests_get_mock():
    """
    Mock request.get calls that occur during testing done by the
    `common.urls.rewrite_redirected_url` function.
    """
    with mock.patch("common.urls.requests_get", autospec=True) as mock_get:
        mock_get.side_effect = _make_response
        yield
