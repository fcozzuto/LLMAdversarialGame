def solve_cvrp(instance):
    # Instance structure:
    # instance = {
    #   'customers': [{'id': int, 'demand': float, 'x': float, 'y': float}, ...],
    #   'depot': {'id': int, 'x': float, 'y': float},
    #   'vehicle_capacity': float
    # }

    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']

    # Helper to compute Euclidean distance
    def distance(c1, c2):
        return ((c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2)**0.5

    # Create a mapping from customer id to customer object for quick lookup
    customer_map = {c['id']: c for c in customers}

    # Initialize unvisited customers
    unvisited = set(c['id'] for c in customers)

    routes = []

    # Build routes greedily, each starting and ending at the depot implicitly
    while unvisited:
        route = []
        load = 0.0
        current_node = depot
        while True:
            # Select the next customer to visit based on nearest neighbor heuristic
            nearest_customer_id = None
            nearest_dist = float('inf')
            for cid in unvisited:
                customer = customer_map[cid]
                dist = distance(current_node, customer)
                if load + customer['demand'] <= capacity and dist < nearest_dist:
                    nearest_dist = dist
                    nearest_customer_id = cid
            if nearest_customer_id is None:
                # No suitable next customer, end current route
                break
            # Add customer to route
            route.append(nearest_customer_id)
            load += customer_map[nearest_customer_id]['demand']
            current_node = customer_map[nearest_customer_id]
            unvisited.remove(nearest_customer_id)
        routes.append(route)

    # Improve routes with a simple local-repair: try to swap customers between routes if it reduces total distance
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_a = routes[i]
                route_b = routes[j]
                for a_idx, a_cid in enumerate(route_a):
                    for b_idx, b_cid in enumerate(route_b):
                        a_cust = customer_map[a_cid]
                        b_cust = customer_map[b_cid]
                        # Check if swapping does not violate capacity constraints
                        load_a = sum(customer_map[cid]['demand'] for cid in route_a)
                        load_b = sum(customer_map[cid]['demand'] for cid in route_b)
                        new_load_a = load_a - a_cust['demand'] + b_cust['demand']
                        new_load_b = load_b - b_cust['demand'] + a_cust['demand']
                        if new_load_a <= capacity and new_load_b <= capacity:
                            # Calculate current total distances
                            def route_distance(route):
                                total = 0.0
                                prev = depot
                                for cid in route:
                                    total += distance(prev, customer_map[cid])
                                    prev = customer_map[cid]
                                total += distance(prev, depot)
                                return total
                            current_total = route_distance(route_a) + route_distance(route_b)

                            # Swap customers
                            new_route_a = route_a[:]
                            new_route_b = route_b[:]
                            new_route_a[a_idx] = b_cid
                            new_route_b[b_idx] = a_cid
                            new_total = route_distance(new_route_a) + route_distance(new_route_b)

                            # If total distance is improved, commit the swap
                            if new_total < current_total:
                                routes[i] = new_route_a
                                routes[j] = new_route_b
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes

