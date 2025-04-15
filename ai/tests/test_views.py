import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from leitner.models import CustomUser
from django.contrib.auth import get_user_model
from unittest.mock import patch
from ai.schemas import BackcardResponse, TopicGenerationResponse, TopicCard

User = get_user_model()


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
def authenticated_client(user):
    """Returns an authenticated API client."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email="test@example.com", password="password123", name="Test User"
    )


@pytest.mark.django_db
class TestGenerateBackcardView:
    """Tests for the GenerateBackcardView."""

    @patch("ai.views.generate_back_card_usecase.generate")
    def test_generate_backcard_success(self, mock_generate, authenticated_client):
        """Test successful backcard generation."""
        # Configure mock response
        mock_response = BackcardResponse(
            translation="Hallo",
            definition="A common greeting.",
            example_sentences="Hello world!",
            example_sentences_translated="Hallo Welt!",
            pronunciation="/həˈloʊ/",
        )
        mock_generate.return_value = mock_response

        url = reverse("ai:generate-backcard")
        data = {
            "word_or_phrase": "Hello",
            "source_language": "EN",
            "target_language": "DE",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == mock_response.model_dump(exclude_none=True)
        mock_generate.assert_called_once_with(
            front_card="Hello", source_language="EN", target_language="DE"
        )

    @patch("ai.views.generate_back_card_usecase.generate")
    def test_generate_backcard_invalid_language(
        self, mock_generate, authenticated_client
    ):
        """Test backcard generation with invalid language code."""
        url = reverse("ai:generate-backcard")
        data = {
            "word_or_phrase": "Hello",
            "source_language": "XX",
            "target_language": "DE",
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        mock_generate.assert_not_called()


@pytest.mark.django_db
class TestGenerateTopicCardsView:
    """Tests for the GenerateTopicCardsView."""

    @patch("ai.views.generate_topic_usecase.generate")
    def test_generate_topic_cards_success(self, mock_generate, authenticated_client):
        """Test successful topic card generation with valid count."""
        # Configure mock response
        mock_cards = [
            TopicCard(front="Apple", back="Apfel"),
            TopicCard(front="Banana", back="Banane"),
        ]
        mock_response = TopicGenerationResponse(cards=mock_cards)
        mock_generate.return_value = mock_response

        url = reverse("ai:generate-topic-cards")
        data = {
            "topic": "Food",
            "source_language": "EN",
            "target_language": "DE",
            "count": 2,
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "cards" in response.data
        # Check the structure and number of cards returned matches the mock
        assert len(response.data["cards"]) == 2
        assert response.data["cards"][0]["front"] == "Apple"
        assert response.data["cards"][1]["front"] == "Banana"

        mock_generate.assert_called_once_with(
            topic="Food", source_language="EN", target_language="DE", count=2
        )

    @patch("ai.views.generate_topic_usecase.generate")
    def test_generate_topic_cards_invalid_language(
        self, mock_generate, authenticated_client
    ):
        """Test topic card generation with invalid language code."""
        url = reverse("ai:generate-topic-cards")
        data = {"topic": "Food", "source_language": "XX", "target_language": "DE"}
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        mock_generate.assert_not_called()

    @patch("ai.views.generate_topic_usecase.generate")
    def test_generate_topic_cards_invalid_type_count(
        self, mock_generate, authenticated_client
    ):
        """Test topic card generation with non-integer count (expects 400)."""
        url = reverse("ai:generate-topic-cards")
        data = {
            "topic": "Food",
            "source_language": "EN",
            "target_language": "DE",
            "count": "invalid",
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        # Check for the specific field error if possible (depends on exact view response)
        assert "details" in response.data
        assert "count" in response.data["details"]
        mock_generate.assert_not_called()

    @patch("ai.views.generate_topic_usecase.generate")
    def test_generate_topic_cards_missing_count(
        self, mock_generate, authenticated_client
    ):
        """Test topic card generation with missing count (should default)."""
        mock_cards_default = [TopicCard(front=f"Card {i}") for i in range(50)]
        mock_response_default = TopicGenerationResponse(cards=mock_cards_default)
        mock_generate.return_value = mock_response_default

        url = reverse("ai:generate-topic-cards")
        data = {
            "topic": "Food",
            "source_language": "EN",
            "target_language": "DE",
            # count is missing
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "cards" in response.data
        assert len(response.data["cards"]) == 50
        mock_generate.assert_called_once_with(
            topic="Food", source_language="EN", target_language="DE", count=50
        )

    @patch("ai.views.generate_topic_usecase.generate")
    def test_generate_topic_cards_out_of_range_count(
        self, mock_generate, authenticated_client
    ):
        """Test topic card generation with out-of-range integer count (should default)."""
        mock_cards_default = [TopicCard(front=f"Card {i}") for i in range(50)]
        mock_response_default = TopicGenerationResponse(cards=mock_cards_default)
        mock_generate.return_value = mock_response_default

        url = reverse("ai:generate-topic-cards")
        data = {
            "topic": "Food",
            "source_language": "EN",
            "target_language": "DE",
            "count": 250,  # Out of range (1-50)
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
