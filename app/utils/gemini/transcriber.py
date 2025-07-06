import pathlib
from google import genai
from google.genai import types


class Audioresponse:
    def __init__(self, text: str, thought: bool):
        self.text = text
        self.thought = thought

    def __repr__(self):
        return f"<Audioresponse text={self.text[:30]!r} thought={self.thought}>"

    def to_dict(self):
        return {"text": self.text, "thought": self.thought}


class GeminiAudioTranscriber:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)

    def transcribe(self, audio_path: str) -> list[Audioresponse]:
        if not isinstance(audio_path, str) or not audio_path.strip():
            raise ValueError("Audio path harus berupa string dan tidak boleh kosong.")

        path_obj = pathlib.Path(audio_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {audio_path}")

        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(include_thoughts=False)
                ),
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/m4a")
                ],
            )

            output = []
            for part in response.candidates[0].content.parts:
                if not part.text:
                    continue
                output.append(Audioresponse(part.text, bool(part.thought)))

            return output

        except Exception as e:
            raise RuntimeError(f"Gagal memproses audio dengan Gemini: {e}") from e
