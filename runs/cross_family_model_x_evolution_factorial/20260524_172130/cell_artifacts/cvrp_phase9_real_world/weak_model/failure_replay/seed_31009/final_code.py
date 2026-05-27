def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) using a deterministic, interpretable approach,
    combining constructive, repair, and local search techniques with failure replay.

    Args:
        instance (dict): Contains 'depot', 'customers', 'vehicle_capacity', and 'distances'.
            - 'depot': int, id of the depot node.
            - 'customers': list of dicts, each with 'id', 'demand'.
            - 'vehicle_capacity': float or int, capacity of each vehicle.
            - 'distances': dict of dicts, distances[a][b] = distance between node a and b.

    Returns:
        list of lists: Routes, each route is a list of customer ids (excluding depot).
    """
    # Extract data
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    distances = instance['distances']

    # Create list of customer ids and demands
    customer_ids = [c['id'] for c in customers]
    demands = {c['id']: c['demand'] for c in customers}

    # Initialize list to hold routes
    routes = []

    # Keep track of unvisited customers
    unvisited = set(customer_ids)

    # Construct initial feasible routes (Constructive phase)
    # While there are unvisited customers, build a route greedily
    while unvisited:
        route = []
        load = 0
        current_node = depot
        # Create a list of unvisited customers sorted by distance from current_node
        remaining_customers = list(unvisited)
        remaining_customers.sort(key=lambda c: distances[current_node][c])

        for customer in remaining_customers:
            demand = demands[customer]
            if load + demand <= capacity:
                # Add customer to current route
                route.append(customer)
                load += demand
                unvisited.remove(customer)
                current_node = customer
            else:
                # Cannot add more customers to this route
                continue
        # Append the constructed route
        routes.append(route)

    # Repair phase: try to improve routes via customer swapping (Local search)
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route1 = routes[i]
                route2 = routes[j]
                for c1_idx in range(len(route1)):
                    for c2_idx in range(len(route2)):
                        c1 = route1[c1_idx]
                        c2 = route2[c2_idx]
                        demand_c1 = demands[c1]
                        demand_c2 = demands[c2]
                        # Check capacity feasibility for swap
                        load1 = sum(demands[c] for c in route1)
                        load2 = sum(demands[c] for c in route2)
                        if (load1 - demand_c1 + demand_c2 <= capacity and
                            load2 - demand_c2 + demand_c1 <= capacity):
                            # Swap customers
                            route1[c1_idx], route2[c2_idx] = route2[c2_idx], route1[c1_idx]
                            improved = True
        # Continue loop if any swap improved solution

    # Local optimization: try to reoptimize each route internally
    def optimize_route(route):
        # Use a greedy reordering to minimize total distance within route
        if len(route) <= 1:
            return route
        optimized = False
        nodes = route[:]
        # Attempt to reorder route to reduce total travel distance
        improved_distance = compute_route_distance([depot] + nodes + [depot])
        improved_route = nodes[:]
        # Simple heuristic: try swapping pairs
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                new_nodes = nodes[:]
                new_nodes[i], new_nodes[j] = new_nodes[j], new_nodes[i]
                dist = compute_route_distance([depot] + new_nodes + [depot])
                if dist < improved_distance:
                    improved_distance = dist
                    optimized = True
                    optimized_route = new_nodes
        return optimized_route if optimized else route

    def compute_route_distance(route_nodes):
        distance = 0
        for k in range(len(route_nodes) - 1):
            distance += distances[route_nodes[k]][route_nodes[k + 1]]
        return distance

    # Apply internal route optimization
    for idx in range(len(routes)):
        routes[idx] = optimize_route(routes[idx])

    # Final route list without depot nodes
    return routes

