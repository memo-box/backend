import pytest
from rest_framework.test import APIClient
from leitner.models import CustomUser, Language, Box, Card
from rest_framework.test import APIRequestFactory


@pytest.fixture
def api_client():
    """Returns an authenticated API client."""
    return APIClient()


@pytest.fixture
def user_data():
    """Returns default user data."""
    return {"email": "test@example.com", "name": "Test User", "password": "testpass123"}


@pytest.fixture
def user(user_data):
    """Creates and returns a user."""
    return CustomUser.objects.create_user(
        email=user_data["email"], name=user_data["name"], password=user_data["password"]
    )


@pytest.fixture
def other_user_data():
    """Returns data for another user."""
    return {"email": "otheruser@example.com", "name": "Other User", "password": "testpass123"}


@pytest.fixture
def other_user(other_user_data):
    """Creates and returns another user."""
    return CustomUser.objects.create_user(
        email=other_user_data["email"], name=other_user_data["name"], password=other_user_data["password"]
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Returns an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def language_data():
    """Returns default language data."""
    return [{"name": "English", "code": "en"}, {"name": "Spanish", "code": "es"}]


@pytest.fixture
def languages(language_data):
    """Creates and returns languages."""
    return [
        Language.objects.create(name=data["name"], code=data["code"])
        for data in language_data
    ]


@pytest.fixture
def box_data(user, languages):
    """Returns default box data."""
    return {
        "name": "Test Box",
        "description": "A test box",
        "user": user,
        "source_language": languages[0],
        "target_language": languages[1],
    }


@pytest.fixture
def box(box_data):
    """Creates and returns a box."""
    return Box.objects.create(**box_data)


@pytest.fixture
def other_box_data(other_user, languages):
    """Returns data for another box."""
    return {
        "name": "Other Box",
        "description": "Another test box",
        "user": other_user,
        "source_language": languages[0],
        "target_language": languages[1],
    }


@pytest.fixture
def other_box(other_box_data):
    """Creates and returns another box."""
    return Box.objects.create(**other_box_data)


@pytest.fixture
def card_data(box):
    """Returns default card data."""
    return {
        "source_text": "Hello",
        "target_text": "Hola",
        "box": box,
    }


@pytest.fixture
def card(card_data):
    """Creates and returns a card."""
    return Card.objects.create(**card_data)


@pytest.fixture
def mock_request():
    """Returns a mock request object that can be used for serializer context."""
    factory = APIRequestFactory()
    request = factory.get("/")
    return request


# Fixtures for leitner app tests
# Using fixtures from root-level conftest.py
