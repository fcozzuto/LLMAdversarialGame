def solve_cvrp(instance):
    """
    Solves the Capacitated Vehicle Routing Problem (CVRP) using a deterministic,
    interpretable approach with constructive, repair, and local-search strategies.
    """
    # Extract data from instance
    depot = instance['depot']
    customers = instance['customers']  # List of dicts with 'id', 'x', 'y', 'demand'
    vehicle_capacity = instance['vehicle_capacity']

    # Prepare list of customers with relevant info
    customer_list = customers.copy()
    # Track customers not yet assigned
    unassigned = {c['id']: c for c in customer_list}

    # Helper functions
    def distance(c1, c2):
        return ((c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2)**0.5

    # Compute distance matrix for all customers and depot
    all_points = [depot] + customer_list
    dist_matrix = {}
    for c1 in all_points:
        for c2 in all_points:
            dist_matrix[(c1['id'], c2['id'])] = distance(c1, c2)

    # Build initial routes: start from depot and greedily add closest feasible customer
    routes = []
    while unassigned:
        route = []
        load = 0
        current_node = depot
        # Continue adding customers to the route
        while True:
            # Find nearest feasible customer
            feasible_customers = [c for c in unassigned.values()
                                  if load + c['demand'] <= vehicle_capacity]
            if not feasible_customers:
                break
            # Select the closest customer
            next_customer = min(feasible_customers,
                                key=lambda c: dist_matrix[(current_node['id'], c['id'])])
            # Add customer to route
            route.append(next_customer['id'])
            load += next_customer['demand']
            current_node = next_customer
            # Remove from unassigned
            del unassigned[next_customer['id']]
        # Save the route
        routes.append(route)

    # Repair step: try to improve by reassigning customers to reduce total distance
    # For simplicity, perform a single pass of reassignments
    def total_distance(routes):
        total = 0
        for r in routes:
            prev = depot
            for c_id in r:
                total += dist_matrix[(prev['id'], c_id)]
                prev = next(c for c in customer_list if c['id'] == c_id)
            total += dist_matrix[(prev['id'], depot['id'])]
        return total

    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Attempt to swap a customer from route_i with one from route_j
                for ci in range(len(route_i)):
                    c_id_i = route_i[ci]
                    c_i = next(c for c in customer_list if c['id'] == c_id_i)
                    for cj in range(len(route_j)):
                        c_id_j = route_j[cj]
                        c_j = next(c for c in customer_list if c['id'] == c_id_j)
                        # Check capacity constraints if swapped
                        load_i = sum(next(c for c in customer_list if c['id']==cid)['demand'] for cid in route_i) - c_i['demand'] + c_j['demand']
                        load_j = sum(next(c for c in customer_list if c['id']==cid)['demand'] for cid in route_j) - c_j['demand'] + c_i['demand']
                        if load_i <= vehicle_capacity and load_j <= vehicle_capacity:
                            # Compute new total distance if swapped
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[ci] = c_id_j
                            new_route_j[cj] = c_id_i
                            new_routes = routes[:]
                            new_routes[i] = new_route_i
                            new_routes[j] = new_route_j
                            if total_distance(new_routes) < total_distance(routes):
                                routes = new_routes
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes

