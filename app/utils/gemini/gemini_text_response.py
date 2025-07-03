from google import genai
from google.genai import types


class Textresponse:
    def __init__(self, text: str, thought: bool):
        self.text = text
        self.thought = thought

    def __repr__(self):
        return f"<Textresponse text={self.text[:30]!r} thought={self.thought}>"

    def to_dict(self):
        return {"text": self.text, "thought": self.thought}


class GeminiTextResponder:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = genai.Client(api_key=self.api_key)

    def get_response(self, prompt: str) -> list[Textresponse]:
        """
        Mengirim prompt teks ke Gemini dan mengembalikan list of Textresponse.
        Raise Exception jika gagal.
        """

        # Validasi input
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt harus berupa teks dan tidak boleh kosong.")

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(include_thoughts=True)
                ),
            )

            output = []
            for part in response.candidates[0].content.parts:
                if not part.text:
                    continue
                output.append(Textresponse(part.text, bool(part.thought)))

            return output

        except Exception as e:
            raise RuntimeError(f"Gagal menghasilkan respon dari Gemini: {e}") from e


responder = GeminiTextResponder(api_key="YOUR_API_KEY")

try:
    responses = responder.get_response("Apa itu perubahan iklim?")
    for res in responses:
        print(res.text)
except Exception as e:
    print("Terjadi kesalahan:", e)
