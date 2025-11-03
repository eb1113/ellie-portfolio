import heapq

def dijkstra(graph, source_id):
    """Dijkstra's algorithm assuming all edges have weight 1.0."""
    adjacency_list = graph.get_adjacency_list()
    distances = {v_id: float('inf') for v_id in graph._vertices}
    parents = {v_id: None for v_id in graph._vertices}
    distances[source_id] = 0
    priority_queue = [(0, source_id)]
    visited = set()

    while priority_queue:
        current_distance, current_vertex_id = heapq.heappop(priority_queue)

        if current_distance > distances[current_vertex_id]:
            continue

        # Mark the current vertex as visited
        visited.add(current_vertex_id)

        slelement = adjacency_list[current_vertex_id]
        while slelement is not None:
            edge = slelement.value
            neighbor_id = edge.tov
            new_distance = current_distance + 1.0

            if new_distance < distances[neighbor_id]:
                distances[neighbor_id] = new_distance
                parents[neighbor_id] = current_vertex_id
                heapq.heappush(priority_queue, (new_distance, neighbor_id))

            slelement = slelement.next

    # Flag disconnected vertices
    disconnected_vertices = [v_id for v_id, dist in distances.items() if dist == float('inf')]

    # Return distances, parents, and disconnected vertices
    return distances, parents, disconnected_vertices
