def solve_cvrp(instance):
    """
    A deterministic, interpretable CVRP solver using a simple constructive and local improvement approach.
    """
    # Constants
    depot_id = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    n_customers = len(customers)

    # Initialize unvisited customers: list of (customer_id, demand, x, y)
    unvisited = []
    for cid, data in customers.items():
        demand = data['demand']
        unvisited.append( (cid, demand, data['x'], data['y']) )

    routes = []

    # Function to compute Euclidean distance
    def distance(c1, c2):
        return ((c1[2] - c2[2])**2 + (c1[3] - c2[3])**2)**0.5

    # Build initial routes: assign customers greedily to routes respecting capacity
    while unvisited:
        route = []
        load = 0
        current_loc = (depot_id, 0, instance['depot_x'], instance['depot_y'])  # starting at depot
        remaining_customers = unvisited[:]
        while remaining_customers:
            # Find nearest customer that fits into the load
            best_cust = None
            min_dist = float('inf')
            for cust in remaining_customers:
                if load + cust[1] <= vehicle_capacity:
                    dist = distance(current_loc, cust)
                    if dist < min_dist:
                        min_dist = dist
                        best_cust = cust
            if best_cust is None:
                # No fitting customer found, end route
                break
            # Assign customer to route
            route.append(best_cust[0])
            load += best_cust[1]
            current_loc = best_cust
            remaining_customers.remove(best_cust)
        # Remove assigned customers from unvisited
        for cid in route:
            unvisited = [c for c in unvisited if c[0] != cid]
        routes.append(route)

    # Local improvement: try to swap customers between routes to reduce total distance
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for ix in range(len(route_i)):
                    for jx in range(len(route_j)):
                        c_i = next(c for c in customers.values() if c['id'] == route_i[ix])
                        c_j = next(c for c in customers.values() if c['id'] == route_j[jx])
                        demand_i = c_i['demand']
                        demand_j = c_j['demand']
                        # Check capacity constraints after swap
                        load_i = sum(customers[c]['demand'] for c in route_i) - demand_i + demand_j
                        load_j = sum(customers[c]['demand'] for c in route_j) - demand_j + demand_i
                        if load_i <= vehicle_capacity and load_j <= vehicle_capacity:
                            # Compute current distances
                            def route_distance(route):
                                total_dist = 0.0
                                prev = (depot_id, 0, instance['depot_x'], instance['depot_y'])
                                for c_id in route:
                                    c_data = customers[c_id]
                                    c_node = (c_id, c_data['demand'], c_data['x'], c_data['y'])
                                    total_dist += distance(prev, c_node)
                                    prev = c_node
                                total_dist += distance(prev, (depot_id,0,instance['depot_x'],instance['depot_y']))
                                return total_dist
                            # Swap customers
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[ix] = route_j[jx]
                            new_route_j[jx] = route_i[ix]
                            old_dist = route_distance(route_i) + route_distance(route_j)
                            new_dist = route_distance(new_route_i) + route_distance(new_route_j)
                            # Accept swap if improvement
                            if new_dist < old_dist:
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes

