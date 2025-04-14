from rest_framework import viewsets, status, serializers
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser, Language, Box, Card
from .serializers import (
    UserSerializer,
    LanguageSerializer,
    BoxSerializer,
    CardSerializer,
    CardRecallSerializer,
    CustomTokenObtainPairSerializer,
)
from .constants import SUPPORTED_LANGUAGES


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses our enhanced serializer."""

    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by("id")
    serializer_class = UserSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing languages.
    Users can only select from predefined languages.
    """

    queryset = Language.objects.all().order_by("code")
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return all languages, ordered by name.
        """
        return Language.objects.all().order_by("name")

    def perform_create(self, serializer):
        """
        Create a new language, ensuring it's one of the supported languages.
        """
        name = serializer.validated_data.get("name")
        code = serializer.validated_data.get("code")

        if name not in SUPPORTED_LANGUAGES or code not in SUPPORTED_LANGUAGES.values():
            raise serializers.ValidationError(
                "Language must be one of the supported languages."
            )

        serializer.save()


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all().order_by("id")
    serializer_class = BoxSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all boxes
        for the currently authenticated user.
        """
        user = self.request.user
        if user.is_authenticated:
            return Box.objects.filter(user=user).order_by("id")
        return Box.objects.none()  # Return empty queryset for anonymous users

    def perform_create(self, serializer):
        """
        Set the user to the current authenticated user when creating a box.
        """
        serializer.save(user=self.request.user)


class CardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cards.

    list:
        Get a list of all cards belonging to the authenticated user.
        Can be filtered by box_id and due_only parameters.

    Parameters:
        box (int): Optional. Filter cards by box ID.
        due_only (str): Optional. If "true", only returns cards that are due for review
                       (next_recall <= current time).
    """

    queryset = Card.objects.all().order_by("id")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "recall":
            return CardRecallSerializer
        return CardSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned cards to a given box,
        by filtering against a `box` query parameter in the URL.
        Additionally, restricts cards to those belonging to the current user.
        Can also filter to show only cards that are due for review.

        Parameters:
            box (int): Optional box ID to filter cards by. If not provided,
                      returns all cards from all boxes belonging to the user.
            due_only (str): Optional. If "true", only returns cards that are due
                          for review (next_recall <= current time).
        """
        user = self.request.user
        if not user.is_authenticated:
            return Card.objects.none()

        queryset = Card.objects.filter(box__user=user).order_by("id")

        box_id = self.request.query_params.get("box", None)
        if box_id is not None:
            queryset = queryset.filter(box__id=box_id)

        due_only = self.request.query_params.get("due_only", None)
        if due_only == "true":
            queryset = queryset.filter(next_recall__lte=timezone.now())

        return queryset

    @action(detail=True, methods=["post"])
    def recall(self, request, pk=None):
        """
        Record a recall event for a card.
        """
        card = self.get_object()
        serializer = self.get_serializer(card, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
