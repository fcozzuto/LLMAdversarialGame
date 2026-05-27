def solve_cvrp(instance):
    # Extract problem data
    # instance should be a dict with at least:
    # 'demands': list of demands per customer (indexing customers from 1),
    # 'locations': list of (x, y) coordinates for each customer and depot,
    # 'capacity': vehicle capacity,
    # 'depot': index of the depot (usually 0)
    
    demands = instance['demands']
    locations = instance['locations']
    capacity = instance['capacity']
    depot = instance['depot']
    
    # Determine customer list
    customers = [i for i in range(len(demands)) if i != depot]
    
    # Compute simple Euclidean distance function
    def distance(i, j):
        dx = locations[i][0] - locations[j][0]
        dy = locations[i][1] - locations[j][1]
        return (dx*dx + dy*dy) ** 0.5
    
    # Build initial routes: nearest neighbor heuristic
    unvisited = set(customers)
    routes = []
    
    while unvisited:
        route = []
        load = 0
        current_node = depot
        while True:
            # Find the closest unvisited customer that fits in capacity
            candidates = []
            for customer in unvisited:
                if load + demands[customer] <= capacity:
                    dist = distance(current_node, customer)
                    candidates.append( (dist, customer) )
            if not candidates:
                # No feasible next customer
                break
            candidates.sort(key=lambda x: x[0])
            next_customer = candidates[0][1]
            route.append(next_customer)
            load += demands[next_customer]
            unvisited.remove(next_customer)
            current_node = next_customer
        routes.append(route)
    
    # Repair step: try to merge small routes if capacity permits
    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                total_demand = sum(demands[cust] for cust in route_i + route_j)
                if total_demand <= capacity:
                    # Calculate insertion cost
                    # Try to merge route_j into route_i
                    merged = route_i + route_j
                    # No explicit ordering heuristic here, keep order as found
                    # Check if the merge reduces total distance
                    def route_distance(route):
                        total = 0
                        prev = depot
                        for cust in route:
                            total += distance(prev, cust)
                            prev = cust
                        total += distance(prev, depot)
                        return total
                    old_distance = route_distance(route_i) + route_distance(route_j)
                    new_distance = route_distance(merged)
                    if new_distance <= old_distance:
                        routes[i] = merged
                        routes.pop(j)
                        changed = True
                        break
            if changed:
                break
    
    # Local improvement: for each route, attempt intra-route swaps to reduce total distance
    def improve_route(route):
        improved = True
        while improved:
            improved = False
            for i in range(len(route)):
                for j in range(i+1, len(route)):
                    # Swap customers i and j
                    new_route = route[:]
                    new_route[i], new_route[j] = new_route[j], new_route[i]
                    # Check if the new route is better
                    def route_distance(r):
                        total = 0
                        prev = depot
                        for cust in r:
                            total += distance(prev, cust)
                            prev = cust
                        total += distance(prev, depot)
                        return total
                    if route_distance(new_route) < route_distance(route):
                        route = new_route
                        improved = True
            # Update route reference
        return route
    
    for idx in range(len(routes)):
        routes[idx] = improve_route(routes[idx])
    
    # Final output: list of customer routes
    return routes

