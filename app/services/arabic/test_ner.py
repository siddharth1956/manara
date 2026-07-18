from app.services.arabic.ner import ArabicNER
ner = ArabicNER()

text = "ما هو متوسط الغطاء السحابي في دبي؟"

print("Question:")
print(text)

print("\nEntities:")

print(ner.extract(text))