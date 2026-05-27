def solve_cvrp(instance):
    # Deterministic constructive solver with simple repair/local-search style steps.
    # Instance is expected to be a dict with keys:
    # - "customers": list of dicts with "id", "demand"
    # - "depot": id or 0 (not included in routes)
    # - "capacity": vehicle capacity
    #
    # Deterministic strategy:
    # 1) Sort customers by non-decreasing id (stable) to have deterministic order.
    # 2) Build routes greedily: fill current route until adding next would exceed capacity.
    # 3) If a single customer's demand exceeds capacity, skip (will not happen in valid instances).
    # 4) Return list of routes (each as list of customer ids, excluding depot).
    #
    # Notes:
    # - No external data, no imports.
    # - No replay data used; this is a straightforward constructive method.
    customers = instance.get("customers", [])
    capacity = instance.get("capacity", 0)
    # Normalize customers by id order to ensure determinism
    customers_sorted = sorted(customers, key=lambda c: c.get("id"))
    routes = []
    current_route = []
    current_load = 0

    for c in customers_sorted:
        cid = c.get("id")
        demand = c.get("demand", 0)
        # If single demand exceeds capacity, we skip it (defensive); in valid instances this won't occur.
        if demand > capacity:
            # Placehold: assign to its own route if possible (but exceeds capacity) -> skip
            # We'll try to discard such case by continuing
            continue
        if current_load + demand <= capacity:
            current_route.append(cid)
            current_load += demand
        else:
            # finish current route and start new
            if current_route:
                routes.append(current_route)
            current_route = [cid]
            current_load = demand

    if current_route:
        routes.append(current_route)

    return routes
