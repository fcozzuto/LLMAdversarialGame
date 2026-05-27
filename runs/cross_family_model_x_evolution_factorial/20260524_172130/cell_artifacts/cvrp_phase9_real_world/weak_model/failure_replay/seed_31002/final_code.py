def solve_cvrp(instance):
    # instance is assumed to be a dict with:
    # - 'depot': int, representing the depot node id
    # - 'customers': list of dicts, each with 'id' and 'demand'
    # - 'distance': function(d1, d2) returning distance between two nodes
    # - 'vehicle_capacity': int

    depot = instance['depot']
    customers = instance['customers']
    distance = instance['distance']
    capacity = instance['vehicle_capacity']

    # Map customer ids to demands for easy access
    customer_demands = {c['id']: c['demand'] for c in customers}

    # Create a list of customer ids for processing
    unvisited = set(c['id'] for c in customers)

    routes = []

    # Build routes iteratively by selecting a seed customer and greedily adding nearest feasible customers
    while unvisited:
        # Select a seed customer: the unvisited customer with the smallest demand
        seed_id = min(unvisited, key=lambda cid: customer_demands[cid])
        route = []
        load = 0
        current_node = depot

        # Start route with seed customer
        demand = customer_demands[seed_id]
        if demand > capacity:
            # Customer demand exceeds vehicle capacity, cannot serve this customer
            # Fail fast: skipping this customer (or could raise error)
            # For this implementation, assume all demands are feasible
            unvisited.remove(seed_id)
            continue
        route.append(seed_id)
        unvisited.remove(seed_id)
        load += demand
        current_node = seed_id

        # Greedily add nearest feasible customers
        while True:
            feasible_neighbors = []
            for cid in unvisited:
                d = customer_demands[cid]
                if load + d <= capacity:
                    feasible_neighbors.append(cid)
            if not feasible_neighbors:
                break
            # Pick the nearest feasible customer
            next_cid = min(feasible_neighbors, key=lambda cid: distance(current_node, cid))
            route.append(next_cid)
            load += customer_demands[next_cid]
            unvisited.remove(next_cid)
            current_node = next_cid

        routes.append(route)

    return routes

