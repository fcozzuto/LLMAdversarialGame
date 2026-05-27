def solve_cvrp(instance):
    # Assumed instance dict structure:
    # instance = {
    #   'depot': int,
    #   'customers': {
    #       customer_id: {
    #           'demand': int,
    #           'x': float,
    #           'y': float
    #       }
    #   },
    #   'vehicle_capacity': int
    # }
    
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Helper: get list of customer ids
    customer_ids = list(customers.keys())
    
    # Step 1: Compute a simple distance function
    def dist(c1, c2):
        dx = customers[c1]['x'] - customers[c2]['x']
        dy = customers[c1]['y'] - customers[c2]['y']
        return (dx*dx + dy*dy)**0.5
    
    # Step 2: Sort customers by their distance to depot (deterministic initial ordering)
    customers_sorted = sorted(customer_ids, key=lambda cid: dist(depot, cid))
    
    routes = []
    
    # Step 3: Construct initial routes greedily based on nearest neighbor, respecting capacity
    unvisited = set(customers_sorted)
    while unvisited:
        route = []
        load = 0
        current_location = depot
        # Keep adding nearest feasible customer
        while True:
            # Find feasible candidates
            candidates = [cid for cid in unvisited if load + customers[cid]['demand'] <= capacity]
            if not candidates:
                break
            # Select the nearest candidate
            next_cust = min(candidates, key=lambda cid: dist(current_location, cid))
            # Add to route
            route.append(next_cust)
            load += customers[next_cust]['demand']
            unvisited.remove(next_cust)
            current_location = next_cust
        routes.append(route)
    
    # Step 4: Improvement - local swapping of customers between routes
    # Repeat a fixed number of local improvements (e.g., one pass)
    improved = True
    iteration = 0
    max_iterations = 1  # deterministic, so limit to 1 pass
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        # Check all pairs of routes for possible swaps
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for idx_i in range(len(route_i)):
                    for idx_j in range(len(route_j)):
                        c1 = route_i[idx_i]
                        c2 = route_j[idx_j]
                        # Compute load after swap
                        load_i = sum(customers[c]['demand'] for c in route_i)
                        load_j = sum(customers[c]['demand'] for c in route_j)
                        demand_c1 = customers[c1]['demand']
                        demand_c2 = customers[c2]['demand']
                        new_load_i = load_i - demand_c1 + demand_c2
                        new_load_j = load_j - demand_c2 + demand_c1
                        # Check capacity constraints
                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Compute total route lengths before swap
                            def route_length(route):
                                length = 0.0
                                prev = depot
                                for c in route:
                                    length += dist(prev, c)
                                    prev = c
                                length += dist(prev, depot)
                                return length
                            old_length = route_length(route_i) + route_length(route_j)
                            # Swap customers
                            route_i[idx_i], route_j[idx_j] = route_j[idx_j], route_i[idx_i]
                            new_length = route_length(route_i) + route_length(route_j)
                            # Accept swap if improved
                            if new_length < old_length:
                                improved = True
                            else:
                                # revert swap
                                route_i[idx_i], route_j[idx_j] = c1, c2
    # Final routes: exclude depot, list customer IDs
    return routes

