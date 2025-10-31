import botte_http_client


class TestE2eEndpointIntrospection:
    def test_version(self):
        client = botte_http_client.BotteHttpClient()
        response = client.get_version()
        # response.data like:
        # {
        #     "appName": "Botte BE",
        #     "app": "1.0.0",
        #     "python": "3.13.7 (main, Sep 26 2025, 14:01:44) [GCC 11.5.0 20240719 (Red Hat 11.5.0-5)]",
        #     "boto3": "1.40.4",
        #     "botocore": "1.40.4",
        #     "pydantic": [
        #         "pydantic version: 2.11.7",
        #         "pydantic-core version: 2.33.2",
        #         "pydantic-core build: profile=release pgo=false",
        #         "python version: 3.13.7 (main, Sep 26 2025, 14:01:44) [GCC 11.5.0 20240719 (Red Hat 11.5.0-5)]",
        #         "platform: Linux-5.10.244-267.968.amzn2.x86_64-x86_64-with-glibc2.34",
        #         "related packages: pydantic-settings-2.9.1 typing_extensions-4.14.0",
        #         "commit: unknown",
        #     ],
        #     "sqlite3": "3.40.0",
        # }
        assert response.data["appName"] == "Botte BE"

    # @pytest.mark.skip(
    #     reason="Don't always run this as it causes the sending of an email"
    # )
    def test_unhealth(self):
        client = botte_http_client.BotteHttpClient()
        response = client.get_unhealth()
        assert response.data["message"] == "Internal Server Error"
