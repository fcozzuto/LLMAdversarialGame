def solve_cvrp(instance):
    """
    Solves a Capacitated Vehicle Routing Problem (CVRP) instance using a deterministic,
    interpretable heuristic. Builds routes by sequentially assigning customers based on
    nearest feasible nodes, then refines routes with simple local improvements.

    Parameters:
        instance: dict with keys:
            'customers': list of dicts, each with 'id', 'x', 'y', 'demand'
            'depot': dict with 'id', 'x', 'y'
            'vehicle_capacity': int

    Returns:
        routes: list of routes, each route being a list of customer IDs
    """

    # Extract data
    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']

    # Create list of customers with positions and demands
    customer_list = customers[:]
    # Map for quick access
    customer_map = {c['id']: c for c in customer_list}

    # Initialize set of unvisited customers
    unvisited = set(c['id'] for c in customer_list)

    # Helper function for Euclidean distance
    def dist(a, b):
        return ((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2) ** 0.5

    # Build initial routes: nearest feasible insertion
    routes = []

    while unvisited:
        route = []
        load = 0
        current_node = depot
        # While there are customers left
        while True:
            # Find nearest feasible customer to current_node
            candidates = []
            for cust_id in unvisited:
                cust = customer_map[cust_id]
                if load + cust['demand'] <= capacity:
                    candidates.append(cust)
            if not candidates:
                break  # No more feasible customers to add in this route

            # Select nearest customer
            next_customer = min(candidates, key=lambda c: dist(current_node, c))
            # Add to route
            route.append(next_customer['id'])
            load += next_customer['demand']
            unvisited.remove(next_customer['id'])
            current_node = next_customer

        routes.append(route)

    # Simple local improvement: try to swap customers between routes
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for idx_i in range(len(route_i)):
                    for idx_j in range(len(route_j)):
                        cust_id_i = route_i[idx_i]
                        cust_id_j = route_j[idx_j]
                        cust_i = customer_map[cust_id_i]
                        cust_j = customer_map[cust_id_j]

                        # Check capacity constraints after swap
                        load_i = sum(customer_map[cid]['demand'] for cid in route_i)
                        load_j = sum(customer_map[cid]['demand'] for cid in route_j)

                        new_load_i = load_i - cust_i['demand'] + cust_j['demand']
                        new_load_j = load_j - cust_j['demand'] + cust_i['demand']

                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Perform swap
                            route_i[idx_i], route_j[idx_j] = cust_id_j, cust_id_i
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes

