import django_gcp_iam_auth.postgresql.base
from django_gcp_iam_auth.postgresql.base import DatabaseWrapper


def test_simple():

    settings = {
        "ENGINE": "django_gcp_iam_auth.postgresql.postgresql",
        "HOST": "mydbhost",
        "NAME": "mySAusername@iam",
        "OPTIONS": {"gcp_iam_auth": True},
        "PASSWORD": "not-used",
        "PORT": 5432,
		"USER": "some-iam-user",
	}

    x = DatabaseWrapper(settings)
    print(x)

test_simple()
