def solve_cvrp(instance):
    # Assumptions about instance structure:
    # instance is a dict with keys:
    # - 'customer_count': int, number of customers (excluding depot)
    # - 'demand': list of int, length equal to customer_count, demand[i] for customer i+1
    # - 'capacity': int, vehicle capacity
    # - 'dist': function(i, j) or 2D list, distance between nodes i and j
    # We will implement a simple constructive, deterministic solver:
    # - Build a list of customers 1..N
    # - Sort customers by non-decreasing demand (deterministic tie-breaking by index)
    # - Greedily assign to current route until adding next customer would exceed capacity, then start new route
    # - Distances are not used to optimize route order beyond maintaining deterministic construction; we keep order as added to keep interpretability
    # - Returns routes as list of lists of customer ids (1-based)
    #
    # Handle different possible representations of dist
    customers = list(range(1, instance['customer_count'] + 1))
    demands = instance['demand']
    capacity = instance['capacity']
    # Build list of (id, demand)
    cand = [(i, demands[i-1]) for i in customers]
    # Sort by demand then by id to ensure deterministic order
    cand.sort(key=lambda x: (x[1], x[0]))
    routes = []
    current_route = []
    current_load = 0
    for cid, dem in cand:
        if dem > capacity:
            # Impossible to serve this customer with given capacity; skip by creating empty route attempt
            # To stay deterministic, place as its own route (even though exceeding capacity) but best effort
            # Instead, we will skip adding and continue; but that would miss customer. To remain robust, assign as single-customer route if possible
            # If still exceeds, we cannot satisfy; in this simple solver, we'll place it alone if possible else raise minimal fallback
            if dem <= capacity:
                pass
        if current_load + dem <= capacity:
            current_route.append(cid)
            current_load += dem
        else:
            if current_route:
                routes.append(current_route)
            current_route = [cid]
            current_load = dem
    if current_route:
        routes.append(current_route)
    # Ensure all customers covered; build set
    covered = set(sum(routes, []))
    all_customers = set(range(1, instance['customer_count'] + 1))
    if covered != all_customers:
        # Fallback: assign any missing customers in increasing order
        missing = sorted(list(all_customers - covered))
        for mid in missing:
            if not routes:
                routes.append([mid])
            else:
                # try to append to last route if capacity allows
                last = routes[-1]
                # compute load
                load = sum(instance['demand'][c-1] for c in last)
                if load + instance['demand'][mid-1] <= capacity:
                    last.append(mid)
                else:
                    routes.append([mid])
    return routes
