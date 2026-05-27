def solve_cvrp(instance):
    # instance: dict with keys:
    # 'demands': list of demands for each customer (indexes correspond to customer IDs starting at 1),
    # 'coords': list of (x, y) for depot at index 0 and customers at 1..n,
    # 'vehicle_capacity': integer
    
    demands = instance['demands']
    coords = instance['coords']
    capacity = instance['vehicle_capacity']
    
    # Number of customers
    n_customers = len(demands)
    
    # Generate a simple distance function (Manhattan distance)
    def distance(i, j):
        x1, y1 = coords[i]
        x2, y2 = coords[j]
        return abs(x1 - x2) + abs(y1 - y2)
    
    # Initialize unvisited customers
    unvisited = set(range(1, n_customers + 1))
    
    routes = []
    depot_index = 0
    
    # Construct initial routes using a greedy sequential approach
    while unvisited:
        route = []
        load = 0
        current_node = depot_index
        while True:
            # Select the nearest unvisited customer that fits the capacity
            candidate = None
            min_dist = float('inf')
            for customer in unvisited:
                demand = demands[customer - 1]
                if load + demand <= capacity:
                    d = distance(current_node, customer)
                    if d < min_dist:
                        min_dist = d
                        candidate = customer
            if candidate is None:
                # No feasible next customer, return to depot
                break
            # Add customer to route
            route.append(candidate)
            load += demands[candidate - 1]
            unvisited.remove(candidate)
            current_node = candidate
        routes.append(route)
    
    # Improve routes locally by trying to swap customers between routes if it reduces total distance
    # and maintains capacity constraints
    def total_distance(routes):
        total = 0
        for route in routes:
            prev = depot_index
            for customer in route:
                total += distance(prev, customer)
                prev = customer
            total += distance(prev, depot_index)
        return total
    
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Try swapping each customer pair between routes
                for ci in range(len(route_i)):
                    for cj in range(len(route_j)):
                        c1 = route_i[ci]
                        c2 = route_j[cj]
                        # Check capacity constraints after swapping
                        load_i = sum(demands[cust -1] for cust in route_i) - demands[c1 -1] + demands[c2 -1]
                        load_j = sum(demands[cust -1] for cust in route_j) - demands[c2 -1] + demands[c1 -1]
                        if load_i <= capacity and load_j <= capacity:
                            # Compute current distances
                            def route_distance(route):
                                dist = 0
                                prev_node = depot_index
                                for cust in route:
                                    dist += distance(prev_node, cust)
                                    prev_node = cust
                                dist += distance(prev_node, depot_index)
                                return dist
                            current_dist = route_distance(route_i) + route_distance(route_j)
                            # Swap customers
                            new_route_i = route_i.copy()
                            new_route_j = route_j.copy()
                            new_route_i[ci] = c2
                            new_route_j[cj] = c1
                            new_dist = route_distance(new_route_i) + route_distance(new_route_j)
                            if new_dist < current_dist:
                                # Accept swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
        # Continue until no improvement
    
    return routes

