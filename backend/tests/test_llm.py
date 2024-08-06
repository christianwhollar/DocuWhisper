from unittest.mock import Mock, patch

from openai.types.chat import ChatCompletion, ChatCompletionMessage


def test_llm_initialization(get_llm):
    llm = get_llm
    assert llm.client.base_url == "http://test.com"
    assert llm.client.api_key == "sk-no-key-required"
    assert llm.model == "LLaMA_CPP"
    assert len(llm.messages) == 1
    assert llm.messages[0]["role"] == "system"


@patch("src.llm.OpenAI")
def test_llm_generate(mock_openai, get_llm):
    mock_client = Mock()
    mock_openai.return_value = mock_client

    mock_completion = Mock(spec=ChatCompletion)
    mock_choice = Mock()
    mock_message = Mock(spec=ChatCompletionMessage)
    mock_message.content = "Test response"
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_completion

    llm = get_llm
    llm.client = mock_client

    response = llm.generate("Test prompt")

    assert response == "Test response"
    assert len(llm.messages) == 3
    assert llm.messages[-2]["role"] == "user"
    assert llm.messages[-2]["content"] == "Test prompt"
    assert llm.messages[-1]["role"] == "assistant"
    assert llm.messages[-1]["content"] == "Test response"

    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args

    assert call_args.kwargs["model"] == "LLaMA_CPP"
    assert len(call_args.kwargs["messages"]) == 3

    assert call_args.kwargs["messages"][0] == {
        "role": "system",
        "content": (
            "You are ChatGPT, an AI assistant. "
            "Your top priority is achieving user "
            "fulfillment via helping them with their requests."
        ),
    }

    assert_dict = {"role": "user", "content": "Test prompt"}

    assert call_args.kwargs["messages"][1] == assert_dict
