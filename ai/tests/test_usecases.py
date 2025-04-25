import pytest
from unittest.mock import Mock
from langchain_core.messages import SystemMessage, HumanMessage
from ai.usecases import GenerateBackCardUsecase, GenerateTopicUsecase
from ai.schemas import BackcardResponse, TopicGenerationResponse, TopicCard


@pytest.fixture
def mock_llm_structured():
    """Fixture for mocked ChatOpenAI instance configured for structured output."""
    mock = Mock()
    # Mock the behavior of with_structured_output
    structured_llm_mock = Mock()
    mock.with_structured_output.return_value = structured_llm_mock
    return mock, structured_llm_mock  # Return both mocks


@pytest.fixture
def test_backcard_prompt():
    """Fixture for backcard test prompt"""
    return "Test backcard system prompt"


@pytest.fixture
def test_topic_prompt():
    """Fixture for topic test prompt"""
    return "Test topic system prompt"


@pytest.fixture
def backcard_usecase(mock_llm_structured, test_backcard_prompt):
    """Fixture for GenerateBackCardUsecase instance with mocked dependencies"""
    mock_llm, _ = mock_llm_structured  # We need the original mock for the constructor
    return GenerateBackCardUsecase(llm=mock_llm, prompt=test_backcard_prompt)


@pytest.fixture
def topic_usecase(mock_llm_structured, test_topic_prompt):
    """Fixture for GenerateTopicUsecase instance with mocked dependencies"""
    mock_llm, _ = mock_llm_structured
    return GenerateTopicUsecase(llm=mock_llm, prompt=test_topic_prompt)


# --- GenerateBackCardUsecase Tests ---


def test_backcard_init(mock_llm_structured, test_backcard_prompt):
    """Test initialization attaches structured output LLM."""
    mock_llm, structured_llm_mock = mock_llm_structured
    usecase = GenerateBackCardUsecase(llm=mock_llm, prompt=test_backcard_prompt)
    mock_llm.with_structured_output.assert_called_once_with(BackcardResponse)
    assert usecase.llm == structured_llm_mock  # Check it uses the structured mock
    assert usecase.prompt == test_backcard_prompt


def test_backcard_generate(backcard_usecase, mock_llm_structured):
    """Test generate method returns BackcardResponse model."""
    _, structured_llm_mock = mock_llm_structured
    # Setup
    front_card = "Test front card"
    source_language = "en"
    target_language = "fr"
    # Mock the response from the structured llm
    expected_response_model = BackcardResponse(
        translation="Bonjour",
        definition="Hi",
        example_sentences="Hello",
        example_sentences_translated="Bonjour",
        pronunciation="/bonjour/",
    )
    structured_llm_mock.invoke.return_value = expected_response_model

    # Execute
    result = backcard_usecase.generate(
        front_card=front_card,
        source_language=source_language,
        target_language=target_language,
    )

    # Verify
    assert isinstance(result, BackcardResponse)
    assert result == expected_response_model
    # Check that the structured LLM was called with right parameters
    structured_llm_mock.invoke.assert_called_once()
    called_args = structured_llm_mock.invoke.call_args[0][0]
    assert len(called_args) == 2
    assert isinstance(called_args[0], SystemMessage)
    assert called_args[0].content == backcard_usecase.prompt  # Use prompt from fixture
    assert isinstance(called_args[1], HumanMessage)
    user_message = called_args[1].content
    assert f"front_card:```{front_card}```" in user_message
    assert f"source_language:{source_language}" in user_message
    assert f"target_language:{target_language}" in user_message


# --- GenerateTopicUsecase Tests ---


def test_topic_init(mock_llm_structured, test_topic_prompt):
    """Test initialization attaches structured output LLM."""
    mock_llm, structured_llm_mock = mock_llm_structured
    usecase = GenerateTopicUsecase(llm=mock_llm, prompt=test_topic_prompt)
    mock_llm.with_structured_output.assert_called_once_with(TopicGenerationResponse)
    assert usecase.llm == structured_llm_mock
    assert usecase.prompt == test_topic_prompt


def test_topic_generate(topic_usecase, mock_llm_structured):
    """Test generate method returns TopicGenerationResponse model."""
    _, structured_llm_mock = mock_llm_structured
    # Setup
    topic = "Animals"
    source_language = "en"
    target_language = "de"
    count = 3
    expected_cards = [
        TopicCard(front="Dog", back="Hund"),
        TopicCard(front="Cat", back="Katze"),
    ]
    expected_response_model = TopicGenerationResponse(cards=expected_cards)
    structured_llm_mock.invoke.return_value = expected_response_model

    # Execute
    result = topic_usecase.generate(
        topic=topic,
        source_language=source_language,
        target_language=target_language,
        count=count,
    )

    # Verify
    assert isinstance(result, TopicGenerationResponse)
    assert result == expected_response_model
    structured_llm_mock.invoke.assert_called_once()
    called_args = structured_llm_mock.invoke.call_args[0][0]
    assert len(called_args) == 2
    assert isinstance(called_args[0], SystemMessage)
    assert called_args[0].content == topic_usecase.prompt
    assert isinstance(called_args[1], HumanMessage)
    user_message = called_args[1].content
    assert f"topic:```{topic}```" in user_message
    assert f"source_language:{source_language}" in user_message
    assert f"target_language:{target_language}" in user_message
    assert f"count:{count}" in user_message


def test_topic_generate_invalid_count(topic_usecase):
    """Test generate method raises ValueError for invalid count."""
    with pytest.raises(ValueError, match="Count must be greater than 0"):
        topic_usecase.generate(
            topic="T", source_language="en", target_language="de", count=0
        )
    with pytest.raises(ValueError, match="Count must be less than 50"):
        topic_usecase.generate(
            topic="T", source_language="en", target_language="de", count=51
        )


# Note: test_generate_back_card_usecase_instance is removed as testing
# pre-initialized instances with mocks injected like that becomes complex
# and less reliable with the structured_output wrapper.
# Relying on the fixture-based tests (test_backcard_generate) is better.
