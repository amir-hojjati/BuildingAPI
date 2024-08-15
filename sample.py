import json

import geopandas as gpd
import matplotlib.pyplot as plt

with open('sample.json', 'r') as sample:
    sample = json.load(sample)

b_limits = gpd.GeoDataFrame.from_features(sample['building_limits'])
h_plats = gpd.GeoDataFrame.from_features(sample['height_plateaus'])


fix, axes = plt.subplots(2, 1, figsize=(10, 10))
b_limits.plot(ax=axes[0])
h_plats.plot(ax=axes[1])

# Plot each vertex
for _, row in b_limits.iterrows():
    x, y = row.geometry.exterior.xy
    axes[0].scatter(x, y, color='red', marker='o')

colors = ['blue', 'red', 'green']
i = 0
for _, row in h_plats.iterrows():
    x, y = row.geometry.exterior.xy
    axes[1].scatter(x, y, color=colors[i], marker='x')
    i += 1

plt.legend()
plt.show()

