# django_gcp_iam_auth

django db engine for using IAM Authentication with Google Cloud SQL.

Available on pypi at https://pypi.org/project/django-gcp-iam-auth

## Installation

```
pip install django_gcp_iam_auth
```

## Usage

Update the DATABASES entry to replace the ENGINE for your connection.

```
DATABASES["default"]["ENGINE"]  = "django_gcp_iam_auth.postgresql"
```
