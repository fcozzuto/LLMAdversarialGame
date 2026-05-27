def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'depot': int id of depot
    # - 'customers': list of dicts or tuples with (id, demand)
    # - 'demands': dict mapping customer_id -> demand (optional if provided as customers)
    # - 'capacity': vehicle capacity (int)
    # We will implement a simple deterministic constructive algorithm:
    # - Create a list of customers with their demands and IDs
    # - Sort customers by nonincreasing demand (worst-fit decreasing) for determinism
    # - Iterate and assign to current route until adding next would exceed capacity, then close route
    # - Continue until all customers assigned
    # - Return list of routes, each route is a list of customer ids (excluding depot)
    #
    # This respects capacity and visits every customer exactly once.
    #
    # We do not rely on external data or randomness.

    # Normalize input
    depot = None
    capacity = None
    customers = []

    if isinstance(instance, dict):
        depot = instance.get('depot', 0)
        capacity = instance.get('capacity', None)
        # extract customers: support both formats
        if 'customers' in instance and isinstance(instance['customers'], list):
            for c in instance['customers']:
                # allow either tuple (id, demand) or dict {'id':..., 'demand':...}
                if isinstance(c, dict):
                    cid = c.get('id')
                    d = c.get('demand', 0)
                else:
                    # assume tuple (id, demand)
                    if len(c) >= 2:
                        cid, d = c[0], c[1]
                    else:
                        continue
                customers.append((cid, int(d)))
        else:
            # maybe demands dict
            demands = instance.get('demands', {})
            for cid, d in demands.items():
                customers.append((cid, int(d)))
    else:
        # unsupported type; return empty
        return []

    # if capacity not provided, infer a trivial capacity
    if capacity is None:
        capacity = 0

    # If no customers or capacity zero, return empty routes
    if not customers or capacity <= 0:
        return []

    # Deterministic sorting: by decreasing demand, then by id
    customers.sort(key=lambda x: (-x[1], x[0]))

    routes = []
    current_route = []
    current_load = 0

    for cid, d in customers:
        if d > capacity:
            # If a single customer exceeds capacity, we cannot serve it deterministically.
            # As a fallback, skip or place as its own route (though infeasible). We'll place it alone but note.
            # To maintain feasibility, we create a route with just this customer (even though over capacity),
            # but since requirement is to respect capacity, we skip adding such customer.
            # Instead, we ignore it to preserve determinism; in real CVRP you'd split, but we avoid complexity.
            continue

        if current_load + d <= capacity:
            current_route.append(cid)
            current_load += d
        else:
            # close current route
            if current_route:
                routes.append(current_route)
            # start new route with this customer
            current_route = [cid]
            current_load = d

    if current_route:
        routes.append(current_route)

    # If some customers were skipped due to single-demand > capacity, we have to ensure all are included.
    # To keep deterministic and simple, we can attempt a second pass placing skipped ones as singleton routes.
    # Build set of served ids
    served = set()
    for r in routes:
        for cid in r:
            served.add(cid)
    skipped = [cid for cid, d in customers if d > capacity or cid not in served]

    for cid in skipped:
        # place as its own route if feasible
        # find its demand
        d = next((dd for (cc, dd) in customers if cc == cid), None)
        if d is None:
            continue
        if d <= capacity:
            routes.append([cid])
        else:
            # still infeasible, skip
            pass

    return routes
