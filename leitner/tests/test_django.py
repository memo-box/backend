import uuid
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from leitner.models import CustomUser, Language, Box, Card


class UserManagerTestCase(TestCase):
    """Tests for the CustomUserManager."""

    @classmethod
    def setUpTestData(cls):
        # Generate a unique email prefix for this test class
        cls.email_prefix = str(uuid.uuid4())
        cls.user_data = {
            "email": f"{cls.email_prefix}@example.com",
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
        admin_user = CustomUser.objects.create_superuser(
            email=self.user_data["email"], password=self.user_data["password"]
        )
        self.assertEqual(admin_user.email, self.user_data["email"])
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.name, "Admin")  # Default name for superuser

    def test_create_superuser_not_staff(self):
        """Test creating a superuser with is_staff=False raises an error."""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email=self.user_data["email"],
                password=self.user_data["password"],
                is_staff=False,
            )

    def test_create_superuser_not_superuser(self):
        """Test creating a superuser with is_superuser=False raises an error."""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email=self.user_data["email"],
                password=self.user_data["password"],
                is_superuser=False,
            )


class UserModelTestCase(TestCase):
    """Tests for the CustomUser model."""

    @classmethod
    def setUpTestData(cls):
        unique_email = f"user-{uuid.uuid4()}@example.com"
        cls.user = CustomUser.objects.create_user(
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

    @classmethod
    def setUpTestData(cls):
        cls.language_data = {"name": "English", "code": "en"}
        cls.language = Language.objects.create(**cls.language_data)

    def test_str_method(self):
        """Test the string representation of a language."""
        self.assertEqual(str(self.language), self.language.name)


class BoxModelTestCase(TestCase):
    """Tests for the Box model."""

    @classmethod
    def setUpTestData(cls):
        unique_email = f"box-user-{uuid.uuid4()}@example.com"
        cls.user = CustomUser.objects.create_user(
            email=unique_email, name="Test User", password="testpass123"
        )
        cls.source_language = Language.objects.create(name="English", code="en")
        cls.target_language = Language.objects.create(name="Spanish", code="es")
        cls.box_data = {
            "name": "Test Box",
            "description": "A test box",
            "user": cls.user,
            "source_language": cls.source_language,
            "target_language": cls.target_language,
        }
        cls.box = Box.objects.create(**cls.box_data)

    def test_str_method(self):
        """Test the string representation of a box."""
        self.assertEqual(str(self.box), self.box.name)

    def test_user_box_relationship(self):
        """Test the relationship between user and box."""
        user_boxes = Box.objects.filter(user=self.user)
        self.assertIn(self.box, user_boxes)


class CardModelTestCase(TestCase):
    """Tests for the Card model."""

    @classmethod
    def setUpTestData(cls):
        unique_email = f"card-user-{uuid.uuid4()}@example.com"
        cls.user = CustomUser.objects.create_user(
            email=unique_email, name="Test User", password="testpass123"
        )
        cls.source_language = Language.objects.create(name="English", code="en")
        cls.target_language = Language.objects.create(name="Spanish", code="es")
        cls.box = Box.objects.create(
            name="Test Box",
            description="A test box",
            user=cls.user,
            source_language=cls.source_language,
            target_language=cls.target_language,
        )
        cls.card_data = {
            "source_text": "Hello",
            "target_text": "Hola",
            "box": cls.box,
        }
        cls.card = Card.objects.create(**cls.card_data)

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

    def test_record_recall_at_max_interval(self):
        """Test recording a successful recall when already at max interval."""
        # Set to the maximum interval
        self.card.recall_count = len(Card.RECALL_INTERVALS) - 1
        self.card.save()

        next_recall = self.card.record_recall(remembered=True)

        # Check that recall count stays at max
        self.assertEqual(self.card.recall_count, len(Card.RECALL_INTERVALS) - 1)
        # Check that the method returns the next recall date
        self.assertEqual(next_recall, self.card.next_recall)


class UserViewSetTestCase(TestCase):
    """Tests for the UserViewSet."""

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        unique_email = f"view-user-{uuid.uuid4()}@example.com"
        cls.user = CustomUser.objects.create_user(
            email=unique_email, name="Test User", password="testpass123"
        )
        cls.client.force_authenticate(user=cls.user)

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

    def test_update_user(self):
        """Test updating a user."""
        url = reverse("customuser-detail", kwargs={"pk": self.user.pk})
        data = {"name": "Updated Name"}
        response = self.client.patch(url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], data["name"])

        # Confirm user is updated in database
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, data["name"])

    def test_delete_user(self):
        """Test deleting a user."""
        url = reverse("customuser-detail", kwargs={"pk": self.user.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Confirm user is deleted from database
        self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())


class LanguageViewSetTestCase(TestCase):
    """Tests for the LanguageViewSet."""

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        unique_email = f"lang-user-{uuid.uuid4()}@example.com"
        cls.user = CustomUser.objects.create_user(
            email=unique_email, name="Test User", password="testpass123"
        )
        cls.client.force_authenticate(user=cls.user)
        cls.language = Language.objects.create(name="English", code="en")

    def test_list_languages(self):
        """Test listing languages."""
        url = reverse("language-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.language.name)
        self.assertEqual(response.data[0]["code"], self.language.code)

    def test_retrieve_language(self):
        """Test retrieving a specific language."""
        url = reverse("language-detail", kwargs={"pk": self.language.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.language.name)
        self.assertEqual(response.data["code"], self.language.code)

    def test_update_language(self):
        """Test updating a language."""
        url = reverse("language-detail", kwargs={"pk": self.language.pk})
        data = {"name": "Updated Language"}
        response = self.client.patch(url, data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], data["name"])

        # Confirm language is updated in database
        self.language.refresh_from_db()
        self.assertEqual(self.language.name, data["name"])

    def test_delete_language(self):
        """Test deleting a language."""
        url = reverse("language-detail", kwargs={"pk": self.language.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Confirm language is deleted from database
        self.assertFalse(Language.objects.filter(pk=self.language.pk).exists())
