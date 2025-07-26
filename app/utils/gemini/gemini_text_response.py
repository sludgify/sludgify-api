from google import genai
from google.genai import types


class GeminiCitationGenerator:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

        # Aktifkan Google Search grounding tool
        self.config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )

    def is_valid_prompt(self, prompt: str) -> bool:
        return (
            isinstance(prompt, str) and not prompt.isspace() and len(prompt.strip()) > 0
        )

    def get_response_text(self, prompt: str) -> str | None:
        """
        Menghasilkan teks dari prompt menggunakan Gemini dan menambahkan citation jika tersedia.
        Return:
            - str: teks hasil respons dengan citation (jika ada)
            - None: jika gagal atau prompt tidak valid
        """
        if not self.is_valid_prompt(prompt):
            print("❌ Prompt tidak valid. Harus berupa string dan tidak kosong.")
            return None

        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt, config=self.config
            )

            return self._add_citations(response)

        except Exception as e:
            print(f"❌ Error saat memanggil Gemini API: {e}")
            return None

    def _add_citations(self, response) -> str:
        if not response.candidates:
            return getattr(response, "text", "")

        candidate = response.candidates[0]
        metadata = getattr(candidate, "grounding_metadata", None)
        text = candidate.content.parts[0].text if candidate.content.parts else ""

        if not metadata or not metadata.grounding_supports:
            return text

        supports = metadata.grounding_supports
        chunks = metadata.grounding_chunks

        for support in sorted(
            supports, key=lambda s: s.segment.end_index, reverse=True
        ):
            end_index = support.segment.end_index
            citation_links = []

            for i in support.grounding_chunk_indices:
                if i < len(chunks) and chunks[i].web and chunks[i].web.uri:
                    citation_links.append(f"[{i + 1}]({chunks[i].web.uri})")

            if citation_links:
                citation_str = " " + ", ".join(citation_links)
                text = text[:end_index] + citation_str + text[end_index:]

        return text
