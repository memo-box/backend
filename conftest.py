import os
import django
import pytest

# Set up Django for pytest
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "memobox.settings")
django.setup()


# Common fixtures that can be used across all tests
@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user_data():
    return {"email": "test@example.com", "name": "Test User", "password": "testpass123"}


@pytest.fixture
def user(user_data):
    from leitner.models import CustomUser

    return CustomUser.objects.create_user(
        email=user_data["email"], name=user_data["name"], password=user_data["password"]
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def language_data():
    return [{"name": "English", "code": "en"}, {"name": "Spanish", "code": "es"}]


@pytest.fixture
def languages(language_data):
    from leitner.models import Language

    return [
        Language.objects.create(name=data["name"], code=data["code"])
        for data in language_data
    ]


@pytest.fixture
def box(user, languages):
    from leitner.models import Box

    return Box.objects.create(
        name="Test Box",
        description="A test box",
        user=user,
        source_language=languages[0],
        target_language=languages[1],
    )


@pytest.fixture
def card(box):
    from leitner.models import Card

    return Card.objects.create(source_text="Hello", target_text="Hola", box=box)
