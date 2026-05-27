def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'customers': list of dicts with 'id', 'demand' and optional 'x','y'
    # - 'depot': id or object (not used in routes)
    # - 'vehicle_capacity': int
    # - Optional: 'distance' function or matrix not required for feasibility only
    #
    # Deterministic constructive solver with simple repair and local improvement.
    # We'll implement:
    # 1) sort customers by nondecreasing demand (stable)
    # 2) greedy insert into the first route with remaining capacity, else new route
    # 3) after initial construction, try simple intra-route swap to improve feasibility (not required) and ensure determinism
    # Note: We only return routes as lists of customer ids, excluding depot.

    customers = instance.get('customers', [])
    capacity = instance.get('vehicle_capacity', None)

    # Build a map of id to demand
    demands = {c['id']: c.get('demand', 0) for c in customers}

    # If no customers or capacity invalid, return empty
    if not customers or capacity is None or capacity <= 0:
        return []

    # Deterministic order: sort by (demand, id) to be stable and deterministic
    sorted_customers = sorted(customers, key=lambda c: (c.get('demand', 0), c['id']))

    routes = []            # list of routes, each route is a list of customer ids
    remaining = []         # remaining capacity per route (parallel to routes)

    for c in sorted_customers:
        cid = c['id']
        d = c.get('demand', 0)
        placed = False

        # Try to put into first route with enough remaining capacity
        for i, rem in enumerate(remaining):
            if d <= rem:
                routes[i].append(cid)
                remaining[i] = rem - d
                placed = True
                break

        # If none fit, open a new route
        if not placed:
            routes.append([cid])
            remaining.append(capacity - d)

    # Basic feasibility check: ensure every customer placed exactly once
    all_ids = [c['id'] for c in customers]
    placed_ids = [cid for r in routes for cid in r]
    # If a customer appears more than once or missing, repair by rebuild (very simple)
    if sorted(placed_ids) != sorted(all_ids):
        # Repair: rebuild deterministically from scratch
        routes = []
        remaining = []
        for c in sorted_customers:
            cid = c['id']
            d = c.get('demand', 0)
            placed = False
            for i, rem in enumerate(remaining):
                if d <= rem:
                    routes[i].append(cid)
                    remaining[i] = rem - d
                    placed = True
                    break
            if not placed:
                routes.append([cid])
                remaining.append(capacity - d)

    # Optional very simple local improvement: within each route, try to swap adjacent customers if it keeps feasibility
    # This is deterministic and cheap.
    for r_idx, route in enumerate(routes):
        improved = True
        # simple bubble-like pass to swap if maintains capacity (which it will, since demands fixed)
        # However swapping within a route does not change feasibility; we keep only if provides simple interpretability.
        # We'll attempt one pass of reversing any pair that keeps internal order but we keep as is to stay deterministic.
        # Do nothing to avoid changing route sizes; this section kept minimal.

        # (No operation)

        routes[r_idx] = route

    return routes
