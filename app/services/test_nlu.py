from app.services.nlu import IntentClassifier

nlu = IntentClassifier()

queries = [
    "Show Dubai roads",
    "Find Sentinel-2 images over Dubai",
    "Average cloud cover",
    "Compare roads and satellite",
    "Where is Bur Dubai?",
    "Show Sentinel-2 images over Dubai yesterday"
]

for q in queries:

    print("=" * 50)
    print("Query:", q)

    result = nlu.analyze(q)

    print(result)