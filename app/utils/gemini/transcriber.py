import pathlib
from google import genai
from google.genai import types


class Audioresponse:
    def __init__(self, text: str, thought: bool):
        self.text = text
        self.thought = thought

    def __repr__(self):
        return f"<Audioresponse text={self.text!r} thought={self.thought}>"


class GeminiAudioTranscriber:
    def __init__(self, api_key: str, model: str = "gemini-2.5-pro"):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def transcribe(self, audio_path: str) -> list[Audioresponse]:
        """
        Transcribe audio and return a list of Audioresponse.
        Raises ValueError for input issues, and RuntimeError for transcription issues.
        """

        if not isinstance(audio_path, str) or not audio_path.strip():
            raise ValueError("Audio path must be a non-empty string.")

        path_obj = pathlib.Path(audio_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Audio file not found at path: {audio_path}")

        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(include_thoughts=True)
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
            raise RuntimeError(f"Failed to transcribe audio: {e}") from e


transcriber = GeminiAudioTranscriber(api_key="YOUR_API_KEY")
try:
    responses = transcriber.transcribe("path/to/audio.m4a")
    for res in responses:
        print(res.text, "| thought:", res.thought)
except FileNotFoundError:
    print("File tidak ditemukan.")
except ValueError as ve:
    print("Input tidak valid:", ve)
except RuntimeError as re:
    print("Gagal saat transkripsi:", re)
