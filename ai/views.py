from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .schemas import BackcardResponse, TopicGenerationResponse
from .serializers import BackcardGenerationSerializer, TopicCardsGenerationSerializer
from .usecases import generate_back_card_usecase, generate_topic_usecase


class GenerateBackcardView(GenericAPIView):
    """
    API endpoint for generating backcard content.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BackcardGenerationSerializer

    @swagger_auto_schema(
        operation_description="Generate backcard content for a word or phrase",
        request_body=BackcardGenerationSerializer,
        responses={
            200: BackcardResponse.schema(),
            400: openapi.Response(
                description="Invalid language code",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                    example={
                        "error": "Invalid language code. Use one of the supported language codes."
                    },
                ),
            ),
        },
    )
    def post(self, request):
        """
        Generate backcard content for a word or phrase.
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid request data. Please check your input."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_model = generate_back_card_usecase.generate(
            front_card=serializer.validated_data["word_or_phrase"],
            source_language=serializer.validated_data["source_language"],
            target_language=serializer.validated_data["target_language"],
        )

        return Response(response_model.model_dump(exclude_none=True))


class GenerateTopicCardsView(GenericAPIView):
    """
    API endpoint for generating topic cards.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TopicCardsGenerationSerializer

    @swagger_auto_schema(
        operation_description="Generate cards for a specific topic",
        request_body=TopicCardsGenerationSerializer,
        responses={
            200: TopicGenerationResponse.schema(),
            400: openapi.Response(
                description="Invalid language code",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                    example={
                        "error": "Invalid language code. Use one of the supported language codes."
                    },
                ),
            ),
        },
    )
    def post(self, request):
        """
        Generate cards for a specific topic.
        """
        # Use the serializer to handle validation and defaulting of 'count'
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            # If the only error is 'count', the custom validator should have handled it.
            # Any remaining errors mean other fields are invalid.
            return Response(
                {
                    "error": "Invalid request data. Please check your input.",
                    "details": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Serializer validation passed, including defaulting invalid 'count' values via validate_count
        validated_data = serializer.validated_data
        count = validated_data.get(
            "count"
        )  # .get() handles case where count wasn't provided, already defaulted by serializer

        # Call use case with validated data
        response_model = generate_topic_usecase.generate(
            topic=validated_data["topic"],
            source_language=validated_data["source_language"],
            target_language=validated_data["target_language"],
            count=count,
        )

        return Response(response_model.model_dump(exclude_none=True))
