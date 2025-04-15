import pytest
from datetime import timedelta
from django.utils import timezone
from leitner.serializers import (
    UserSerializer,
    LanguageSerializer,
    BoxSerializer,
    CardSerializer,
    CardRecallSerializer,
)
from leitner.constants import RECALL_INTERVALS
from rest_framework import serializers
from ..models import Language, Box, Card


@pytest.mark.django_db
class TestUserSerializer:
    """Tests for the UserSerializer."""

    def test_serialization(self, user, mock_request):
        """Test serializing a user."""
        serializer = UserSerializer(user, context={"request": mock_request})
        data = serializer.data

        assert data["email"] == user.email
        assert data["name"] == user.name
        assert "is_staff" in data
        assert "url" in data
        assert "created_at" in data
        assert "updated_at" in data
        # Password should not be included
        assert "password" not in data

    def test_deserialization(self, user_data):
        """Test deserializing user data."""
        serializer = UserSerializer(
            data={
                "email": user_data["email"],
                "name": user_data["name"],
                "password": user_data["password"],
            }
        )

        assert serializer.is_valid()
        user = serializer.save()

        assert user.email == user_data["email"]
        assert user.name == user_data["name"]


@pytest.mark.django_db
class TestLanguageSerializer:
    """Tests for the LanguageSerializer."""

    def test_serialization(self, languages, mock_request):
        """Test serializing a language."""
        serializer = LanguageSerializer(languages[0], context={"request": mock_request})
        data = serializer.data

        assert data["name"] == languages[0].name
        assert data["code"] == languages[0].code
        assert "created_at" in data
        assert "updated_at" in data

    def test_deserialization(self):
        """Test deserializing language data (name only, code is read-only)."""
        # Serializer treats code as read-only, so only needs name.
        # Use a unique name not present in migration data
        unique_name = "Klingon"
        serializer = LanguageSerializer(
            data={
                "name": unique_name,
                # Code is read-only and generated or handled elsewhere
            }
        )
        # Serializer itself should be valid
        assert serializer.is_valid(), serializer.errors
        # Check the validated data
        assert serializer.validated_data["name"] == unique_name


@pytest.mark.django_db
class TestBoxSerializer:
    """Tests for the BoxSerializer."""

    def test_serialization(self, box, mock_request):
        """Test serializing a box."""
        serializer = BoxSerializer(box, context={"request": mock_request})
        data = serializer.data

        assert data["name"] == box.name
        assert data["description"] == box.description
        assert "url" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Test nested language serialization
        assert data["source_language"]["name"] == box.source_language.name
        assert data["source_language"]["code"] == box.source_language.code
        assert data["target_language"]["name"] == box.target_language.name
        assert data["target_language"]["code"] == box.target_language.code

        # IDs should not be included since they are write-only
        assert "source_language_id" not in data
        assert "target_language_id" not in data

    def test_deserialization(self, user, languages):
        """Test deserializing box data."""
        box_data = {
            "name": "New Test Box",
            "description": "A new test box",
            "source_language_id": languages[0].id,
            "target_language_id": languages[1].id,
        }

        serializer = BoxSerializer(
            data=box_data, context={"request": type("obj", (object,), {"user": user})}
        )

        assert serializer.is_valid()
        box = serializer.save(user=user)

        assert box.name == box_data["name"]
        assert box.description == box_data["description"]
        assert box.source_language == languages[0]
        assert box.target_language == languages[1]
        assert box.user == user


@pytest.mark.django_db
class TestCardSerializer:
    """Tests for the CardSerializer."""

    def test_serialization(self, card, mock_request):
        """Test serializing a card."""
        serializer = CardSerializer(card, context={"request": mock_request})
        data = serializer.data

        assert data["source_text"] == card.source_text
        assert data["target_text"] == card.target_text
        assert data["recall_count"] == card.recall_count
        assert "last_recall" in data
        assert "next_recall" in data
        assert "url" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Test nested box serialization
        assert data["box"]["name"] == card.box.name
        assert data["box"]["description"] == card.box.description

        # ID should not be included since it is write-only
        assert "box_id" not in data

    def test_deserialization(self, box):
        """Test deserializing card data."""
        card_data = {
            "source_text": "New Test Card",
            "target_text": "Nueva Tarjeta de Prueba",
            "box_id": box.id,
        }

        serializer = CardSerializer(data=card_data)

        assert serializer.is_valid()
        card = serializer.save()

        assert card.source_text == card_data["source_text"]
        assert card.target_text == card_data["target_text"]
        assert card.box == box
        assert card.recall_count == 0
        assert card.last_recall is None
        assert card.next_recall is not None


@pytest.mark.django_db
class TestCardRecallSerializer:
    """Tests for the CardRecallSerializer."""

    def test_serialization(self, card, mock_request):
        """Test serializing a card for recall."""
        # First, record a recall to set the relevant fields
        card.record_recall(remembered=True)

        serializer = CardRecallSerializer(card, context={"request": mock_request})
        data = serializer.data

        assert data["id"] == card.id
        assert data["recall_count"] == card.recall_count
        assert "last_recall" in data
        assert "next_recall" in data

        # Remembered should not be included since it is write-only
        assert "remembered" not in data

    def test_update_remembered_true(self, card):
        """Test updating a card with remembered=True."""
        initial_recall_count = card.recall_count
        now = timezone.now()

        serializer = CardRecallSerializer(card, data={"remembered": True})
        assert serializer.is_valid()
        updated_card = serializer.save()

        assert updated_card.recall_count == initial_recall_count + 1
        assert updated_card.last_recall is not None
        assert updated_card.last_recall.replace(microsecond=0) >= now.replace(
            microsecond=0
        )

        # Check calculation based on current state
        expected_next_recall = updated_card.last_recall + timedelta(
            days=RECALL_INTERVALS[updated_card.recall_count]
        )
        assert (
            abs((updated_card.next_recall - expected_next_recall).total_seconds()) < 1
        )

    def test_update_remembered_false(self, card):
        """Test updating a card with remembered=False."""
        card.recall_count = 5
        card.save()
        now = timezone.now()

        serializer = CardRecallSerializer(card, data={"remembered": False})
        assert serializer.is_valid()
        updated_card = serializer.save()

        assert updated_card.recall_count == 0
        assert updated_card.last_recall is not None
        assert updated_card.last_recall.replace(microsecond=0) >= now.replace(
            microsecond=0
        )

        # Check calculation based on current state
        expected_next_recall = updated_card.last_recall + timedelta(
            days=RECALL_INTERVALS[0]
        )
        assert (
            abs((updated_card.next_recall - expected_next_recall).total_seconds()) < 1
        )
