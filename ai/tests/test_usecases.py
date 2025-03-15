import pytest
from unittest.mock import Mock
from langchain_core.messages import SystemMessage, HumanMessage
from ai.usecases import GenerateBackCardUsecase


@pytest.fixture
def mock_llm():
    """Fixture for mocked ChatOpenAI instance"""
    mock = Mock()
    mock.invoke.return_value = Mock(content="Mocked LLM response")
    return mock


@pytest.fixture
def test_prompt():
    """Fixture for test prompt"""
    return "Test system prompt"


@pytest.fixture
def usecase(mock_llm, test_prompt):
    """Fixture for GenerateBackCardUsecase instance with mocked dependencies"""
    return GenerateBackCardUsecase(llm=mock_llm, prompt=test_prompt)


def test_init(mock_llm, test_prompt):
    """Test initialization of GenerateBackCardUsecase"""
    usecase = GenerateBackCardUsecase(llm=mock_llm, prompt=test_prompt)
    assert usecase.llm == mock_llm
    assert usecase.prompt == test_prompt


def test_generate(usecase, mock_llm):
    """Test generate method of GenerateBackCardUsecase"""
    # Setup
    front_card = "Test front card"
    source_language = "en"
    target_language = "fr"
    expected_response = "Mocked LLM response"

    # Execute
    result = usecase.generate(
        front_card=front_card,
        source_language=source_language,
        target_language=target_language,
    )

    # Verify
    assert result == expected_response
    # Check that LLM was called with right parameters
    mock_llm.invoke.assert_called_once()
    # Extract the call arguments
    called_args = mock_llm.invoke.call_args[0][0]

    # Verify contents of the messages list
    assert len(called_args) == 2
    assert isinstance(called_args[0], SystemMessage)
    assert called_args[0].content == "Test system prompt"
    assert isinstance(called_args[1], HumanMessage)

    # Verify that the user message contains all required information
    user_message = called_args[1].content
    assert f"front_card:```{front_card}```" in user_message
    assert f"source_language:{source_language}" in user_message
    assert f"target_language:{target_language}" in user_message


def test_generate_back_card_usecase_instance():
    """Test the pre-initialized instance of GenerateBackCardUsecase"""
    # Import the module but mock its components
    from ai.usecases import generate_back_card_usecase

    # Create a new mock for direct replacement
    mock_response = Mock(content="Mocked result")
    original_llm = generate_back_card_usecase.llm

    try:
        # Replace the LLM with our mock
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        generate_back_card_usecase.llm = mock_llm

        # Execute the test
        result = generate_back_card_usecase.generate(
            front_card="Test card", source_language="en", target_language="es"
        )

        # Verify
        assert result == "Mocked result"
        mock_llm.invoke.assert_called_once()

    finally:
        # Restore the original LLM
        generate_back_card_usecase.llm = original_llm
