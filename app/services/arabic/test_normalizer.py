from app.services.arabic.normalizer import ArabicNormalizer
normalizer = ArabicNormalizer()

text = "مَا هُوَ مُتَوَسِّطُ نِسْبَةِ الغِطَاءِ السَّحَابِي؟"

print("Original:")
print(text)

print("\nNormalized:")
print(normalizer.normalize(text))