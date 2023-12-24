import networkx as nx
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.wkt import loads


nodelist_file = 'nodelist_upd.csv'
edgelist_file = 'edgelist_upd.csv'
path_file = 'path_upd.csv'
poi_file = 'poi_upd.csv'


G = nx.MultiDiGraph()


nodelist = pd.read_csv(nodelist_file)
for index, row in nodelist.iterrows():
    geom = loads(row['geometry'])
    row_data = row.to_dict()
    row_data.pop('x', None)  
    row_data.pop('y', None) 
    G.add_node(row['id'], x=geom.x, y=geom.y, **row_data)

poi_list = pd.read_csv(poi_file)
for index, row in poi_list.iterrows():
    geom = loads(row['geometry'])
    row_data = row.to_dict()
    row_data.pop('x', None) 
    row_data.pop('y', None)  
    G.add_node(row['osmid'], x=geom.x, y=geom.y, poi=True, **row_data)


path_data = pd.read_csv(path_file)
for index, row in path_data.iterrows():
    geom = loads(row['geometry'])
    G.add_node(f"cross_{index}", x=geom.coords[-1][0], y=geom.coords[-1][1], path=True)

edgelist = pd.read_csv(edgelist_file)
for index, row in edgelist.iterrows():
    G.add_edge(row['start_node'], row['end_node'], **row.to_dict())

for index, row in path_data.iterrows():
    G.add_edge(row['start_node'], f"cross_{index}", **row.to_dict())

node_data = []
for node, data in G.nodes(data=True):
    if 'x' in data and 'y' in data:
        geom = Point(data['x'], data['y'])
        node_data.append({**data, 'geometry': geom})
node_gdf = gpd.GeoDataFrame(node_data)

edge_data = []
for start_node, end_node, data in G.edges(data=True):
    if 'geometry' in data and isinstance(data['geometry'], str):
        try:
            geom = loads(data['geometry'])
        except Exception:
            continue 
    else:
        if 'x' in G.nodes[start_node] and 'y' in G.nodes[start_node] and 'x' in G.nodes[end_node] and 'y' in G.nodes[end_node]:
            start_geom = Point(G.nodes[start_node]['x'], G.nodes[start_node]['y'])
            end_geom = Point(G.nodes[end_node]['x'], G.nodes[end_node]['y'])
            geom = LineString([start_geom, end_geom])
        else:
            continue 
    edge_data.append({**data, 'geometry': geom})
edge_gdf = gpd.GeoDataFrame(edge_data)

node_gdf.to_file('nodes.geojson', driver='GeoJSON')
edge_gdf.to_file('edges.geojson', driver='GeoJSON')