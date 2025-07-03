import pathlib
from google import genai
from google.genai import types


class Readfile:
    def __init__(self, text: str, thought: bool):
        self.text = text
        self.thought = thought

    def to_dict(self):
        return {"text": self.text, "thought": self.thought}


class GeminiFileResponseController:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def get_response_from_file(self, pdf_path: str, prompt: str) -> list[Readfile]:
        # Validasi
        if not isinstance(pdf_path, str) or not pdf_path.strip():
            raise ValueError("pdf_path is required and must be a non-empty string.")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt is required and must be a non-empty string.")

        doc_path = pathlib.Path(pdf_path)
        if not doc_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(
                        data=doc_path.read_bytes(),
                        mime_type="application/pdf",
                    ),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(include_thoughts=True)
                ),
            )

            output = []
            for part in response.candidates[0].content.parts:
                if part.text:
                    output.append(Readfile(part.text, bool(part.thought)))

            return output

        except Exception as e:
            raise RuntimeError(f"Gagal memproses file dengan Gemini: {str(e)}") from e
