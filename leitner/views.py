from rest_framework import viewsets
from .models import CustomUser, Language, Box, Card
from .serializers import UserSerializer, LanguageSerializer, BoxSerializer, CardSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer

    def get_queryset(self):
        """
        This view should return a list of all boxes
        for the currently authenticated user.
        """
        user = self.request.user
        return Box.objects.filter(user=user)


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned cards to a given box,
        by filtering against a `box` query parameter in the URL.
        """
        queryset = Card.objects.all()
        box_id = self.request.query_params.get('box', None)
        if box_id is not None:
            queryset = queryset.filter(box__id=box_id)
        return queryset
