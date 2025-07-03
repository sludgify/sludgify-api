from google import genai
from google.genai import types


class GeminiError(Exception):
    pass


class TextResponse:
    def __init__(self, text: str, thought: bool):
        self.text = text
        self.thought = thought


class GeminiTextResponseController:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def get_response_text(self, prompt: str) -> list[TextResponse]:
        if not prompt or (isinstance(prompt, str) and prompt.isspace()):
            raise GeminiError("Prompt is required and must be non-empty text.")

        if not isinstance(prompt, str):
            raise GeminiError("Prompt must be a string.")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(include_thoughts=True)
                ),
            )
        except Exception as e:
            raise GeminiError(f"Internal error: {e}") from e

        results = []
        for part in response.candidates[0].content.parts:
            if part.text:
                results.append(TextResponse(part.text, bool(part.thought)))

        return results
