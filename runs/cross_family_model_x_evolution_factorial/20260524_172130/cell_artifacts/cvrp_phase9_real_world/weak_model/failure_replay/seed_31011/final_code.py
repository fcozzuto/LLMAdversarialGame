def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) using a deterministic, interpretable approach.
    Returns a list of routes, each route is a list of customer ids (excluding depot), covering all customers exactly once.
    """
    # Extract data from instance
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create a dict for easy access
    customer_dict = {c['id']: c for c in customers}
    
    # Precompute distance matrix (assuming Euclidean)
    def dist(a, b):
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        return (dx*dx + dy*dy) ** 0.5
    
    nodes = [depot] + customers
    n = len(nodes)
    distance_matrix = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            distance_matrix[i][j] = dist(nodes[i], nodes[j])
    
    # Map customer id to index in nodes list
    id_to_index = {node['id']: idx for idx, node in enumerate(nodes)}
    index_to_id = {idx: node['id'] for idx, node in enumerate(nodes)}
    
    # Initialize unvisited customers set
    unvisited = set(c['id'] for c in customers)
    
    # Initialize routes list
    routes = []
    
    # Greedy construction: build routes until all customers are assigned
    while unvisited:
        route = []
        load = 0
        current_node_idx = 0  # start at depot index
        route_capacity = capacity
        while True:
            # Select next customer based on closest distance
            candidates = []
            for cid in unvisited:
                c_idx = id_to_index[cid]
                if c_idx == 0:
                    continue
                demand = customer_dict[cid]['demand']
                if demand <= route_capacity - load:
                    candidates.append((distance_matrix[current_node_idx][c_idx], cid))
            if not candidates:
                # No feasible next customer, end current route
                break
            # Select the closest feasible customer
            candidates.sort(key=lambda x: x[0])
            next_cid = candidates[0][1]
            # Add customer to route
            route.append(next_cid)
            load += customer_dict[next_cid]['demand']
            unvisited.remove(next_cid)
            current_node_idx = id_to_index[next_cid]
        # Append the constructed route
        routes.append(route)
    
    # Improve routes with local reordering (2-opt-like)
    for _ in range(2):  # perform a few local improvements
        for r_idx, route in enumerate(routes):
            improved = True
            while improved:
                improved = False
                for i in range(1, len(route) - 1):
                    for j in range(i + 1, len(route)):
                        # Reverse segment between i and j
                        new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
                        # Check capacity constraint
                        total_demand = sum(customer_dict[cid]['demand'] for cid in new_route)
                        if total_demand <= capacity:
                            # Calculate total route distance
                            def route_distance(r):
                                total = 0.0
                                prev_idx = 0  # start at depot
                                for cid in r:
                                    c_idx = id_to_index[cid]
                                    total += distance_matrix[prev_idx][c_idx]
                                    prev_idx = c_idx
                                total += distance_matrix[prev_idx][0]  # return to depot
                                return total
                            current_distance = route_distance(route)
                            new_distance = route_distance(new_route)
                            if new_distance < current_distance:
                                route = new_route
                                routes[r_idx] = route
                                improved = True
    return routes

