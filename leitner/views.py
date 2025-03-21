from rest_framework import viewsets, status
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


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses our enhanced serializer."""

    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all boxes
        for the currently authenticated user.
        """
        user = self.request.user
        if user.is_authenticated:
            return Box.objects.filter(user=user)
        return Box.objects.none()  # Return empty queryset for anonymous users

    def perform_create(self, serializer):
        """
        Set the user to the current authenticated user when creating a box.
        """
        serializer.save(user=self.request.user)


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
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
        """
        user = self.request.user
        if not user.is_authenticated:
            return Card.objects.none()  # Return empty queryset for anonymous users

        queryset = Card.objects.filter(
            box__user=user
        )  # Only show cards from user's boxes
        box_id = self.request.query_params.get("box", None)
        if box_id is not None:
            queryset = queryset.filter(box__id=box_id)
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
