def solve_cvrp(instance):
    # instance is assumed to have:
    # 'customers': list of customer dicts with keys: 'id', 'demand', 'x', 'y'
    # 'depot': dict with keys: 'id', 'x', 'y'
    # 'vehicle_capacity': int
    # We interpret:
    # customers: list of customers
    # depot: a single depot node
    # vehicle_capacity: maximum capacity per vehicle

    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']

    # Initialize customer list sorted by id for consistency
    customer_list = sorted(customers, key=lambda c: c['id'])

    # Compute pairwise distances for deterministic selection
    def distance(a, b):
        return ((a['x'] - b['x'])**2 + (a['y'] - b['y'])**2)**0.5

    # Build a lookup for customers by id
    customer_dict = {c['id']: c for c in customer_list}

    # Initialize unserved customers set
    unserved = set(c['id'] for c in customer_list)

    routes = []

    # Main constructive phase:
    # Build routes greedily by selecting nearest unserved customers
    while unserved:
        route = []
        load = 0
        current_node = depot
        while True:
            # Filter customers that can be served without exceeding capacity
            candidates = [cid for cid in unserved if customer_dict[cid]['demand'] + load <= capacity]
            if not candidates:
                break
            # Select the nearest candidate to current node
            next_cid = min(candidates, key=lambda cid: distance(current_node, customer_dict[cid]))
            # Append to route
            route.append(next_cid)
            load += customer_dict[next_cid]['demand']
            current_node = customer_dict[next_cid]
            unserved.remove(next_cid)
        routes.append(route)

    # Local improvement: attempt to optimize routes by relocating customers between routes
    improved = True
    while improved:
        improved = False
        # Try all pairs of routes
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                route_i = routes[i]
                route_j = routes[j]
                # Try moving each customer from route_i to route_j
                for k, cust_id in enumerate(route_i):
                    cust_demand = customer_dict[cust_id]['demand']
                    # Check capacity constraint for route_j
                    load_j = sum(customer_dict[c]['demand'] for c in route_j)
                    if load_j + cust_demand <= capacity:
                        # Compute cost before move
                        def route_cost(route):
                            total = 0
                            prev_node = depot
                            for cid in route:
                                total += distance(prev_node, customer_dict[cid])
                                prev_node = customer_dict[cid]
                            total += distance(prev_node, depot)
                            return total
                        old_cost = route_cost(route_i) + route_cost(route_j)
                        # Create new routes with moved customer
                        new_route_i = route_i[:k] + route_i[k+1:]
                        new_route_j = route_j + [cust_id]
                        new_cost = route_cost(new_route_i) + route_cost(new_route_j)
                        if new_cost < old_cost:
                            # Make move
                            routes[i] = new_route_i
                            routes[j] = new_route_j
                            improved = True
                            break
                if improved:
                    break
            if improved:
                break

    # Remove empty routes if any
    routes = [r for r in routes if r]

    return routes

