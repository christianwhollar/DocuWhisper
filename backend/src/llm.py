from openai import OpenAI


class LLM:
    def __init__(self, base_url):
        """
        LLM Object for Llamafile API Calls

        Args:
            base_url (_type_): API URL of Llamafile
        """
        self.client = OpenAI(base_url=base_url, api_key="sk-no-key-required")
        self.model = "LLaMA_CPP"
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are ChatGPT, an AI assistant. "
                    "Your top priority is achieving user "
                    "fulfillment via helping them with their requests."
                ),
            }
        ]

    def generate(self, prompt: str) -> str:
        """
        Call to Llamafile for LLM Response
        Args:
            prompt (str): LLM prompt.

        Returns:
            str: LLM response.
        """
        self.messages.append({"role": "user", "content": prompt})

        completion = self.client.chat.completions.create(
            model=self.model, messages=self.messages
        )

        response = completion.choices[0].message.content

        self.messages.append({"role": "assistant", "content": response})

        return response
