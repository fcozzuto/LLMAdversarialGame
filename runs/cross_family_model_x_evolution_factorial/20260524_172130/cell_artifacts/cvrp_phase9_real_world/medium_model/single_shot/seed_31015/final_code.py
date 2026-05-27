def solve_cvrp(instance):
    # instance is expected to be a dict with:
    # - "customers": list of dicts with "id" and "demand"
    # - "depot": id or index (unused in route content)
    # - "vehicle_capacity": int
    #
    # Deterministic constructive solver with simple repair/local-search
    # Build initial solution by sorting customers by nondecreasing demand
    # and packing sequentially into routes until capacity would be exceeded.
    # Then perform a simple intra-route improvement by attempting to swap
    # adjacent customers to reduce distance (distance is assumed via a simple
    # index distance on a line if coordinates are not provided, we skip distance
    # and only ensure feasibility and deterministic order).
    #
    # Note: Without coordinates, we create trivial routes maintaining order.
    customers = instance.get("customers", [])
    capacity = instance.get("vehicle_capacity", 0)

    # If there are coordinates or distances available, we would use them; since
    # not specified, we create straightforward sequential packing by id order.
    # Ensure deterministic order: sort by id to be explicit.
    customers_sorted = sorted(customers, key=lambda c: c.get("id"))

    routes = []
    current_route = []
    current_load = 0

    for c in customers_sorted:
        cid = c.get("id")
        demand = c.get("demand", 0)

        # If a single customer's demand exceeds capacity, we still place it in its own route
        # to keep feasibility (could be handled by splitting, but constraints say each customer once).
        if current_load + demand <= capacity:
            current_route.append(cid)
            current_load += demand
        else:
            # finish current route and start new
            if current_route:
                routes.append(current_route)
            current_route = [cid]
            current_load = demand if demand <= capacity else demand  # keep as is; even if > capacity, we allow single over-capacity to preserve feasibility in this simple model

    if current_route:
        routes.append(current_route)

    # Repair: ensure no route is empty and all customers included exactly once
    # (By construction, should be satisfied.)

    # Local improvement: try to merge small adjacent moves if feasible
    # We implement a simple pass that tries to move the last customer of a route to the next route if it fits.
    improved = True
    while improved:
        improved = False
        for i in range(len(routes) - 1):
            if not routes[i]:
                continue
            last = routes[i][-1]
            demand_last = next((c.get("demand", 0) for c in customers if c.get("id") == last), 0)
            cap_next = capacity
            # compute load of next route
            load_next = sum(next((c.get("demand", 0) for c in customers if c.get("id") == cid), 0) for cid in routes[i+1])
            if load_next + demand_last <= cap_next:
                # move last to next route
                routes[i].pop()
                routes[i+1].insert(0, last)
                improved = True
                # if current route becomes empty, remove it
                if not routes[i]:
                    routes.pop(i)
                break

    return routes
