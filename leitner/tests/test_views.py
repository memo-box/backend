import pytest
from django.urls import reverse
from rest_framework import status
from leitner.models import CustomUser, Language, Box, Card


@pytest.mark.django_db
class TestUserViewSet:
    """Tests for the UserViewSet."""

    def test_list_users(self, authenticated_client, user):
        """Test listing users."""
        url = reverse("customuser-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["email"] == user.email
        assert response.data[0]["name"] == user.name

    def test_retrieve_user(self, authenticated_client, user):
        """Test retrieving a specific user."""
        url = reverse("customuser-detail", kwargs={"pk": user.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert response.data["name"] == user.name

    def test_create_user(self, authenticated_client, user_data):
        """Test creating a new user."""
        url = reverse("customuser-list")
        data = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "newpass123",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == data["email"]
        assert response.data["name"] == data["name"]

        # Confirm user is in database
        assert CustomUser.objects.filter(email=data["email"]).exists()

    def test_update_user(self, authenticated_client, user):
        """Test updating a user."""
        url = reverse("customuser-detail", kwargs={"pk": user.pk})
        data = {"name": "Updated Name"}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]

        # Confirm user is updated in database
        user.refresh_from_db()
        assert user.name == data["name"]

    def test_delete_user(self, authenticated_client, user):
        """Test deleting a user."""
        # Create a second user to delete
        second_user = CustomUser.objects.create_user(
            email="seconduser@example.com", name="Second User", password="testpass123"
        )

        url = reverse("customuser-detail", kwargs={"pk": second_user.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Confirm user is deleted from database
        assert not CustomUser.objects.filter(pk=second_user.pk).exists()


@pytest.mark.django_db
class TestLanguageViewSet:
    """Tests for the LanguageViewSet."""

    def test_list_languages(self, authenticated_client, languages):
        """Test listing languages."""
        url = reverse("language-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= len(languages)

        # Verify all languages are in the response
        language_names = [lang["name"] for lang in response.data]
        for language in languages:
            assert language.name in language_names

    def test_retrieve_language(self, authenticated_client, languages):
        """Test retrieving a specific language."""
        url = reverse("language-detail", kwargs={"pk": languages[0].pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == languages[0].name
        assert response.data["code"] == languages[0].code

    def test_create_language(self, authenticated_client):
        """Test creating a new language."""
        url = reverse("language-list")
        data = {
            "name": "French",
            "code": "fr",
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == data["name"]
        assert response.data["code"] == data["code"]

        # Confirm language is in database
        assert Language.objects.filter(name=data["name"]).exists()

    def test_update_language(self, authenticated_client, languages):
        """Test updating a language."""
        url = reverse("language-detail", kwargs={"pk": languages[0].pk})
        data = {"name": "Updated Language"}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]

        # Confirm language is updated in database
        languages[0].refresh_from_db()
        assert languages[0].name == data["name"]

    def test_delete_language(self, authenticated_client, languages):
        """Test deleting a language."""
        url = reverse("language-detail", kwargs={"pk": languages[0].pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Confirm language is deleted from database
        assert not Language.objects.filter(pk=languages[0].pk).exists()


@pytest.mark.django_db
class TestBoxViewSet:
    """Tests for the BoxViewSet."""

    def test_list_boxes(self, authenticated_client, user, box):
        """Test listing boxes."""
        url = reverse("box-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["name"] == box.name
        assert response.data[0]["description"] == box.description

    def test_list_boxes_filtered_by_user(self, authenticated_client, user, box):
        """Test that boxes are filtered by the authenticated user."""
        # Create another user with a box
        other_user = CustomUser.objects.create_user(
            email="otheruser@example.com", name="Other User", password="testpass123"
        )

        other_box = Box.objects.create(
            name="Other Box",
            description="Another test box",
            user=other_user,
            source_language=box.source_language,
            target_language=box.target_language,
        )

        url = reverse("box-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Only the authenticated user's box should be returned
        box_names = [b["name"] for b in response.data]
        assert box.name in box_names
        assert other_box.name not in box_names

    def test_retrieve_box(self, authenticated_client, box):
        """Test retrieving a specific box."""
        url = reverse("box-detail", kwargs={"pk": box.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == box.name
        assert response.data["description"] == box.description
        assert response.data["source_language"]["name"] == box.source_language.name
        assert response.data["target_language"]["name"] == box.target_language.name

    def test_create_box(self, authenticated_client, user, languages):
        """Test creating a new box."""
        url = reverse("box-list")
        data = {
            "name": "New Box",
            "description": "A new test box",
            "source_language_id": languages[0].id,
            "target_language_id": languages[1].id,
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == data["name"]
        assert response.data["description"] == data["description"]
        assert response.data["source_language"]["name"] == languages[0].name
        assert response.data["target_language"]["name"] == languages[1].name

        # Confirm box is in database and associated with the authenticated user
        box = Box.objects.get(name=data["name"])
        assert box.user == user

    def test_update_box(self, authenticated_client, box):
        """Test updating a box."""
        url = reverse("box-detail", kwargs={"pk": box.pk})
        data = {"name": "Updated Box Name"}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]

        # Confirm box is updated in database
        box.refresh_from_db()
        assert box.name == data["name"]

    def test_delete_box(self, authenticated_client, box):
        """Test deleting a box."""
        url = reverse("box-detail", kwargs={"pk": box.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Confirm box is deleted from database
        assert not Box.objects.filter(pk=box.pk).exists()


@pytest.mark.django_db
class TestCardViewSet:
    """Tests for the CardViewSet."""

    def test_list_cards(self, authenticated_client, card):
        """Test listing cards."""
        url = reverse("card-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["source_text"] == card.source_text
        assert response.data[0]["target_text"] == card.target_text

    def test_list_cards_filtered_by_box(self, authenticated_client, card, box):
        """Test filtering cards by box."""
        # Create another box and card
        other_box = Box.objects.create(
            name="Other Box",
            description="Another test box",
            user=box.user,
            source_language=box.source_language,
            target_language=box.target_language,
        )

        other_card = Card.objects.create(
            source_text="Other Card", target_text="Otra Tarjeta", box=other_box
        )

        # Get cards filtered by the original box
        url = reverse("card-list") + f"?box={box.id}"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Only cards from the specified box should be returned
        card_texts = [c["source_text"] for c in response.data]
        assert card.source_text in card_texts
        assert other_card.source_text not in card_texts

    def test_retrieve_card(self, authenticated_client, card):
        """Test retrieving a specific card."""
        url = reverse("card-detail", kwargs={"pk": card.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["source_text"] == card.source_text
        assert response.data["target_text"] == card.target_text
        assert response.data["box"]["name"] == card.box.name

    def test_create_card(self, authenticated_client, box):
        """Test creating a new card."""
        url = reverse("card-list")
        data = {
            "source_text": "New Card",
            "target_text": "Nueva Tarjeta",
            "box_id": box.id,
        }
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["source_text"] == data["source_text"]
        assert response.data["target_text"] == data["target_text"]
        assert response.data["box"]["name"] == box.name

        # Confirm card is in database
        assert Card.objects.filter(source_text=data["source_text"]).exists()

    def test_update_card(self, authenticated_client, card):
        """Test updating a card."""
        url = reverse("card-detail", kwargs={"pk": card.pk})
        data = {"source_text": "Updated Card Text"}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["source_text"] == data["source_text"]

        # Confirm card is updated in database
        card.refresh_from_db()
        assert card.source_text == data["source_text"]

    def test_delete_card(self, authenticated_client, card):
        """Test deleting a card."""
        url = reverse("card-detail", kwargs={"pk": card.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Confirm card is deleted from database
        assert not Card.objects.filter(pk=card.pk).exists()

    def test_recall_card_remembered(self, authenticated_client, card):
        """Test recording a remembered recall for a card."""
        url = reverse("card-recall", kwargs={"pk": card.pk})
        data = {"remembered": True}

        # Get the initial recall count
        initial_recall_count = card.recall_count

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["recall_count"] == initial_recall_count + 1
        assert "last_recall" in response.data
        assert "next_recall" in response.data

        # Confirm card is updated in database
        card.refresh_from_db()
        assert card.recall_count == initial_recall_count + 1
        assert card.last_recall is not None
        assert card.next_recall is not None

    def test_recall_card_not_remembered(self, authenticated_client, card):
        """Test recording a not remembered recall for a card."""
        url = reverse("card-recall", kwargs={"pk": card.pk})
        data = {"remembered": False}

        # Set an initial recall count greater than 0
        card.recall_count = 5
        card.save()

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["recall_count"] == 0  # Should be reset to 0
        assert "last_recall" in response.data
        assert "next_recall" in response.data

        # Confirm card is updated in database
        card.refresh_from_db()
        assert card.recall_count == 0
        assert card.last_recall is not None
        assert card.next_recall is not None
