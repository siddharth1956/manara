import json
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# Load Results
# -------------------------------

with open("evaluation/results.json") as f:
    data = json.load(f)

results = pd.DataFrame(data["results"])

summary = {
    "Total Queries": data["total_queries"],
    "Intent Accuracy": data["intent_accuracy"],
    "Average Latency": data["average_latency"],
    "Average Sources": data["average_sources"],
    "Analytics Queries": data["analytics_queries"],
    "RAG Queries": data["rag_queries"],
    "Failed Requests": data["failed_requests"]
}

# -------------------------------
# Summary
# -------------------------------

print("=" * 60)

print("MANARA Evaluation Summary")

print("=" * 60)

for k, v in summary.items():

    print(f"{k:25}: {v}")

# -------------------------------
# Latency Chart
# -------------------------------

plt.figure(figsize=(10,5))

plt.bar(

    range(len(results)),

    results["latency"]

)

plt.title("Query Latency")

plt.xlabel("Query Number")

plt.ylabel("Seconds")

plt.tight_layout()

plt.savefig("evaluation/latency_chart.png")

plt.close()

# -------------------------------
# Intent Distribution
# -------------------------------

intent_counts = results["predicted"].value_counts()

plt.figure(figsize=(8,6))

intent_counts.plot(

    kind="bar"

)

plt.title("Predicted Intent Distribution")

plt.ylabel("Queries")

plt.tight_layout()

plt.savefig(

    "evaluation/intent_distribution.png"

)

plt.close()

# -------------------------------
# Sources Used
# -------------------------------

plt.figure(figsize=(10,5))

plt.bar(

    range(len(results)),

    results["sources"]

)

plt.title("Retrieved Sources")

plt.xlabel("Query Number")

plt.ylabel("Sources")

plt.tight_layout()

plt.savefig(

    "evaluation/source_usage.png"

)

plt.close()

# -------------------------------
# Query Category
# -------------------------------

expected = results["expected"]

category = expected.value_counts()

plt.figure(figsize=(8,6))

category.plot(

    kind="pie",

    autopct="%1.1f%%"

)

plt.ylabel("")

plt.title("Query Categories")

plt.tight_layout()

plt.savefig(

    "evaluation/query_distribution.png"

)

plt.close()

# -------------------------------
# Text Report
# -------------------------------

with open(

    "evaluation/evaluation_summary.txt",

    "w"

) as f:

    for k, v in summary.items():

        f.write(f"{k}: {v}\n")

print()

print("Graphs Generated Successfully")

print()

print("✓ latency_chart.png")

print("✓ intent_distribution.png")

print("✓ query_distribution.png")

print("✓ source_usage.png")

print("✓ evaluation_summary.txt")
