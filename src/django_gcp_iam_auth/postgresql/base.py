import copy
from django.db.backends.postgresql import base

try:
    import google.auth
    import google.auth.exceptions
    from google.auth.transport import requests
    from google.auth.credentials import Credentials, Scoped, TokenState

except google.auth.exceptions.DefaultCredentialsError:
    pass

CLOUDSQL_IAM_LOGIN_SCOPE = ["https://www.googleapis.com/auth/sqlservice.login"]

class DatabaseWrapper(base.DatabaseWrapper):
    def get_connection_params(self):
        params = super().get_connection_params()
        # need to remove this otherwise we'll get errors like
        # invalid dsn: invalid connection option "gcp_iam_auth"
        if params.pop("gcp_iam_auth", None):

            # TODO - check if _credentials already exists and the token is still valid
            # refreshing if needed
            self._credentials, _ = google.auth.default(scopes=CLOUDSQL_IAM_LOGIN_SCOPE)
            if not self._credentials.token_state == TokenState.FRESH:
                print('** Refreshing token')
                self._credentials.refresh(requests.Request())
            params.setdefault("port", 5432)
            # Set password to newly fetched oauth token
            params["password"] = self._credentials.token
            print('** USING GCP IAM TOKEN FOR PASSWORD')

        return params
    

def _downscope_credentials(
    credentials: Credentials,
    ) -> Credentials:

    # credentials sourced from a service account or metadata are children of
    # Scoped class and are capable of being re-scoped
    if isinstance(credentials, Scoped):
        scoped_creds = credentials.with_scopes(scopes=CLOUDSQL_IAM_LOGIN_SCOPE)
    # authenticated user credentials can not be re-scoped
    else:
        # create shallow copy to not overwrite scopes on default credentials
        scoped_creds = copy.copy(credentials)
        # overwrite '_scopes' to down-scope user credentials
        # Cloud SDK reference: https://github.com/google-cloud-sdk-unofficial/google-cloud-sdk/blob/93920ccb6d2cce0fe6d1ce841e9e33410551d66b/lib/googlecloudsdk/command_lib/sql/generate_login_token_util.py#L116
        scoped_creds._scopes = CLOUDSQL_IAM_LOGIN_SCOPE
    # down-scoped credentials require refresh, are invalid after being re-scoped
    request = google.auth.transport.requests.Request()
    scoped_creds.refresh(request)
    return scoped_creds