from .inventaris_rumus import (
    kalkulator_emisi_default,
    hitung_emisi_co2_coprocessing,
    hitung_emisi_co2e_kompos,
    hitung_emisi_maggot,
)


def calculate_emisi(metode: str, massa: float, user_input: str) -> dict:
    try:
        if metode == "default":
            input_lower = user_input.lower()
            if "non" in input_lower and "b3" in input_lower:
                sludge_type = "Non-B3"
            elif "b3" in input_lower:
                sludge_type = "B3"
            else:
                sludge_type = "Non-B3"
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
