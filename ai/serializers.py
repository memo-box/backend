from rest_framework import serializers
from leitner.constants import LANGUAGE_CHOICES


class BackcardGenerationSerializer(serializers.Serializer):
    """Serializer for backcard generation request."""

    word_or_phrase = serializers.CharField(required=True)
    source_language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, required=True)
    target_language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, required=True)


class TopicCardsGenerationSerializer(serializers.Serializer):
    """Serializer for topic cards generation request."""

    topic = serializers.CharField(required=True)
    source_language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, required=True)
    target_language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, required=True)
    count = serializers.IntegerField(
        min_value=1, max_value=200, default=50, required=False
    )

    def validate_count(self, value):
        """Validate count field and return default if invalid."""
        try:
            int_value = int(value)
            if 1 <= int_value <= 200:
                return int_value
        except (ValueError, TypeError):
            pass
        return 50
