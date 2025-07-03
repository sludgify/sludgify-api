import json
import re
import google.generativeai as genai
from ..inventaris_rumus import (
    kalkulator_emisi_default,
    hitung_emisi_co2_coprocessing,
    hitung_emisi_co2e_kompos,
    hitung_emisi_maggot,
)


class EmisiCarbonCalculator:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _interpret_user_input(
        self, prompt: str
    ) -> tuple[str | None, float | None, str | None]:
        system_prompt = (
            """
Ekstrak dua informasi penting dari pertanyaan pengguna:
1. metode: salah satu dari "default", "coprocessing", "kompos", "maggot"
2. massa_ton: jumlah ton lumpur (float)

Jawab hanya dalam format JSON seperti:
{"metode": "kompos", "massa_ton": 5}
Kalimat: """
            + prompt
        )

        try:
            response = self.model.generate_content(system_prompt)
            text = response.text.strip()
            match = re.search(r"{.*}", text)
            if match:
                result = json.loads(match.group())
                return result["metode"], float(result["massa_ton"]), None
            else:
                return None, None, "Tidak ditemukan JSON valid."
        except Exception as e:
            return None, None, str(e)

    def _calculate_emisi(self, metode: str, massa: float, user_input: str) -> dict:
        try:
            if metode == "default":
                sludge_type = "B3" if "b3" in user_input.lower() else "Non-B3"
                emisi = kalkulator_emisi_default(massa, sludge_type)
                return {
                    "metode": metode,
                    "massa_ton": massa,
                    "sludge_type": sludge_type,
                    "emisi_kg_CO2": emisi,
                }
            elif metode == "coprocessing":
                emisi = hitung_emisi_co2_coprocessing(massa)
                return {
                    "metode": metode,
                    "massa_ton": massa,
                    "emisi_kg_CO2": round(emisi, 2),
                }
            elif metode == "kompos":
                emisi = hitung_emisi_co2e_kompos(massa)
                return {
                    "metode": metode,
                    "massa_ton": massa,
                    "emisi_kg_CO2": round(emisi, 2),
                }
            elif metode == "maggot":
                emisi = hitung_emisi_maggot(massa)
                return {
                    "metode": metode,
                    "massa_ton": massa,
                    "emisi_kg_CO2": round(emisi, 2),
                }
            else:
                raise ValueError("Metode tidak dikenali.")
        except Exception as e:
            raise RuntimeError(f"Terjadi kesalahan saat menghitung emisi: {e}") from e

    def process(self, prompt: str) -> dict:
        if not prompt or prompt.isspace():
            raise ValueError("Prompt tidak boleh kosong.")

        metode, massa, error = self._interpret_user_input(prompt)
        if error:
            raise RuntimeError(f"Gagal memproses input dengan AI: {error}")
        if not metode or massa is None:
            raise ValueError("Input tidak dikenali, mohon gunakan format yang jelas.")

        return self._calculate_emisi(metode, massa, prompt)
