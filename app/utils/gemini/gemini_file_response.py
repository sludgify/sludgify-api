import pathlib
import asyncio
from google import genai
from google.genai import types


class GeminiFileCitationController:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_response_text(
        self,
        file_paths: list[str],
        prompt: str,
    ) -> str:
        valid_files = [
            p for p in file_paths if p and isinstance(p, str) and not p.isspace()
        ]

        if not valid_files:
            raise ValueError("At least one file path is required.")
        if not prompt or prompt.isspace():
            raise ValueError("Prompt is required and must not be blank.")
        elif not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")

        try:
            client_ai = genai.Client(api_key=self.api_key)
            grounding_tools = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(tools=[grounding_tools])

            uploaded_files = []
            for path_str in valid_files:
                file_path_obj = pathlib.Path(path_str)
                if file_path_obj.exists() and file_path_obj.is_file():
                    uploaded = client_ai.files.upload(file=file_path_obj)
                    uploaded_files.append(uploaded)
                else:
                    raise FileNotFoundError(f"File not found: {path_str}")

            contents = uploaded_files + [prompt]

            response = client_ai.models.generate_content(
                model="gemini-2.5-flash", contents=contents, config=config
            )

            citation_text = self.add_citations(response)
            return citation_text

        except Exception as e:
            raise RuntimeError(f"Failed to generate content: {str(e)}")

    def add_citations(self, response):
        if not response.candidates:
            return getattr(response, "text", "")

        candidate = response.candidates[0]
        metadata = getattr(candidate, "grounding_metadata", None)
        if not metadata or not getattr(metadata, "grounding_supports", None):
            return getattr(response, "text", candidate.content.parts[0].text)

        supports = metadata.grounding_supports
        chunks = metadata.grounding_chunks or []
        text = getattr(response, "text", candidate.content.parts[0].text)

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
