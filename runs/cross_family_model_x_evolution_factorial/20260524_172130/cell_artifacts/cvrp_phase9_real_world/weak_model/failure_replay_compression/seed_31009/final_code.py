def solve_cvrp(instance):
    # instance expected: dict with keys:
    # 'customers': list of dicts with 'id', 'demand', 'x', 'y'
    # 'vehicle_capacity': int
    # 'depot': dict with 'id', 'x', 'y'
    
    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customer dicts for easier access
    customer_list = customers[:]
    
    # Initialize list of unvisited customers
    unvisited = {cust['id']: cust for cust in customer_list}
    
    # Helper function to compute Euclidean distance
    def dist(c1, c2):
        dx = c1['x'] - c2['x']
        dy = c1['y'] - c2['y']
        return (dx*dx + dy*dy)**0.5
    
    # Initialize routes list
    routes = []
    
    # Main constructive heuristic: deposit-closest insertion
    while unvisited:
        # Start a new route from depot
        route = []
        load = 0
        current_node = depot
        
        # Greedy insertion of closest customers
        while True:
            # Find the nearest customer that fits in capacity
            candidates = []
            for cust_id, cust in unvisited.items():
                if load + cust['demand'] <= capacity:
                    candidates.append(cust)
            if not candidates:
                break
            # Select the closest candidate
            next_cust = min(candidates, key=lambda c: dist(current_node, c))
            # Append customer to route
            route.append(next_cust['id'])
            load += next_cust['demand']
            current_node = next_cust
            # Remove from unvisited
            del unvisited[next_cust['id']]
        routes.append(route)
    
    # Heuristic improvement: local swap between routes to reduce total distance
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Try swapping one customer from route_i with one from route_j
                for idx_i, cust_id_i in enumerate(route_i):
                    cust_i = next(c for c in customer_list if c['id'] == cust_id_i)
                    for idx_j, cust_id_j in enumerate(route_j):
                        cust_j = next(c for c in customer_list if c['id'] == cust_id_j)
                        # Check capacity constraints
                        load_i = sum(next(c for c in customer_list if c['id'] == cid)['demand'] for cid in route_i)
                        load_j = sum(next(c for c in customer_list if c['id'] == cid)['demand'] for cid in route_j)
                        new_load_i = load_i - cust_i['demand'] + cust_j['demand']
                        new_load_j = load_j - cust_j['demand'] + cust_i['demand']
                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Compute current total distance
                            def route_distance(route):
                                total = 0.0
                                prev = depot
                                for cid in route:
                                    cnode = next(c for c in customer_list if c['id'] == cid)
                                    total += dist(prev, cnode)
                                    prev = cnode
                                total += dist(prev, depot)
                                return total
                            current_total = route_distance(route_i) + route_distance(route_j)
                            # Swap customers
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[idx_i] = cust_id_j
                            new_route_j[idx_j] = cust_id_i
                            new_total = route_distance(new_route_i) + route_distance(new_route_j)
                            if new_total < current_total:
                                # Accept swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
    return routes

