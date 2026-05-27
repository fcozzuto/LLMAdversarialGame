def solve_cvrp(instance):
    # instance is a dictionary with keys:
    # 'depot': depot_id
    # 'demands': dict {customer_id: demand}
    # 'coordinates': dict {node_id: (x, y)}
    # 'vehicle_capacity': capacity
    #
    # Returns: list of routes (each route is list of customer_ids)

    depot = instance['depot']
    demands = instance['demands']
    coords = instance['coordinates']
    capacity = instance['vehicle_capacity']
    
    # Get list of customers (excluding depot)
    customers = [node for node in demands if node != depot]
    
    # Initialize unvisited customers
    unvisited = set(customers)
    
    # Precompute distances between all nodes for efficiency
    def distance(a, b):
        x1, y1 = coords[a]
        x2, y2 = coords[b]
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

    # Initialize list of routes
    routes = []

    # Build routes through a greedy, constructive approach
    while unvisited:
        route = []
        load = 0
        current_node = depot
        while True:
            # Find unvisited customers that can be served without exceeding capacity
            feasible_customers = [c for c in unvisited if demands[c] + load <= capacity]
            if not feasible_customers:
                break
            # Select the closest feasible customer
            next_customer = min(feasible_customers, key=lambda c: distance(current_node, c))
            # Append to route
            route.append(next_customer)
            load += demands[next_customer]
            unvisited.remove(next_customer)
            current_node = next_customer
        routes.append(route)

    # Improve routes with a local search: try to swap customers between routes to reduce total distance
    # Using a simple pairwise swap heuristic
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for idx_i in range(len(route_i)):
                    for idx_j in range(len(route_j)):
                        c1 = route_i[idx_i]
                        c2 = route_j[idx_j]
                        # Swap only if demands after swap remain feasible
                        load_i = sum(demands[c] for c in route_i) - demands[c1] + demands[c2]
                        load_j = sum(demands[c] for c in route_j) - demands[c2] + demands[c1]
                        if load_i <= capacity and load_j <= capacity:
                            # Compute current total distance
                            def route_distance(route):
                                dist = 0
                                prev = depot
                                for c in route:
                                    dist += distance(prev, c)
                                    prev = c
                                dist += distance(prev, depot)
                                return dist
                            current_dist = route_distance(route_i) + route_distance(route_j)
                            # Swap customers
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[idx_i], new_route_j[idx_j] = c2, c1
                            new_dist = route_distance(new_route_i) + route_distance(new_route_j)
                            if new_dist < current_dist:
                                # Accept swap
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

    # Return the routes (excluding depot)
    return routes

