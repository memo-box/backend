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
    source_language = LanguageSerializer(read_only=True)
    target_language = LanguageSerializer(read_only=True)
    source_language_id = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(),
        source='source_language',
        write_only=True
    )
    target_language_id = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(),
        source='target_language',
        write_only=True
    )
    
    class Meta:
        model = Box
        fields = ['url', 'name', 'description', 'source_language', 'target_language', 
                 'source_language_id', 'target_language_id', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CardSerializer(serializers.ModelSerializer):
    box = BoxSerializer(read_only=True)
    box_id = serializers.PrimaryKeyRelatedField(
        queryset=Box.objects.all(),
        source='box',
        write_only=True
    )
    
    class Meta:
        model = Card
        fields = ['url', 'id', 'source_text', 'target_text', 'box', 'box_id', 'recall_count', 'last_recall', 'next_recall', 'created_at', 'updated_at']
        read_only_fields = ['recall_count', 'last_recall', 'next_recall', 'created_at', 'updated_at']

class CardRecallSerializer(serializers.Serializer):
    """
    Serializer for recording a recall event for a card.
    """
    id = serializers.IntegerField(read_only=True)
    remembered = serializers.BooleanField(write_only=True, required=True)
    recall_count = serializers.IntegerField(read_only=True)
    last_recall = serializers.DateTimeField(read_only=True)
    next_recall = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        # Record the recall and get the next recall date
        remembered = validated_data.get('remembered', True)
        instance.record_recall(remembered=remembered)
        
        return instance