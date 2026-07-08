from app.services.retriever import retrieve
from app.services.generator import generate_answer

print("=" * 60)
print("MANARA AI")
print("=" * 60)

question = input("Question: ")

docs = retrieve(question)

answer = generate_answer(question, docs)

print("\nAnswer:\n")
print(answer)