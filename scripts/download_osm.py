import osmnx as ox
from pathlib import Path

print("=" * 60)
print("Downloading UAE OpenStreetMap Data")
print("=" * 60)

# Output folder
output_dir = Path("data/raw/osm")
output_dir.mkdir(parents=True, exist_ok=True)

# Download Dubai road network
print("Downloading road network...")

graph = ox.graph_from_place(
    "Dubai, United Arab Emirates",
    network_type="drive"
)

# Save graph
output_file = output_dir / "dubai_roads.graphml"

ox.save_graphml(graph, output_file)

print()
print("Saved to:")
print(output_file)