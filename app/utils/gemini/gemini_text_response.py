from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError


class GeminiESGReporter:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """Inisialisasi Gemini client dan konfigurasi dengan Google Search tool."""
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
        self.response: types.GenerateContentResponse | None = None

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5)
    )
    def _generate_content_with_retry(
        self, prompt: str
    ) -> types.GenerateContentResponse:
        """Mencoba menghasilkan konten dengan retry logic untuk meningkatkan keandalan."""
        return self.client.models.generate_content(
            model=self.model, contents=prompt, config=self.config
        )

    def generate_report(self, prompt: str) -> str | None:
        """
        Menghasilkan laporan ESG berdasarkan prompt yang diberikan.
        Mengembalikan teks mentah (tanpa citation) atau None jika gagal.
        """
        try:
            self.response = self._generate_content_with_retry(prompt)
            return self.response.text
        except RetryError as e:
            print("❌ Gagal mendapatkan respon setelah beberapa kali percobaan.")
            print(f"📄 Detail error: {e}")
            return None

    def generate_report_with_citations(self, prompt: str) -> str | None:
        """
        Menghasilkan laporan ESG dan menambahkan citation/link sumber.
        """
        text = self.generate_report(prompt)
        if text is None:
            return None
        return self._add_citations()

    def _add_citations(self) -> str:
        """Menambahkan link citation dari grounding_metadata ke dalam teks respon."""
        if not self.response:
            raise ValueError(
                "No response generated. Please run generate_report() first."
            )

        candidate = self.response.candidates[0]
        text = (
            candidate.content.parts[0].text
            if candidate.content.parts
            else self.response.text
        )

        metadata = candidate.grounding_metadata
        if not metadata or not metadata.grounding_supports:
            return text

        supports = metadata.grounding_supports
        chunks = metadata.grounding_chunks

        for support in sorted(
            supports, key=lambda s: s.segment.end_index, reverse=True
        ):
            end_index = support.segment.end_index
            links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks) and chunks[i].web and chunks[i].web.uri:
                    links.append(f"[{i + 1}]({chunks[i].web.uri})")

            if links:
                citation = " " + ", ".join(links)
                text = text[:end_index] + citation + text[end_index:]

        return text
