from typing import Any, Dict

from django.db.backends.postgresql import base

try:
    import google.auth
    import google.auth.exceptions
    from google.auth.credentials import TokenState
    from google.auth.transport import requests

except google.auth.exceptions.DefaultCredentialsError:
    pass

CLOUDSQL_IAM_LOGIN_SCOPE = ["https://www.googleapis.com/auth/sqlservice.login"]


class DatabaseWrapper(base.DatabaseWrapper):

    def get_connection_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = super().get_connection_params()
        # need to remove this otherwise we'll get errors like
        #   'invalid dsn: invalid connection option "gcp_iam_auth"'
        if params.pop("gcp_iam_auth", None):
            self._credentials, _ = google.auth.default(scopes=CLOUDSQL_IAM_LOGIN_SCOPE)
            if not self._credentials.token_state == TokenState.FRESH:
                self._credentials.refresh(requests.Request())
            params.setdefault("port", 5432)
            # TODO - should we add in a resource restriction for the
            # DB instance?
            # https://cloud.google.com/iam/docs/downscoping-short-lived-credentials#auth_downscoping_token_broker-python
            # Set password to newly fetched access token
            params["password"] = self._credentials.token

        return params
