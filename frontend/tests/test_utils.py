from utils import clean_response


def test_clean_response():
    response = "This is a test response with a tag </s> inside."
    cleaned_response = clean_response(response)
    assert cleaned_response == "This is a test response with a tag inside."

    response = "<div>This is a test response with an HTML tag</div>"
    cleaned_response = clean_response(response)
    assert cleaned_response == "This is a test response with an HTML tag"

    response = "  Response with leading and trailing whitespace  "
    cleaned_response = clean_response(response)
    assert cleaned_response == "Response with leading and trailing whitespace"

    response = "</s>Starting with tag"
    cleaned_response = clean_response(response)
    assert cleaned_response == "Starting with tag"

    response = "Ending with tag</s>"
    cleaned_response = clean_response(response)
    assert cleaned_response == "Ending with tag"

    response = "<p>Multiple </s> tags </p> and </s> HTML"
    cleaned_response = clean_response(response)
    assert cleaned_response == "Multiple tags and HTML"
