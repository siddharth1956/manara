import json
import time
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000/query"

df = pd.read_csv("evaluation/evaluation_queries.csv")

results = []

correct = 0
latencies = []
failures = 0
analytics_queries = 0
rag_queries = 0
source_counts = []

print("=" * 60)
print("MANARA Evaluation")
print("=" * 60)

for _, row in df.iterrows():

    query = row["query"]
    expected = row["intent"]

    start = time.time()

    try:

        response = requests.post(
            API_URL,
            json={"question": query}
        )

        latency = round(time.time() - start, 3)

        data = response.json()

        predicted = data.get("intent", "unknown")

        if predicted == expected:
            correct += 1

        if predicted == "analytics":
            analytics_queries += 1
        else:
            rag_queries += 1

        sources = len(data.get("sources", []))
        source_counts.append(sources)

        latencies.append(latency)

        results.append({

            "query": query,
            "expected": expected,
            "predicted": predicted,
            "correct": predicted == expected,
            "latency": latency,
            "sources": sources

        })

        print(f"✓ {query}")

    except Exception as e:

        failures += 1

        print(f"✗ {query}")
        print(e)

summary = {

    "total_queries": len(df),

    "intent_accuracy":
        round(correct / len(df) * 100, 2),

    "average_latency":
        round(sum(latencies) / len(latencies), 2),

    "analytics_queries":
        analytics_queries,

    "rag_queries":
        rag_queries,

    "average_sources":
        round(sum(source_counts) / len(source_counts), 2),

    "failed_requests":
        failures,

    "results":
        results

}

with open("evaluation/results.json", "w") as f:

    json.dump(summary, f, indent=4)

print("\nEvaluation Complete\n")

print(json.dumps(summary, indent=4))