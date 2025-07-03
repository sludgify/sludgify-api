import pathlib
from google import genai
from google.genai import types


class Readfile:
    def __init__(self, text: str, thought: bool):
        self.text = text
        self.thought = thought

    def __repr__(self):
        return f"<Readfile text={self.text[:30]!r} thought={self.thought}>"

    def to_dict(self):
        return {"text": self.text, "thought": self.thought}


class GeminiFileReader:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)

    def analyze_file(self, pdf_path: str, prompt: str) -> list[Readfile]:
        """
        Membaca file PDF dan memberikan analisis berdasarkan prompt.
        Return list of Readfile objects atau raise Exception.
        """

        # Validasi input
        if not isinstance(pdf_path, str) or not pdf_path.strip():
            raise ValueError("Path PDF tidak valid.")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt tidak boleh kosong.")

        doc_path = pathlib.Path(pdf_path)
        if not doc_path.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {pdf_path}")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
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
                if not part.text:
                    continue
                output.append(Readfile(part.text, bool(part.thought)))

            return output

        except Exception as e:
            raise RuntimeError(f"Gagal membaca file dengan Gemini: {e}") from e


reader = GeminiFileReader(api_key="YOUR_API_KEY")

try:
    result = reader.analyze_file(
        "fileku.pdf", "Jelaskan isi bab pertama secara ringkas"
    )
    for item in result:
        print(item.text)
except Exception as e:
    print("Terjadi kesalahan:", e)
