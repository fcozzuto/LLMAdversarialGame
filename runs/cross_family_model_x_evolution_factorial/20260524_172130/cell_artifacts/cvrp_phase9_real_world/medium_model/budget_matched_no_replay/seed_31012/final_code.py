def solve_cvrp(instance):
    # instance is expected to be a dict with:
    # - 'customers': list of dicts or tuples representing customers (id, demand)
    # - 'depot': id of depot (not included in routes)
    # - 'vehicle_capacity': integer
    #
    # We'll implement a simple deterministic constructive heuristic:
    # 1) Sort customers by nondecreasing demand to try small first (interpretability).
    # 2) Greedy filling: create routes by adding customers until capacity would be exceeded, then start new route.
    # 3) After initial construction, perform a simple local repair by swapping the last customer of a route with the first of the next route if it reduces number of routes or respects capacity (purely deterministic, no randomness).
    #
    # This uses only constructive and very simple local repair ideas, no external data.
    
    # Normalize input
    customers = []
    depot = None
    capacity = None

    if isinstance(instance, dict):
        if 'customers' in instance:
            # Normalize customers to (id, demand)
            raw = instance['customers']
            # Accept either list of dicts {'id':..., 'demand':...} or tuples (id, demand)
            for c in raw:
                if isinstance(c, dict):
                    cid = c.get('id')
                    dem = c.get('demand', 0)
                else:
                    cid, dem = c
                customers.append((cid, dem))
        else:
            raise ValueError("Instance missing 'customers' field")
        if 'depot' in instance:
            depot = instance['depot']
        if 'vehicle_capacity' in instance:
            capacity = instance['vehicle_capacity']
    else:
        raise ValueError("Unsupported instance format")
    
    if depot is None:
        depot = 0  # fallback label
    if capacity is None:
        raise ValueError("Instance must specify vehicle_capacity")

    # Sort customers by nondecreasing demand, tie-break by id for determinism
    customers.sort(key=lambda x: (x[1], x[0]))
    
    # Construct routes greedily
    routes = []
    current_route = []
    current_load = 0

    for cid, dem in customers:
        if current_load + dem <= capacity:
            current_route.append(cid)
            current_load += dem
        else:
            # finalize current route
            if current_route:
                routes.append(current_route)
            # start new route with this customer
            current_route = [cid]
            current_load = dem
            # if a single customer exceeds capacity, we would normally split, but we assume feasible instances
            if current_load > capacity:
                # handle extremely large demand by splitting into multiple visits (still deterministic)
                # create a dedicated route per portion
                while current_load > capacity:
                    part = capacity
                    # assign a portion to be a separate route
                    routes.append([cid])  # put the customer in its own route (cannot split id)
                    current_route = []
                    current_load = 0
                # if we somehow continued, continue
    if current_route:
        routes.append(current_route)
    
    # If no routes somehow, ensure at least one route
    if not routes:
        routes = [[]]
    
    # Simple local repair: try to merge adjacent routes when possible without exceeding capacity
    i = 0
    while i < len(routes) - 1:
        r1 = routes[i]
        r2 = routes[i+1]
        if not r1 or not r2:
            i += 1
            continue
        # compute loads
        def load(route):
            # sum of demands by ids, using original mapping
            s = 0
            for cid in route:
                # find demand from customers list
                for c in customers:
                    if c[0] == cid:
                        s += c[1]
                        break
            return s
        l1 = load(r1)
        l2 = load(r2)
        # attempt merge
        # ensure merged <= capacity
        # but avoid changing order too much; deterministic
        merge_ok = l1 + l2 <= capacity
        if merge_ok:
            # perform merge: r1 + r2
            routes[i] = r1 + r2
            routes.pop(i+1)
            # do not increment i to recheck with new merged route
        else:
            i += 1

    # Final check: ensure no route is empty
    routes = [r for r in routes if r]

    return routes
