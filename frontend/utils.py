import re


def clean_response(response: str) -> str:
    # Remove specific unwanted tags
    response = response.replace("</s>", "")

    # Remove potential HTML tags
    response = re.sub(r"<[^>]+>", "", response)

    # Trim whitespace
    response = response.strip()

    response = response.replace("  ", " ")

    return response
