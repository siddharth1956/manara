import time
import json
import requests
import pandas as pd

API = "http://127.0.0.1:8000/query"

# --------------------------------------------
# Benchmark Queries
# --------------------------------------------

queries = [

    # Satellite
    ("Show Sentinel images", "satellite_search"),
    ("Show Sentinel-2A scenes", "satellite_search"),
    ("Show Sentinel-2B scenes", "satellite_search"),
    ("Show satellite imagery", "satellite_search"),
    ("Find Copernicus images", "satellite_search"),
    ("Show recent Sentinel images", "satellite_search"),

    # Analytics
    ("What is the average cloud cover?", "analytics"),
    ("Which image has the lowest cloud cover?", "analytics"),
    ("Which image has the highest cloud cover?", "analytics"),
    ("Analyze cloud cover", "analytics"),
    ("Average cloud percentage", "analytics"),
    ("How many satellite images are available?", "analytics"),

    # Roads
    ("Show Dubai roads", "road_search"),
    ("Tell me about the Dubai road network", "road_search"),
    ("Find roads near Dubai", "road_search"),
    ("Show highways", "road_search"),
    ("Show traffic roads", "road_search"),

    # Comparison
    ("Compare Sentinel-2A and Sentinel-2B", "comparison"),
    ("Compare cloud cover", "comparison"),
    ("Compare road and satellite datasets", "comparison"),

    # Map
    ("Where is Bur Dubai?", "map"),
    ("Show Dubai on map", "map"),
    ("Find Dubai location", "map"),
    ("Show coordinates of Dubai", "map"),

    # Arabic
    ("اعرض صور Sentinel", "satellite_search"),
    ("ما متوسط الغطاء السحابي", "analytics"),
    ("اعرض الطرق في دبي", "road_search"),
    ("قارن بين Sentinel-2A و Sentinel-2B", "comparison"),
    ("أين تقع دبي", "map"),
]

results = []

print("=" * 70)
print("MANARA Benchmark Started")
print("=" * 70)

failed = 0

for question, expected in queries:

    start = time.time()

    try:

        response = requests.post(

            API,

            json={
                "question": question
            },

            timeout=60

        )

        latency = round(

            time.time() - start,

            3

        )

        if response.status_code != 200:

            failed += 1

            print(f"✗ {question}")

            continue

        data = response.json()

        predicted = data.get("intent", "unknown")

        language = data.get("language", "unknown")

        model = data.get("model", "unknown")

        sources = len(data.get("sources", []))

        answer = data.get("answer", "")

        results.append({

            "query": question,

            "expected_intent": expected,

            "predicted_intent": predicted,

            "intent_correct": expected == predicted,

            "language": language,

            "model": model,

            "latency_seconds": latency,

            "sources": sources,

            "answer_length": len(answer)

        })

        print(f"✓ {question}")

    except Exception as e:

        failed += 1

        print(f"✗ {question}")

        print(e)

# ---------------------------------------------------
# DataFrame
# ---------------------------------------------------

df = pd.DataFrame(results)

# ---------------------------------------------------
# Statistics
# ---------------------------------------------------

total_queries = len(queries)

successful = len(df)

correct = int(df["intent_correct"].sum())

intent_accuracy = round(

    correct / successful * 100,

    2

) if successful else 0

average_latency = round(

    df["latency_seconds"].mean(),

    3

) if successful else 0

average_sources = round(

    df["sources"].mean(),

    2

) if successful else 0

analytics_queries = len(

    df[df["predicted_intent"] == "analytics"]

)

rag_queries = successful - analytics_queries

summary = {

    "total_queries": total_queries,

    "successful_queries": successful,

    "failed_queries": failed,

    "intent_accuracy": intent_accuracy,

    "average_latency_seconds": average_latency,

    "average_sources": average_sources,

    "analytics_queries": analytics_queries,

    "rag_queries": rag_queries

}

# ---------------------------------------------------
# Save CSV
# ---------------------------------------------------

df.to_csv(

    "evaluation/benchmark_results.csv",

    index=False

)

# ---------------------------------------------------
# Save JSON
# ---------------------------------------------------

with open(

    "evaluation/benchmark_results.json",

    "w"

) as f:

    json.dump(

        {

            "summary": summary,

            "results": results

        },

        f,

        indent=4

    )

# ---------------------------------------------------
# Save Markdown Report
# ---------------------------------------------------

with open(

    "evaluation/benchmark_report.md",

    "w"

) as f:

    f.write("# MANARA Benchmark Report\n\n")

    f.write(f"Total Queries: **{total_queries}**\n\n")

    f.write(f"Successful Queries: **{successful}**\n\n")

    f.write(f"Failed Queries: **{failed}**\n\n")

    f.write(f"Intent Accuracy: **{intent_accuracy}%**\n\n")

    f.write(f"Average Latency: **{average_latency} sec**\n\n")

    f.write(f"Average Sources: **{average_sources}**\n\n")

    f.write(f"Analytics Queries: **{analytics_queries}**\n\n")

    f.write(f"RAG Queries: **{rag_queries}**\n")

print("\n")
print("=" * 70)
print("BENCHMARK SUMMARY")
print("=" * 70)

for key, value in summary.items():

    print(f"{key:30}: {value}")

print("\nFiles Generated:")

print("✓ benchmark_results.csv")

print("✓ benchmark_results.json")

print("✓ benchmark_report.md")

print("=" * 70)