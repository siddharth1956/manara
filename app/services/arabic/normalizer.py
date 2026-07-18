from camel_tools.utils.normalize import (
    normalize_alef_maksura_ar,
    normalize_alef_ar,
    normalize_teh_marbuta_ar,
)

from camel_tools.utils.dediac import dediac_ar


class ArabicNormalizer:

    def normalize(self, text: str) -> str:
        """
        Normalize Arabic text while preserving meaning.
        """

        # Remove diacritics
        text = dediac_ar(text)

        # Normalize Alef variants
        text = normalize_alef_ar(text)

        # Normalize Alef Maksura
        text = normalize_alef_maksura_ar(text)

        # Normalize Teh Marbuta
        text = normalize_teh_marbuta_ar(text)

        # Remove extra whitespace
        text = " ".join(text.split())

        return text