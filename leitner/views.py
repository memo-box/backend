from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import CustomUser, Language, Box, Card
from .serializers import (
    UserSerializer, 
    LanguageSerializer, 
    BoxSerializer, 
    CardSerializer, 
    CardRecallSerializer
)


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
    
    def get_serializer_class(self):
        if self.action == 'recall':
            return CardRecallSerializer
        return CardSerializer

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
   
    @action(detail=True, methods=['post'])
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
        