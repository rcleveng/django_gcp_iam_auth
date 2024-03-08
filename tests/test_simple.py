import copy
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock
from unittest.mock import patch

from django_gcp_iam_auth.postgresql.base import DatabaseWrapper
from google.auth.credentials import Credentials

TEST_DATABASES = {
    "default": {
        "ENGINE": "django_gcp_iam_auth.postgresql.postgresql",
        "HOST": "mydbhost",
        "NAME": "mySAusername@iam",
        "OPTIONS": {"gcp_iam_auth": True},
        "PASSWORD": "not-used",
        "PORT": 5432,
        "USER": "some-iam-user",
    },
}


class FakeCredentials(Credentials):
    refreshed: bool = False

    def __init__(self, token):
        self.token = token
        self.expiry = None

    def refresh(self, request):
        self.refreshed = True


def now():
    now = datetime.now(timezone.utc)
    now = now.replace(tzinfo=None)
    return now


def expired_timestamp():
    now = datetime.now(timezone.utc)
    now = now.replace(tzinfo=None)
    return now - timedelta(days=1)


class TestBasics(unittest.TestCase):
    _creds: FakeCredentials
    _wrapper: DatabaseWrapper

    def setUp(self):
        self._creds = self._make_credentials()
        self._wrapper = DatabaseWrapper(TEST_DATABASES['default'].copy())

    def _make_credentials(self) -> FakeCredentials:
        return FakeCredentials(token='1234')

    @patch('google.auth.default', autospec=True)
    def test_simple(self, mock_auth):
        mock_auth.return_value = (self._creds, mock.sentinel.project)

        params = self._wrapper.get_connection_params()
        self.assertEqual(params['password'], '1234')
        self.assertFalse(self._creds.refreshed)

    @patch('google.auth.default', autospec=True)
    def test_refresh_needed(self, mock_auth):
        mock_auth.return_value = (self._creds, mock.sentinel.project)
        self._creds.expiry = expired_timestamp()

        self.assertFalse(self._creds.refreshed)
        params = self._wrapper.get_connection_params()
        self.assertEqual(params['password'], '1234')
        self.assertTrue(self._creds.refreshed)

    @patch('google.auth.default', autospec=True)
    def test_no_google_auth_called(self, mock_auth):
        db = copy.deepcopy(TEST_DATABASES['default'])
        db['OPTIONS'].pop('gcp_iam_auth')
        dbw = DatabaseWrapper(db)

        dbw.get_connection_params()
        mock_auth.assert_not_called()


if __name__ == '__main__':
    unittest.main()
