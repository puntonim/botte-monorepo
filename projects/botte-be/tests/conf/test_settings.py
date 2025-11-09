from unittest import mock

from botte_be.conf import settings, settings_module


class TestSettings:
    def test_is_test(self):
        assert settings_module.IS_TEST is True
        assert settings.IS_TEST is True

    @mock.patch("botte_be.conf.settings_module.IS_TEST", False)
    def test_prod_settings(self):
        """
        The goal is to test the *prod* settings.
        """
        assert settings.APP_NAME == "Botte BE"
        assert settings.TELEGRAM_TOKEN == "XXX"
        assert settings.IS_TEST is False

    def test_test_settings(self):
        """
        The goal is to test the *test* settings.
        """
        assert settings.APP_NAME == "Botte BE"
        assert settings.IS_TEST is True

        with mock.patch(
            "settings_utils.get_string_from_env_or_aws_parameter_store",
            return_value="ZZZ",
        ):
            assert settings.TELEGRAM_TOKEN == "ZZZ"
