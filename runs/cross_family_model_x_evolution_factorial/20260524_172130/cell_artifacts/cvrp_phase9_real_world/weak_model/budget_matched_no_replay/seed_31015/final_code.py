def solve_cvrp(instance):
    # instance is assumed to be a dict with keys:
    # 'customers': list of customer dicts with 'id', 'demand' and 'coords'
    # 'depot': customer dict with 'id', 'demand', 'coords'
    # 'vehicle_capacity': int
    # The output is a list of routes; each route is a list of customer ids (excluding depot)

    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']

    # Create a list of customer objects with id, demand, and distance for convenience
    customer_list = [c for c in customers]
    unvisited = set(c['id'] for c in customer_list)
    customer_dict = {c['id']: c for c in customer_list}

    # Helper function to compute Euclidean distance
    def dist(c1, c2):
        dx = c1['coords'][0] - c2['coords'][0]
        dy = c1['coords'][1] - c2['coords'][1]
        return (dx*dx + dy*dy) ** 0.5

    routes = []

    # Main loop: build routes until all customers are visited
    while unvisited:
        route = []
        load = 0
        current_location = depot

        # Greedy construct: always pick the nearest unvisited customer that fits
        while True:
            candidates = []
            for cid in unvisited:
                customer = customer_dict[cid]
                if load + customer['demand'] <= capacity:
                    distance = dist(current_location, customer)
                    candidates.append((distance, cid))
            if not candidates:
                break
            # pick nearest customer
            candidates.sort()
            _, next_cid = candidates[0]
            customer = customer_dict[next_cid]
            route.append(next_cid)
            load += customer['demand']
            current_location = customer
            unvisited.remove(next_cid)

        routes.append(route)

    # Optional: local improvement - swap adjacent customers if beneficial
    # For interpretability, limit to a single pass
    for route in routes:
        for i in range(len(route)-1):
            for j in range(i+1, len(route)):
                # Check if swapping causes capacity issues (it won't, since demand sums are same)
                # and if it reduces total route distance
                cust_i = customer_dict[route[i]]
                cust_j = customer_dict[route[j]]
                # Compute current distance
                prev_cust = depot if i == 0 else customer_dict[route[i-1]]
                next_cust = depot if j == len(route)-1 else customer_dict[route[j+1]]

                dist_before = (
                    dist(prev_cust, cust_i) +
                    dist(cust_i, customer_dict[route[i+1] if i+1 == j else i+1]) +
                    dist(customer_dict[route[j-1 if j-1 != i else i-1]], cust_j) +
                    dist(cust_j, next_cust)
                )

                # After swap
                swap_cust_i = cust_j
                swap_cust_j = cust_i
                dist_after = (
                    dist(prev_cust, swap_cust_i) +
                    dist(swap_cust_i, customer_dict[route[i+1] if i+1 == j else i+1]) +
                    dist(customer_dict[route[j-1 if j-1 != i else i-1]], swap_cust_j) +
                    dist(swap_cust_j, next_cust)
                )
                if dist_after < dist_before:
                    # perform swap
                    route[i], route[j] = route[j], route[i]

    return routes

