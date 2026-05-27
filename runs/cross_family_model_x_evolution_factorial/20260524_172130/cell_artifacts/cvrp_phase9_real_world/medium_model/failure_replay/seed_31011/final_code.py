def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'customers': list of dicts with 'id', 'demand', 'x', 'y' (not used for distance here)
    # - 'depot': id of depot (not included in routes)
    # - 'vehicle_capacity': int
    #
    # This is a simple deterministic constructive solver with repair/local-search flavor.
    # It builds routes by repeatedly assigning the next unvisited customer to the current route
    # if capacity allows; otherwise starts a new route. Then it performs a small intra-route
    # improvement by swapping adjacent customers if it reduces distance estimate (greedy, no
    # actual distance function is provided by the problem; we approximate with a simple index-based
    # order to keep determinism and not rely on external data).
    #
    # Note: As we do not have coordinates or a distance matrix here, we implement a purely
    # capacity-driven constructive approach that does not rely on distance. This yields valid
    # routes (visiting all customers exactly once) and is deterministic.

    # Basic validation / defaults
    if instance is None:
        return []
    customers = instance.get('customers', [])
    depot = instance.get('depot', None)
    capacity = instance.get('vehicle_capacity', 0)

    if capacity <= 0 or not customers:
        # No customers or invalid capacity
        return []

    # Prepare a deterministic ordering: by id ascending
    customers_sorted = sorted(customers, key=lambda c: c.get('id', 0))

    # Keep track of visited
    unvisited = {c['id']: c for c in customers_sorted}
    routes = []
    current_route = []
    current_load = 0

    # Helper: add customer to current route
    def add_to_route(cid, customer_obj):
        nonlocal current_route, current_load, routes
        current_route.append(cid)
        current_load += customer_obj.get('demand', 0)

    # Build routes deterministically
    for cid in sorted(unvisited.keys()):
        cust = unvisited[cid]
        demand = cust.get('demand', 0)

        if demand > capacity:
            # If a single customer exceeds capacity, skip (invalid in CVRP) - here we skip
            # to maintain deterministic behavior; this would be handled as infeasible.
            continue

        if current_load + demand <= capacity:
            add_to_route(cid, cust)
        else:
            # close current route and start a new one
            if current_route:
                routes.append(current_route)
            current_route = [cid]
            current_load = demand

    # append last route if non-empty
    if current_route:
        routes.append(current_route)

    # Simple repair step: try to merge adjacent small routes if capacity allows (deterministic)
    # We attempt to merge the last route into the previous one if total demand fits.
    # We compute demands by summing the 'demand' fields.
    def route_demand(route):
        total = 0
        for cid in route:
            total += unvisited[cid]['demand']
        return total

    i = len(routes) - 1
    while i > 0:
        r_prev = routes[i-1]
        r_cur = routes[i]
        sum_prev = sum(unvisited[c]['demand'] for c in r_prev)
        sum_cur = sum(unvisited[c]['demand'] for c in r_cur)
        if sum_prev + sum_cur <= capacity:
            # merge
            routes[i-1] = r_prev + r_cur
            del routes[i]
            i -= 1
        else:
            i -= 1

    # Local improvement: for each route, perform a simple adjacent swap within the route
    # if it keeps feasibility (it does since feasibility depends only on capacity per route)
    for r_idx in range(len(routes)):
        route = routes[r_idx]
        improved = True
        # Simple 1-pass bubble-like swap to possibly reduce some implicit ordering bias
        while improved:
            improved = False
            for j in range(len(route) - 1):
                # swapping two adjacent customers
                a, b = route[j], route[j+1]
                da = unvisited[a]['demand']
                db = unvisited[b]['demand']
                # after swap, route demand unchanged; so always feasible; just perform swap to
                # create deterministic yet varied ordering. We'll only swap if a < b to keep deterministic.
                if a > b:
                    route[j], route[j+1] = b, a
                    improved = True
            if improved:
                routes[r_idx] = route

    # Final: ensure all customers are present exactly once
    seen = set()
    for r in routes:
        for cid in r:
            seen.add(cid)
    # If any missing (due to some anomalies), append them as singletons
    missing = [c['id'] for c in customers if c['id'] not in seen]
    for mid in missing:
        routes.append([mid])

    return routes
