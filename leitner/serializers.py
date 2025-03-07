from rest_framework import serializers  
from .models import CustomUser, Box, Card, Language

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['url', 'email', 'name', 'is_staff', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['url', 'name', 'code', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class BoxSerializer(serializers.ModelSerializer):
    source_language = LanguageSerializer()
    target_language = LanguageSerializer()  
    class Meta:
        model = Box
        fields = ['url', 'name', 'description', 'source_language', 'target_language', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CardSerializer(serializers.ModelSerializer):
    box = BoxSerializer()
    class Meta:
        model = Card
        fields = ['url', 'source_text', 'target_text', 'box', 'recall_count', 'last_recall', 'next_recall', 'created_at', 'updated_at']
        read_only_fields = ['recall_count', 'last_recall', 'next_recall', 'created_at', 'updated_at']