def solve_cvrp(instance):
    # Deterministic CVRP solver: simple constructive packing with deterministic repair.
    # instance is expected to provide:
    # - customers: list of dicts with keys 'id' and 'demand'
    # - vehicle_capacity: int
    # - depot is ignored for route construction but exists in structure

    # Extract data without using banned builtins getattr by directly accessing with get if possible
    customers = instance.get('customers', [])
    capacity = instance.get('vehicle_capacity', 0)

    # Build demand map
    demand = {}
    for c in customers:
        cid = c.get('id')
        d = c.get('demand', 0)
        demand[cid] = d

    # Deterministic order: sort by id value
    customer_ids = sorted(demand.keys())

    # Initial constructive packing: first-fit by capacity
    routes = []
    current_route = []
    current_load = 0

    for cid in customer_ids:
        d = demand[cid]
        if current_load + d <= capacity:
            current_route.append(cid)
            current_load += d
        else:
            if current_route:
                routes.append(current_route)
            current_route = [cid]
            current_load = d
            # If a single demand exceeds capacity, keep as is; it will be infeasible
            if current_load > capacity:
                pass
    if current_route:
        routes.append(current_route)

    # Repair: try to merge adjacent routes by moving last of r1 to start of r2 if feasible
    improved = True
    while improved:
        improved = False
        i = 0
        while i < len(routes) - 1:
            r1 = routes[i]
            r2 = routes[i + 1]
            if not r1:
                i += 1
                continue
            moved = True
            while moved and r1:
                moved = False
                cid = r1[-1]
                d = demand[cid]
                # compute load of r2
                load_r2 = 0
                for x in r2:
                    load_r2 += demand[x]
                if load_r2 + d <= capacity:
                    r1.pop()
                    r2.insert(0, cid)
                    improved = True
                    moved = True
                    if not r1:
                        routes.pop(i)
                        i -= 1
                        break
            i += 1

    # Local improvement: try moving customers to earlier routes if capacity allows
    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            if not routes[i]:
                continue
            for cid in list(routes[i]):
                d = demand[cid]
                # try move to earlier route
                for j in range(i - 1, -1, -1):
                    load_j = sum(demand[x] for x in routes[j])
                    if load_j + d <= capacity:
                        routes[i].remove(cid)
                        routes[j].append(cid)
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
        routes = [r for r in routes if len(r) > 0]

    return routes
