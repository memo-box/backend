from django.urls import path
from .views import GenerateBackcardView, GenerateTopicCardsView

app_name = "ai"

urlpatterns = [
    path(
        "ai-generation/generate_backcard/",
        GenerateBackcardView.as_view(),
        name="generate-backcard",
    ),
    path(
        "ai-generation/generate_topic_cards/",
        GenerateTopicCardsView.as_view(),
        name="generate-topic-cards",
    ),
]
