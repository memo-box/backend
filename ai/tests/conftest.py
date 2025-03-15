import pytest
from unittest.mock import Mock
from langchain_openai import ChatOpenAI


@pytest.fixture
def mock_chat_openai():
    """
    Fixture providing a mocked ChatOpenAI instance
    that can be reused across different tests
    """
    mock = Mock(spec=ChatOpenAI)
    mock.invoke.return_value = Mock(content="Default mocked response")
    return mock
