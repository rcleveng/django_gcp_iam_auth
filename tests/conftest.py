from django.conf import settings

DATABASES = {
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


def pytest_configure():
    settings.configure(
        DEBUG=True,
        USE_TZ=False,
        DATABASES=DATABASES.copy(),
        )
