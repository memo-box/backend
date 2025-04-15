import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from leitner.models import CustomUser, Language, Box, Card
from rest_framework.test import APIRequestFactory
from django.utils import timezone
import uuid


@pytest.fixture
def api_client():
    """Returns an authenticated API client."""
    return APIClient()


@pytest.fixture
def user_data():
    """Returns default user data."""
    return {"email": "test@example.com", "name": "Test User", "password": "testpass123"}


@pytest.fixture
@pytest.mark.django_db
def test_user():
    """Creates and returns a user with a unique email."""
    User = get_user_model()
    unique_email = f"testuser_{uuid.uuid4()}@example.com"
    user = User.objects.create_user(
        email=unique_email, password="testpass123", name="Test User"
    )
    return user


@pytest.fixture
def other_user_data():
    """Returns data for another user."""
    return {
        "email": "otheruser@example.com",
        "name": "Other User",
        "password": "testpass123",
    }


@pytest.fixture
@pytest.mark.django_db
def other_user():
    """Creates and returns another user with a unique email."""
    User = get_user_model()
    unique_email = f"otheruser_{uuid.uuid4()}@example.com"
    user = User.objects.create_user(
        email=unique_email, password="testpass123", name="Other User"
    )
    return user


@pytest.fixture
@pytest.mark.django_db
def authenticated_client(api_client, test_user):
    """Returns an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def language_data():
    """Returns default language data."""
    return [{"name": "English", "code": "en"}, {"name": "Spanish", "code": "es"}]


@pytest.fixture
@pytest.mark.django_db
def languages(language_data):
    """Creates or updates and returns languages."""
    created_languages = []
    for data in language_data:
        # Use update_or_create to ensure the language exists with the correct code.
        # It matches based on the unique field 'name'.
        language, created = Language.objects.update_or_create(
            name=data["name"],  # Assuming 'name' is unique
            defaults={'code': data["code"]}
        )
        created_languages.append(language)
    return created_languages


@pytest.fixture
def box_data(test_user, languages):
    """Returns default box data."""
    return {
        "name": "Test Box",
        "description": "A test box",
        "user": test_user,
        "source_language": languages[0],
        "target_language": languages[1],
    }


@pytest.fixture
@pytest.mark.django_db
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
@pytest.mark.django_db
def card(box):
    """Fixture for creating a test card."""
    return Card.objects.create(
        source_text="Hello",
        target_text="Hola",
        box=box,
        # Set next_recall slightly in the future to avoid being due immediately
        next_recall=timezone.now() + timezone.timedelta(seconds=10),
    )


@pytest.fixture
@pytest.mark.django_db
def due_card(box):
    """Fixture for creating a card that is due for recall."""
    # Set next_recall to a past date to ensure it's due
    past_date = timezone.now() - timezone.timedelta(days=1)
    return Card.objects.create(
        source_text="Goodbye",
        target_text="Adiós",
        box=box,
        next_recall=past_date,
    )


@pytest.fixture
@pytest.mark.django_db
def not_due_card(box):
    """Fixture for creating a card that is not due for recall."""
    # Set next_recall to a future date
    future_date = timezone.now() + timezone.timedelta(days=10)
    return Card.objects.create(
        source_text="Thank you",
        target_text="Gracias",
        box=box,
        next_recall=future_date,
    )


@pytest.fixture
def mock_request():
    """Returns a mock request object that can be used for serializer context."""
    factory = APIRequestFactory()
    request = factory.get("/")
    return request


# Fixtures for leitner app tests
# Using fixtures from root-level conftest.py
