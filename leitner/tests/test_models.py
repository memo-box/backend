import pytest
from django.utils import timezone
from datetime import timedelta
from leitner.models import CustomUser, Language, Box, Card
from leitner.constants import RECALL_INTERVALS


@pytest.mark.django_db
class TestCustomUserManager:
    """Tests for the CustomUserManager."""

    def test_create_user(self, user_data):
        """Test creating a regular user."""
        user = CustomUser.objects.create_user(
            email=user_data["email"],
            password=user_data["password"],
            name=user_data["name"],
        )
        assert user.email == user_data["email"]
        assert user.name == user_data["name"]
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password(user_data["password"])

    def test_create_user_without_email(self):
        """Test creating a user without an email raises an error."""
        with pytest.raises(ValueError, match="The Email field must be set"):
            CustomUser.objects.create_user(email="", password="testpass123")

    def test_create_superuser(self, user_data):
        """Test creating a superuser."""
        admin_user = CustomUser.objects.create_superuser(
            email=user_data["email"], password=user_data["password"]
        )
        assert admin_user.email == user_data["email"]
        assert admin_user.is_staff is True
        assert admin_user.is_superuser is True
        assert admin_user.name == "Admin"  # Default name for superuser

    def test_create_superuser_not_staff(self, user_data):
        """Test creating a superuser with is_staff=False raises an error."""
        with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
            CustomUser.objects.create_superuser(
                email=user_data["email"], password=user_data["password"], is_staff=False
            )

    def test_create_superuser_not_superuser(self, user_data):
        """Test creating a superuser with is_superuser=False raises an error."""
        with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
            CustomUser.objects.create_superuser(
                email=user_data["email"],
                password=user_data["password"],
                is_superuser=False,
            )


@pytest.mark.django_db
class TestCustomUser:
    """Tests for the CustomUser model."""

    def test_str_method(self, user):
        """Test the string representation of a user."""
        assert str(user) == user.email

    def test_created_at_auto_now_add(self, user):
        """Test that created_at is set automatically."""
        assert user.created_at is not None

    def test_updated_at_auto_now(self, user):
        """Test that updated_at is updated automatically."""
        original_updated_at = user.updated_at
        user.name = "Updated Name"
        user.save()
        assert user.updated_at > original_updated_at


@pytest.mark.django_db
class TestLanguage:
    """Tests for the Language model."""

    def test_create_language(self, language_data):
        """Test creating a language."""
        language = Language.objects.create(
            name=language_data[0]["name"], code=language_data[0]["code"]
        )
        assert language.name == language_data[0]["name"]
        assert language.code == language_data[0]["code"]

    def test_str_method(self, languages):
        """Test the string representation of a language."""
        assert str(languages[0]) == languages[0].code


@pytest.mark.django_db
class TestBox:
    """Tests for the Box model."""

    def test_create_box(self, box_data):
        """Test creating a box."""
        box = Box.objects.create(**box_data)
        assert box.name == box_data["name"]
        assert box.description == box_data["description"]
        assert box.user == box_data["user"]
        assert box.source_language == box_data["source_language"]
        assert box.target_language == box_data["target_language"]

    def test_str_method(self, box):
        """Test the string representation of a box."""
        assert str(box) == box.name

    def test_user_box_relationship(self, user, box):
        """Test the relationship between user and box."""
        user_boxes = Box.objects.filter(user=user)
        assert box in user_boxes


@pytest.mark.django_db
class TestCard:
    """Tests for the Card model."""

    def test_create_card(self, card_data):
        """Test creating a card."""
        card = Card.objects.create(**card_data)
        assert card.source_text == card_data["source_text"]
        assert card.target_text == card_data["target_text"]
        assert card.box == card_data["box"]
        assert card.recall_count == 0
        assert card.last_recall is None
        assert card.next_recall is not None

    def test_str_method(self, card):
        """Test the string representation of a card."""
        assert str(card) == card.source_text

    def test_record_recall_remembered(self, card):
        """Test recording a successful recall."""
        now = timezone.now()
        next_recall = card.record_recall(remembered=True)

        # Check that recall count increased
        assert card.recall_count == 1
        # Check that last_recall was updated
        assert card.last_recall is not None
        assert card.last_recall >= now
        # Check that next_recall was updated to a future date
        assert card.next_recall > now
        # Check that next_recall is calculated correctly
        expected_next_recall = card.last_recall + timedelta(days=RECALL_INTERVALS[1])
        assert abs((card.next_recall - expected_next_recall).total_seconds()) < 1
        # Check that the method returns the next recall date
        assert next_recall == card.next_recall

    def test_record_recall_not_remembered(self, card):
        """Test recording an unsuccessful recall."""
        # First, increase the recall count
        card.recall_count = 5
        card.save()

        now = timezone.now()
        next_recall = card.record_recall(remembered=False)

        # Check that recall count was reset to 0
        assert card.recall_count == 0
        # Check that last_recall was updated
        assert card.last_recall is not None
        assert card.last_recall >= now
        # Check that next_recall was updated to a future date
        assert card.next_recall > now
        # Check that next_recall is calculated correctly (reset to first interval)
        expected_next_recall = card.last_recall + timedelta(days=RECALL_INTERVALS[0])
        assert abs((card.next_recall - expected_next_recall).total_seconds()) < 1
        # Check that the method returns the next recall date
        assert next_recall == card.next_recall

    def test_record_recall_at_max_interval(self, card):
        """Test recording a successful recall when already at max interval."""
        # Set to the maximum interval
        card.recall_count = len(RECALL_INTERVALS) - 1
        card.save()

        next_recall = card.record_recall(remembered=True)

        # Check that recall count stays at max
        assert card.recall_count == len(RECALL_INTERVALS) - 1
        # Check that the method returns the next recall date
        assert next_recall == card.next_recall
