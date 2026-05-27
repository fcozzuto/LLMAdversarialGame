def solve_cvrp(instance):
    # instance is expected to contain:
    # instance['depot']: index/id of depot
    # instance['coords']: dict {node_id: (x, y)} for all nodes including depot
    # instance['demand']: dict {node_id: demand} for all nodes except depot
    # instance['vehicle_capacity']: capacity of each vehicle
    # instance['customers']: list of customer ids (excluding depot)
    
    depot = instance['depot']
    coords = instance['coords']
    demand = instance['demand']
    capacity = instance['vehicle_capacity']
    customers = [n for n in coords if n != depot]
    
    # Step 1: Compute distance between all nodes
    def dist(a, b):
        x1, y1 = coords[a]
        x2, y2 = coords[b]
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    
    # Step 2: Sort customers by increasing distance from depot (a simple heuristic)
    sorted_customers = sorted(customers, key=lambda n: dist(depot, n))
    
    # Step 3: Construct routes greedily by proximity and capacity
    routes = []
    unserved = set(sorted_customers)
    
    while unserved:
        route = []
        load = 0
        current_node = depot
        # Build a route by adding the closest unserved customer that fits capacity
        while True:
            # Find candidates: unserved, fit in capacity
            candidates = [n for n in unserved if load + demand[n] <= capacity]
            if not candidates:
                break
            # Choose the closest candidate to current node
            next_customer = min(candidates, key=lambda n: dist(current_node, n))
            # Append to route
            route.append(next_customer)
            load += demand[next_customer]
            unserved.remove(next_customer)
            current_node = next_customer
        routes.append(route)
    
    # Optional Step 4: Improve routes using local search (swap adjacent customers if beneficial)
    for r_idx, route in enumerate(routes):
        # Try to improve route by swapping adjacent customers
        improved = True
        while improved:
            improved = False
            for i in range(len(route) - 1):
                # Calculate current total distance
                prev_node = depot if i == 0 else route[i - 1]
                curr_node = route[i]
                next_node = route[i + 1]
                after_node = depot if i + 2 == len(route) else route[i + 2]
                current_dist = dist(prev_node, curr_node) + dist(next_node, after_node)
                # Swap customers
                route[i], route[i + 1] = route[i + 1], route[i]
                new_prev_node = depot if i == 0 else route[i - 1]
                new_curr_node = route[i]
                new_next_node = route[i + 1]
                new_after_node = depot if i + 2 == len(route) else route[i + 2]
                new_dist = dist(new_prev_node, new_curr_node) + dist(new_next_node, new_after_node)
                # If no improvement, revert swap
                if new_dist >= current_dist:
                    route[i], route[i + 1] = route[i + 1], route[i]
                else:
                    improved = True
    
    # Final step: routes are lists of customers (not including depot)
    return routes

