from bridges.data_src_dependent import data_source
from bridges.bridges import Bridges
from bridges.color import Color
import math
import queue as Q

# Calculate the Haversine distance between two lat/lon coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Find the vertex closest to a specific lat/lon coordinate
def getClosest(gr, lat, lon):
    closest_vertex = None
    min_distance = float('inf')
    for v_id, vertex in gr.vertices.items():
        v_lat, v_lon = vertex.value.latitude, vertex.value.longitude
        distance = haversine(lat, lon, v_lat, v_lon)
        if distance < min_distance:
            min_distance = distance
            closest_vertex = v_id
    return closest_vertex

# Style the root vertex distinctly
def style_root(gr, root):
    vertex = gr.get_vertex(root)
    vertex.size = 100 # Make root stand out
    vertex.color = Color("red")  # Bright red for the source vertex

# Implement Dijkstra's algorithm for shortest path calculation
def shortestPath(gr, root):
    distances = {v_id: float('inf') for v_id in gr.vertices}
    parents = {v_id: None for v_id in gr.vertices}
    pq = Q.PriorityQueue()

    distances[root] = 0
    pq.put((0, root))

    while not pq.empty():
        dist_u, u = pq.get()
        if dist_u > distances[u]:
            continue

        # Traverse the adjacency list for vertex `u`
        slelement = gr.get_adjacency_list()[u]
        while slelement:
            edge = slelement.value
            v = edge.tov
            # Default to weight 1 if not provided
            if distances[u] + 1 < distances[v]:
                distances[v] = distances[u] + 1
                parents[v] = u
                pq.put((distances[v], v))
            slelement = slelement.next  # Move to the next element in the list

    return distances, parents


# Style vertices based on their distances from the root
def style_distance(gr, distances):
    max_dist = max(d for d in distances.values() if d < float('inf'))
    for v_id, dist in distances.items():
        vertex = gr.get_vertex(v_id)
        if dist == float('inf'):
            vertex.color = Color("gray")  # Unreachable vertices
        else:
            # Interpolate colors: closer = blue, farther = red
            t = dist / max_dist
            r = int(255 * t)
            b = int(255 * (1 - t))
            vertex.color = Color(r, 0, b)

# Style the shortest path from root to a destination
def style_parent(gr, parents, dest):
    """Style the path from root to the destination."""
    # Style all vertices and edges as almost invisible (e.g., dark color or very small size)
    for v_id in gr.vertices:
        gr.vertices[v_id].color = Color(13, 34, 67)  # Dark navy
        gr.vertices[v_id].size = 2

    for v_id in gr.vertices:
        current = gr.get_adjacency_list()[v_id]
        while current is not None:
            edge = current.value
            edge.color = Color(13, 34, 67)  # Dark navy
            current = current.next

    # Trace the path from `dest` to the root using the `parents` dictionary
    current = dest
    path_color = Color(0, 0, 0)  # Black for the path
    path_size = 20  # Larger size for the path nodes
    while current is not None:
        # Style the current vertex
        gr.vertices[current].color = path_color
        gr.vertices[current].size = path_size

        # Style the edge from the parent to the current vertex
        parent = parents.get(current)
        if parent is not None:
            edge = gr.get_link_visualizer(parent, current)
            if edge:
                edge.color = path_color
                edge.thickness = 3
        current = parent

    # Highlight the path
    current = dest
    while current is not None:
        vertex = gr.get_vertex(current)
        vertex.opacity = 1.0  # Make visible
        vertex.color = Color("black")  # Highlight path vertices
        parent = parents[current]
        if parent is not None:
            edge = gr.get_link_visualizer(parent, current)
            if edge:
                edge.color = Color("black")  # Highlight path edges
                edge.opacity = 1.0
        current = parent

def main():
    # Set up Bridges
    bridges = Bridges(12, "eb1113", "1056063088544")
    bridges.set_title("Graph : OpenStreet Map Example")
    bridges.set_description("OpenStreet Map data for Charlotte downtown area, with shortest paths visualized.")

    # Load OSM data
    osm_data = data_source.get_osm_data(35.28, -80.8, 35.34, -80.7, "tertiary")  # Example region
    gr = osm_data.get_graph()
    gr.force_large_visualization(True)

    # Find and style the root of the graph
    root_lat = (osm_data.latitude_range[0] + osm_data.latitude_range[1]) / 2
    root_lon = (osm_data.longitude_range[0] + osm_data.longitude_range[1]) / 2
    root = getClosest(gr, root_lat, root_lon)
    style_root(gr, root)
    bridges.set_data_structure(gr)
    bridges.visualize()

    # Calculate shortest paths from the root
    distances, parents = shortestPath(gr, root)

    # Style vertices based on distances
    style_distance(gr, distances)
    bridges.set_data_structure(gr)
    bridges.visualize()

    # Find a destination and style the path
    dest_lat = root_lat + (osm_data.latitude_range[1] - osm_data.latitude_range[0]) / 4
    dest_lon = root_lon + (osm_data.longitude_range[1] - osm_data.longitude_range[0]) / 4
    dest = getClosest(gr, dest_lat, dest_lon)
    style_parent(gr, parents, dest)
    bridges.set_data_structure(gr)
    bridges.visualize()

if __name__ == "__main__":
    main()
