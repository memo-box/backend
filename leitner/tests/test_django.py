from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from leitner.models import CustomUser, Language, Box, Card
from datetime import timedelta
from django.utils import timezone
import uuid


class UserManagerTestCase(TestCase):
    """Tests for the CustomUserManager."""

    def setUp(self):
        # Generate a unique email prefix for this test class
        self.email_prefix = str(uuid.uuid4())
        self.user_data = {
            "email": f"{self.email_prefix}@example.com",
            "name": "Test User",
            "password": "testpass123",
        }

    def test_create_user(self):
        """Test creating a regular user."""
        user = CustomUser.objects.create_user(
            email=self.user_data["email"],
            password=self.user_data["password"],
            name=self.user_data["name"],
        )
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.name, self.user_data["name"])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(self.user_data["password"]))

    def test_create_user_without_email(self):
        """Test creating a user without an email raises an error."""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email="", password="testpass123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        unique_email = f"admin-{uuid.uuid4()}@example.com"
        admin_user = CustomUser.objects.create_superuser(
            email=unique_email, password=self.user_data["password"]
        )
        self.assertEqual(admin_user.email, unique_email)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.name, "Admin")  # Default name for superuser


class UserModelTestCase(TestCase):
    """Tests for the CustomUser model."""

    def setUp(self):
        unique_email = f"user-{uuid.uuid4()}@example.com"
        self.user = CustomUser.objects.create_user(
            email=unique_email, name="Test User", password="testpass123"
        )

    def test_str_method(self):
        """Test the string representation of a user."""
        self.assertEqual(str(self.user), self.user.email)

    def test_created_at_auto_now_add(self):
        """Test that created_at is set automatically."""
        self.assertIsNotNone(self.user.created_at)

    def test_updated_at_auto_now(self):
        """Test that updated_at is updated automatically."""
        original_updated_at = self.user.updated_at
        self.user.name = "Updated Name"
        self.user.save()
        self.assertGreater(self.user.updated_at, original_updated_at)


class LanguageModelTestCase(TestCase):
    """Tests for the Language model."""

    def setUp(self):
        self.language_data = {"name": "English", "code": "en"}
        self.language = Language.objects.create(**self.language_data)

    def test_create_language(self):
        """Test creating a language."""
        self.assertEqual(self.language.name, self.language_data["name"])
        self.assertEqual(self.language.code, self.language_data["code"])

    def test_str_method(self):
        """Test the string representation of a language."""
        self.assertEqual(str(self.language), self.language.name)


class BoxModelTestCase(TestCase):
    """Tests for the Box model."""

    def setUp(self):
        unique_email = f"box-user-{uuid.uuid4()}@example.com"
        self.user = CustomUser.objects.create_user(
            email=unique_email, name="Test User", password="testpass123"
        )
        self.source_language = Language.objects.create(name="English", code="en")
        self.target_language = Language.objects.create(name="Spanish", code="es")
        self.box_data = {
            "name": "Test Box",
            "description": "A test box",
            "user": self.user,
            "source_language": self.source_language,
            "target_language": self.target_language,
        }
        self.box = Box.objects.create(**self.box_data)

    def test_create_box(self):
        """Test creating a box."""
        self.assertEqual(self.box.name, self.box_data["name"])
        self.assertEqual(self.box.description, self.box_data["description"])
        self.assertEqual(self.box.user, self.box_data["user"])
        self.assertEqual(self.box.source_language, self.box_data["source_language"])
        self.assertEqual(self.box.target_language, self.box_data["target_language"])

    def test_str_method(self):
        """Test the string representation of a box."""
        self.assertEqual(str(self.box), self.box.name)

    def test_user_box_relationship(self):
        """Test the relationship between user and box."""
        user_boxes = Box.objects.filter(user=self.user)
        self.assertIn(self.box, user_boxes)


