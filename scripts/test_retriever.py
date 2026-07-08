from app.services.retriever import retrieve

print("=" * 60)
print("MANARA RETRIEVER")
print("=" * 60)

question = input("Question: ")

results = retrieve(question)

print()

for i, r in enumerate(results, 1):

    print(f"Result {i}")
    print(r["text"])
    print("Distance:", r["distance"])
    print("-" * 60)