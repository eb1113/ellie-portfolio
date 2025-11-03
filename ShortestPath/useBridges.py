from bridges.bridges import Bridges
from bridges.data_src_dependent import data_source
from Dijkstra import dijkstra
from A_Star import a_star
from bridges.color import Color
import math
import random

def main():
        bridges = Bridges(10, "eb1113", "1056063088544")
        bridges.set_title("Shortest Path Visualization")
        city = "San Jose, California"
        type = "primary"

        osm_data = data_source.get_osm_data(city, type)
        # osm_data = data_source.get_osm_data(40.700, -111.900, 40.760, -111.800, "tertiary"); 
        graph = osm_data.get_graph()
        graph.force_large_visualization(True)

        if not graph._vertices:
            print("No vertices found in the OSM data.")
            return

        center_lat, center_lon = calculate_center(graph)
        closest_vertex_id = find_closest_vertex(graph, center_lat, center_lon)

        if closest_vertex_id is None:
            print("No closest vertex found.")
            return

        source_vertex = graph._vertices[closest_vertex_id]

        # Run Dijkstra's algorithm OS
        print("Running Dijkstra's Algorithm...")
        reset_colors(graph)
        distances_dijkstra, parents_dijkstra, notconnect_dijkstra = dijkstra(graph, closest_vertex_id)
        apply_distance_coloring(graph, distances_dijkstra)

        source_vertex.color = Color(255, 0, 0)  # Bright red

        bridges.set_title(f"{city, type}Dijkstra OS")
        bridges.set_data_structure(graph)
        bridges.visualize()
        reset_colors(graph)


        # Run Dijkstra's algorithm SS
        random_vertex_id = random.choice(list(graph._vertices.keys()))
        print(f"Highlighting shortest path to random vertex using Dijkstra...")
        shortest_path_dijkstra = get_shortest_path(parents_dijkstra, random_vertex_id)
        if shortest_path_dijkstra:
            highlight_path(graph, shortest_path_dijkstra, Color(0, 255, 163))
            bridges.set_title(f"{city, type}Dijkstra path visual ")
            source_vertex.color = Color(255, 0, 0)
            bridges.set_data_structure(graph)
            bridges.visualize()

        print("Running A* Algorithm...")
        reset_colors(graph)
        distances_astar, parents_astar = a_star(graph, closest_vertex_id)
        apply_distance_coloring(graph, distances_astar)

        # Visualize the map with A* coloring
        bridges.set_title(f"{city, type}A* full")
        source_vertex.color = Color(255, 0, 0)
        bridges.set_data_structure(graph)
        bridges.visualize()
        random_goal_id = random.choice(list(graph._vertices.keys()))

        print("Highlighting shortest path to random goal vertex using A*...")
        shortest_path_astar = get_shortest_path(parents_astar, random_goal_id)
        if shortest_path_astar:
            highlight_path(graph, shortest_path_astar, Color(0, 255, 163))
            bridges.set_title(f"{city, type}A* path")
            source_vertex.color = Color(255, 0, 0)
            bridges.set_data_structure(graph)
            bridges.visualize()





def get_shortest_path(parents, target_id):
    """Reconstruct the shortest path from the source to the target vertex."""
    path = []
    current_id = target_id
    while current_id is not None:
        path.append(current_id)
        current_id = parents.get(current_id)
    return path[::-1] if path else None
def calculate_center(graph):
    """Calculate the latitude and longitude of the map center."""
    latitudes = [v.value.latitude for v in graph._vertices.values()]
    longitudes = [v.value.longitude for v in graph._vertices.values()]
    return sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points."""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def find_closest_vertex(graph, center_lat, center_lon):
    """Find the closest vertex to the given latitude and longitude."""
    return min(graph._vertices,
               key=lambda v_id: haversine(center_lat, center_lon,
                                         graph._vertices[v_id].value.latitude,
                                         graph._vertices[v_id].value.longitude))

def apply_distance_coloring(graph, distances):
    """Color reachable vertices based on distances and hide unreachable ones."""
    # Get valid distances and avoid those that are unreachable (infinity)
    valid_distances = {k: v for k, v in distances.items() if not math.isnan(v) and v != float('inf')}

    if not valid_distances:
        print("No valid distances found.")
        return

    # Find max and min distance for coloring
    min_distance = min(valid_distances.values())
    max_distance = max(valid_distances.values())

    for v_id, dist in distances.items():
        if v_id not in valid_distances:
            continue

        # Normalize distance to interpolate between two colors
        normalized_dist = (dist - min_distance) / (max_distance - min_distance) if max_distance > min_distance else 0

        # teal for close and navy for far
        red = int(0 + (13 - 0) * normalized_dist)
        green = int(255 - (255 - 34) * normalized_dist)
        blue = int(163 - (163 - 67) * normalized_dist)

        graph._vertices[v_id].color = Color(red, green, blue)


def highlight_path(graph, path, color=Color(0, 255, 163)):
    """Highlight only the vertices and edges in the path, leave others unaffected."""
    for v_id in graph._vertices:
        graph._vertices[v_id].color = Color(13, 34, 67)
    for v_id in graph._vertices:
        slelement = graph.get_adjacency_list()[v_id]
        while slelement is not None:
            edge = slelement.value
            edge.color = Color(0,0,0)
            slelement = slelement.next

    # color the path vertices and edges
    for v_id in path:
        graph._vertices[v_id].color = color
    for i in range(len(path) - 1):
        edge = graph.get_link_visualizer(path[i], path[i + 1])
        if edge:
            edge.color = color


def reset_colors(graph):
    """Reset the color of all vertices and edges to default."""
    for v_id in graph._vertices:
        graph._vertices[v_id].color = Color(255,255,255)

    for v_id in graph._vertices:
        slelement = graph.get_adjacency_list()[v_id]
        while slelement is not None:
            edge = slelement.value
            edge.color = Color(255,255,255)
            slelement = slelement.next



if __name__ == "__main__":
    main()