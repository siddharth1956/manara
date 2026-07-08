import osmnx as ox
import pandas as pd
from pathlib import Path

input_file = Path("data/raw/osm/dubai_roads.graphml")

print("Loading road network...")

G = ox.load_graphml(input_file)

nodes, edges = ox.graph_to_gdfs(G)

print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")

# Keep useful columns only
roads = edges[
    ["name", "highway", "length", "geometry"]
].copy()

roads.to_csv(
    "data/processed/dubai_roads.csv",
    index=False
)

print("\nSample Roads:")
print(roads.head())

print("\nSaved to:")
print("data/processed/dubai_roads.csv")