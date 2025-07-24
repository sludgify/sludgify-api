import pycountry
from deep_translator import GoogleTranslator


class Misc:
    def get_country_code(name):
        try:
            country = pycountry.countries.lookup(name)
            return country.alpha_2
        except LookupError:
            return None

    def translator(text, target):
        translation = GoogleTranslator(source="auto", target=target.lower()).translate(
            text
        )
        return translation