class CardModelTestCase(TestCase):
    """Tests for the Card model."""

    def setUp(self):
        unique_email = f"card-user-{uuid.uuid4()}@example.com"
        self.user = CustomUser.objects.create_user(
            email=unique_email, name="Test User", password="testpass123"
        )
        self.source_language = Language.objects.create(name="English", code="en")
        self.target_language = Language.objects.create(name="Spanish", code="es")
        self.box = Box.objects.create(
            name="Test Box",
            description="A test box",
            user=self.user,
            source_language=self.source_language,
            target_language=self.target_language,
        )
        self.card_data = {
            "source_text": "Hello",
            "target_text": "Hola",
            "box": self.box,
        }
        self.card = Card.objects.create(**self.card_data)

    def test_create_card(self):
        """Test creating a card."""
        self.assertEqual(self.card.source_text, self.card_data["source_text"])
        self.assertEqual(self.card.target_text, self.card_data["target_text"])
        self.assertEqual(self.card.box, self.card_data["box"])
        self.assertEqual(self.card.recall_count, 0)
        self.assertIsNone(self.card.last_recall)
        self.assertIsNotNone(self.card.next_recall)

    def test_str_method(self):
        """Test the string representation of a card."""
        self.assertEqual(str(self.card), self.card.source_text)

    def test_record_recall_remembered(self):
        """Test recording a successful recall."""
        now = timezone.now()
        next_recall = self.card.record_recall(remembered=True)

        # Check that recall count increased
        self.assertEqual(self.card.recall_count, 1)
        # Check that last_recall was updated
        self.assertIsNotNone(self.card.last_recall)
        self.assertGreaterEqual(self.card.last_recall, now)
        # Check that next_recall was updated to a future date
        self.assertGreater(self.card.next_recall, now)
        # Check that next_recall is calculated correctly
        expected_next_recall = self.card.last_recall + timedelta(
            days=Card.RECALL_INTERVALS[1]
        )
        self.assertLess(
            abs((self.card.next_recall - expected_next_recall).total_seconds()), 1
        )
        # Check that the method returns the next recall date
        self.assertEqual(next_recall, self.card.next_recall)

    def test_record_recall_not_remembered(self):
        """Test recording an unsuccessful recall."""
        # First, increase the recall count
        self.card.recall_count = 5
        self.card.save()

        now = timezone.now()
        next_recall = self.card.record_recall(remembered=False)

        # Check that recall count was reset to 0
        self.assertEqual(self.card.recall_count, 0)
        # Check that last_recall was updated
        self.assertIsNotNone(self.card.last_recall)
        self.assertGreaterEqual(self.card.last_recall, now)
        # Check that next_recall was updated to a future date
        self.assertGreater(self.card.next_recall, now)
        # Check that next_recall is calculated correctly (reset to first interval)
        expected_next_recall = self.card.last_recall + timedelta(
            days=Card.RECALL_INTERVALS[0]
        )
        self.assertLess(
            abs((self.card.next_recall - expected_next_recall).total_seconds()), 1
        )
        # Check that the method returns the next recall date
        self.assertEqual(next_recall, self.card.next_recall)


class UserViewSetTestCase(TestCase):
    """Tests for the UserViewSet."""

    def setUp(self):
        self.client = APIClient()
        unique_email = f"view-user-{uuid.uuid4()}@example.com"
        self.user = CustomUser.objects.create_user(
            email=unique_email, name="Test User", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_users(self):
        """Test listing users."""
        url = reverse("customuser-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], self.user.email)
        self.assertEqual(response.data[0]["name"], self.user.name)

    def test_retrieve_user(self):
        """Test retrieving a specific user."""
        url = reverse("customuser-detail", kwargs={"pk": self.user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["name"], self.user.name)

    def test_create_user(self):
        """Test creating a new user."""
        url = reverse("customuser-list")
        data = {
            "email": f"newuser-{uuid.uuid4()}@example.com",
            "name": "New User",
            "password": "newpass123",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], data["email"])
        self.assertEqual(response.data["name"], data["name"])

        # Confirm user is in database
        self.assertTrue(CustomUser.objects.filter(email=data["email"]).exists())


class LanguageViewSetTestCase(TestCase):
    """Tests for the LanguageViewSet."""

    def setUp(self):
        self.client = APIClient()
        unique_email = f"lang-user-{uuid.uuid4()}@example.com"
        self.user = CustomUser.objects.create_user(
            email=unique_email, name="Test User", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.language = Language.objects.create(name="English", code="en")

    def test_list_languages(self):
        """Test listing languages."""
        url = reverse("language-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        language_names = [lang["name"] for lang in response.data]
        self.assertIn(self.language.name, language_names)

    def test_retrieve_language(self):
        """Test retrieving a specific language."""
        url = reverse("language-detail", kwargs={"pk": self.language.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.language.name)
        self.assertEqual(response.data["code"], self.language.code)
