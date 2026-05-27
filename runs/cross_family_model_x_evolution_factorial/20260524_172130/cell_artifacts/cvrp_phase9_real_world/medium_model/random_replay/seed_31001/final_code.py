def solve_cvrp(instance):
    # Deterministic, interpretable CVRP solver with constructive + simple repair + local adjustments.
    # Instance is expected as a dict-like object with:
    # - 'customers': list of dicts with 'id', 'demand' (positive int), optional 'x','y'
    # - 'vehicle_capacity': int
    # - Optional 'depot': id of depot (not included in routes)
    # No use of banned builtins getattr in this implementation.

    # Extract data deterministically
    if isinstance(instance, dict):
        customers = instance.get('customers', [])
        capacity = instance.get('vehicle_capacity', None)
        depot_id = instance.get('depot', 0)
    else:
        # Fallback if a more exotic object is passed
        customers = []
        capacity = None
        depot_id = 0

    if capacity is None:
        # If capacity unknown, treat as one route with all customers
        total = sum(c.get('demand', 0) for c in customers)
        if total <= 0:
            return []
        return [[c['id'] for c in customers]]

    # Build a deterministic customer list (id, demand)
    cus = []
    for c in customers:
        cid = c.get('id')
        d = c.get('demand', 0)
        if cid is None:
            continue
        cus.append({'id': cid, 'demand': d})
    cus.sort(key=lambda x: x['id'])

    # Construct routes greedily by capacity
    routes = []
    current_route = []
    current_load = 0
    for c in cus:
        if c['demand'] > capacity:
            # If a single demand exceeds capacity, place in its own route if possible
            if c['demand'] <= capacity:
                pass
            # Create a standalone route for this customer (may violate capacity if truly larger)
            routes.append([c['id']])
            current_route = []
            current_load = 0
            continue
        if current_load + c['demand'] <= capacity:
            current_route.append(c['id'])
            current_load += c['demand']
        else:
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = c['demand']
    if current_route:
        routes.append(current_route)

    # Remove empty routes
    routes = [r for r in routes if r]

    # Repair: ensure all customers appear exactly once
    seen = set()
    for r in routes:
        # iterate over a copy since we may modify
        for cid in list(r):
            if cid in seen:
                r.remove(cid)
            else:
                seen.add(cid)
    all_ids = set(c['id'] for c in cus)
    missing = sorted(all_ids - seen)
    if missing:
        demand_map = {c['id']: c['demand'] for c in cus}
        route_loads = [sum(demand_map[i] for i in r) for r in routes]
        for mid in missing:
            d = demand_map[mid]
            placed = False
            for idx, r in enumerate(routes):
                if route_loads[idx] + d <= capacity:
                    r.append(mid)
                    route_loads[idx] += d
                    placed = True
                    break
            if not placed:
                routes.append([mid])
                route_loads.append(d)

    # Local adjustment: swap adjacent customers between routes to reduce number of routes
    changed = True
    demand = {c['id']: c['demand'] for c in cus}
    while changed:
        changed = False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                ri = routes[i]
                rj = routes[j]
                if not ri or not rj:
                    continue
                cid = ri[-1]
                d = demand[cid]
                if sum(demand[x] for x in rj) + d <= capacity:
                    ri.pop()
                    rj.insert(0, cid)
                    changed = True
                    break
            if changed:
                break

    # Final cleanup: remove any empty routes
    routes = [r for r in routes if r]
    return routes
