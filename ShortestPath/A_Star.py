from heapq import heappop, heappush
import math

def hueristic(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points."""
    R = 6371  # Earth's radius in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def a_star(graph, source_id):
    """A* algorithm for shortest paths to every vertex."""
    # Initialize distances and priority queue
    distances = {v_id: float('inf') for v_id in graph._vertices}
    parents = {v_id: None for v_id in graph._vertices}
    distances[source_id] = 0
    priority_queue = [(0, source_id)]

    # Process each vertex in the graph
    adjacency_list = graph.get_adjacency_list()

    while priority_queue:
        current_f_score, current_vertex_id = heappop(priority_queue)

        # Get neighbors
        neighbors = []
        slelement = adjacency_list[current_vertex_id]
        while slelement is not None:
            neighbors.append(slelement.value)
            slelement = slelement.next

        # Process neighbors
        for edge in neighbors:
            neighbor_id = edge.tov

            # Current coordinates
            neighbor_lat = graph._vertices[neighbor_id].value.latitude
            neighbor_lon = graph._vertices[neighbor_id].value.longitude


            g_score = distances[current_vertex_id] + 1


            h_score = hueristic(neighbor_lat, neighbor_lon, graph._vertices[source_id].value.latitude, graph._vertices[source_id].value.longitude)

            # f_score: Total cost estimate
            f_score = g_score + h_score

            if g_score < distances[neighbor_id]:
                distances[neighbor_id] = g_score
                parents[neighbor_id] = current_vertex_id
                heappush(priority_queue, (f_score, neighbor_id))

    return distances, parents
