from pydantic import BaseModel, Field
from typing import List, Optional


class BackcardResponse(BaseModel):
    """Schema for backcard generation response."""

    translation: Optional[str] = Field(
        None, description="Translation of the word/phrase in target language"
    )
    definition: Optional[str] = Field(None, description="Definition in source language")
    example_sentences: Optional[str] = Field(
        None, description="Example sentence in source language"
    )
    example_sentences_translated: Optional[str] = Field(
        None, description="Translated example sentence"
    )
    pronunciation: Optional[str] = Field(None, description="IPA pronunciation")

    model_config = {
        "json_schema_extra": {
            "example": {
                "translation": "Verschiebe deine heutige Arbeit nicht auf morgen",
                "definition": "1. کار امروز را به فردا نسپار: به تعویق انداختن انجام کارها و مسئولیت‌ها",
                "example_sentences": "کار امروز را به فردا نسپار، زیرا ممکن است دیر شود.",
                "example_sentences_translated": "Verschiebe deine heutige Arbeit nicht auf morgen, denn es könnte zu spät werden.",
                "pronunciation": "/kɒːr emruz rɒ be fardɒ nespɒr/",
            }
        }
    }


class TopicCard(BaseModel):
    """Schema for a single card in topic generation."""

    front: str = Field(..., description="Word or phrase in source language")
    back: Optional[str] = Field(None, description="Translation in target language")
    pronunciation: Optional[str] = Field(None, description="IPA pronunciation")
    definition: Optional[str] = Field(None, description="Definition in source language")
    example_sentence: Optional[str] = Field(
        None, description="Example sentence in source language"
    )
    example_sentence_translated: Optional[str] = Field(
        None, description="Translated example sentence"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "front": "apple",
                "back": "Apfel",
                "pronunciation": "ˈæp.əl",
                "definition": "A round fruit with red, green, or yellow skin and firm white flesh.",
                "example_sentence": "She ate an apple for breakfast.",
                "example_sentence_translated": "Sie aß einen Apfel zum Frühstück.",
            }
        }
    }


class TopicGenerationResponse(BaseModel):
    """Schema for topic generation response."""

    cards: List[TopicCard] = Field(..., description="List of generated cards")

    model_config = {
        "json_schema_extra": {
            "example": {
                "cards": [
                    {
                        "front": "apple",
                        "back": "Apfel",
                        "pronunciation": "ˈæp.əl",
                        "definition": "A round fruit with red, green, or yellow skin and firm white flesh.",
                        "example_sentence": "She ate an apple for breakfast.",
                        "example_sentence_translated": "Sie aß einen Apfel zum Frühstück.",
                    },
                    {
                        "front": "bread",
                        "back": "Brot",
                        "pronunciation": "brɛd",
                        "definition": "A food made of flour, water, and yeast, mixed together and baked.",
                        "example_sentence": "He bought a loaf of bread from the bakery.",
                        "example_sentence_translated": "Er kaufte ein Laib Brot in der Bäckerei.",
                    },
                ]
            }
        }
    }
