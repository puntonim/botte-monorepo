import requests


class TestE2eEndpointIntrospection:
    def test_version(self, base_url):
        url = f"{base_url}/version"
        response = requests.get(url)
        response.raise_for_status()
        assert response.json()
        # {
        #     "appName": "Botte",
        #     "app": "0.1.0",
        #     "python": "3.11.6 (main, Oct  2 2023, 18:13:32) [GCC 7.3.1 20180712 (Red Hat 7.3.1-17)]",
        #     "boto3": "1.27.1",
        #     "botocore": "1.30.1",
        # }
        assert response.json()["appName"] == "Botte BE"

    # @pytest.mark.skip(
    #     reason="Don't always run this as it causes the sending of an email"
    # )
    def test_lambda_to_raise_exception_and_email_sent(self, base_url):
        url = f"{base_url}/unhealth"
        response = requests.get(url)
        assert response.status_code == 500
