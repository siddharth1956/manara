from app.services.arabic.tokenizer import ArabicTokenizer
tokenizer = ArabicTokenizer()

text = "ما هو متوسط نسبة الغطاء السحابي؟"

tokens = tokenizer.tokenize(text)

print("Sentence:")
print(text)

print("\nTokens:")
print(tokens)