from rest_framework import serializers
from .models import CustomUser, Box, Card, Language
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user details."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["name"] = user.name
        token["email"] = user.email
        token["is_staff"] = user.is_staff

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra responses here
        data["user_id"] = self.user.id
        data["email"] = self.user.email
        data["name"] = self.user.name
        data["is_staff"] = self.user.is_staff

        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = CustomUser
        fields = [
            "url",
            "email",
            "name",
            "password",
            "is_staff",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "is_staff"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            name=validated_data["name"],
            password=validated_data["password"],
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "name", "code", "created_at", "updated_at"]
        read_only_fields = ["id", "code", "created_at", "updated_at"]


class BoxSerializer(serializers.ModelSerializer):
    source_language = LanguageSerializer(read_only=True)
    target_language = LanguageSerializer(read_only=True)
    source_language_id = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(), source="source_language", write_only=True
    )
    target_language_id = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(), source="target_language", write_only=True
    )

    class Meta:
        model = Box
        fields = [
            "url",
            "name",
            "description",
            "source_language",
            "target_language",
            "source_language_id",
            "target_language_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class CardSerializer(serializers.ModelSerializer):
    box = BoxSerializer(read_only=True)
    box_id = serializers.PrimaryKeyRelatedField(
        queryset=Box.objects.all(), source="box", write_only=True
    )

    class Meta:
        model = Card
        fields = [
            "url",
            "id",
            "source_text",
            "target_text",
            "box",
            "box_id",
            "recall_count",
            "last_recall",
            "next_recall",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "recall_count",
            "last_recall",
            "next_recall",
            "created_at",
            "updated_at",
        ]


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
        remembered = validated_data.get("remembered", True)
        instance.record_recall(remembered=remembered)

        return instance
