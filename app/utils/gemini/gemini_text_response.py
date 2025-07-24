from google import genai
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError


class GeminiESGReporter:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.grounding_tool = types.Tool(google_search=types.GoogleSearch())
        self.config = types.GenerateContentConfig(tools=[self.grounding_tool])
        self.response = None

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5)
    )
    def _generate_content_with_retry(self, prompt: str):
        return self.client.models.generate_content(
            model=self.model, contents=prompt, config=self.config
        )

    def generate_report(self, prompt: str):
        try:
            self.response = self._generate_content_with_retry(prompt)
            return self.response
        except RetryError as e:
            print("Gagal mendapatkan respon setelah beberapa kali percobaan.")
            print(f"Detail error: {e}")
            return None

    def add_citations(self):
        if self.response is None:
            raise ValueError(
                "No response generated. Please run generate_report() first."
            )

        text = self.response.text
        supports = self.response.candidates[0].grounding_metadata.grounding_supports
        chunks = self.response.candidates[0].grounding_metadata.grounding_chunks

        sorted_supports = sorted(
            supports, key=lambda s: s.segment.end_index, reverse=True
        )

        for support in sorted_supports:
            end_index = support.segment.end_index
            if support.grounding_chunk_indices:
                citation_links = []
                for i in support.grounding_chunk_indices:
                    if i < len(chunks):
                        uri = chunks[i].web.uri
                        citation_links.append(f"[{i + 1}]({uri})")

                citation_string = ", ".join(citation_links)
                text = text[:end_index] + citation_string + text[end_index:]

        return text
