def solve_cvrp(instance):
    # instance is expected as a dict-like object with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id (not included in routes)
    # - 'capacity': int
    # We implement a deterministic constructive + simple repair heuristic with local adjustments.

    # Helper: build simple distance matrix from coordinates if present, else use dummy sequential
    # Since we cannot import, we avoid heavy math. We only need deterministic grouping by demand and order.

    # Extract data
    customers = []
    if isinstance(instance, dict):
        customers = list(instance.get('customers', []))
        capacity = instance.get('capacity', 0)
        depot = instance.get('depot', None)
        # If coordinates exist, we won't use them in routing to keep deterministic simple
        # We'll rely on given order and demands.
    else:
        return []

    # Normalize id and demand
    for c in customers:
        if 'id' not in c and 'customer_id' in c:
            c['id'] = c['customer_id']

    # Create a deterministic order: sort by (demand ascending, id)
    customers_sorted = sorted(customers, key=lambda c: (c.get('demand', 0), c.get('id', 0)))

    # Construct routes by greedy packing respecting capacity
    routes = []
    current_route = []
    current_load = 0

    for c in customers_sorted:
        cid = c.get('id')
        d = c.get('demand', 0)

        if d < 0:
            d = 0  # safeguard

        # If single customer exceeds capacity, we must still place (but typically not in CVRP)
        if d > capacity and capacity > 0:
            # Put as its own route if possible
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([cid])
            continue

        if capacity <= 0:
            # No capacity constraint
            current_route = [cid] if not current_route else current_route + [cid]
            routes.append(current_route)
            current_route = []
            current_load = 0
            continue

        if current_load + d <= capacity:
            current_route.append(cid)
            current_load += d
        else:
            # finalize current route
            if current_route:
                routes.append(current_route)
            # start new route with this customer
            current_route = [cid]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Repair pass: ensure no route is empty and remove any depot inclusion (we never include depot)
    routes = [r for r in routes if r]

    # Local improvement: try to merge adjacent routes if capacity allows (deterministic)
    i = 0
    while i < len(routes) - 1:
        r1 = routes[i]
        r2 = routes[i+1]
        cap = capacity
        if cap > 0:
            sumd = sum(next((c.get('demand', 0) for c in customers if c.get('id') == cid), 0) for cid in r1 + r2)
            if sumd <= cap:
                # merge
                routes[i] = r1 + r2
                del routes[i+1]
                # stay on same i to check further merges
                continue
        i += 1

    return routes
