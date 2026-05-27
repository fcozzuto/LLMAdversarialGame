def solve_cvrp(instance):
    # instance is expected to be a dict with keys:
    # 'depot': depot id, 'capacity': vehicle capacity,
    # 'demands': dict {node_id: demand},
    # 'distances': dict {(node1, node2): distance}
    depot = instance['depot']
    capacity = instance['capacity']
    demands = instance['demands']
    distances = instance['distances']

    # Identify customer nodes (excluding depot)
    customers = [node for node in demands if node != depot]

    # Initialize variables
    unvisited = set(customers)
    routes = []

    while unvisited:
        route = []
        load = 0
        current_node = depot

        # Build a route greedily
        while True:
            # Find the nearest unvisited customer that fits in remaining capacity
            candidates = []
            for node in unvisited:
                demand = demands[node]
                if load + demand <= capacity:
                    # Compute distance from current node to candidate
                    dist = distances.get((current_node, node), distances.get((node, current_node), float('inf')))
                    candidates.append((dist, node))
            if not candidates:
                # No suitable next customer
                break
            # Choose the nearest neighbor
            candidates.sort(key=lambda x: x[0])
            nearest_node = candidates[0][1]

            # Assign customer to route
            route.append(nearest_node)
            unvisited.remove(nearest_node)
            load += demands[nearest_node]
            current_node = nearest_node

        routes.append(route)

    return routes

