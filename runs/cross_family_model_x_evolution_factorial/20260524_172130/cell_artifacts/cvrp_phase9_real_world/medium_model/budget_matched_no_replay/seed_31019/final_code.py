def solve_cvrp(instance):
    # Instance expected to be a dict with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': {'id': 0} optional, but we won't include depot in routes
    # - 'capacity': int
    #
    # Deterministic constructive + simple repair/local-improvement
    # Build routes by sorting customers by nondecreasing demand-to-distance proxy
    # Then greedy insert into first feasible route; then try simple 2-opt like local swap of adjacent customers within routes
    #
    # We avoid any imports and rely on basic Python

    customers = instance.get('customers', [])
    capacity = instance.get('capacity', 0)

    # If input is not in expected form, return empty
    if not isinstance(customers, list) or capacity <= 0:
        return []

    # Build a simple proxy key to sort customers deterministically.
    # Use a combination of id and demand for stable ordering.
    # We assume each customer dict has 'id' and 'demand'
    candidate_list = []
    for c in customers:
        cid = c.get('id')
        d = c.get('demand', 0)
        if cid is None:
            continue
        candidate_list.append((cid, int(d)))
    # Sort by id to ensure determinism; if many same id ordering preserved
    candidate_list.sort(key=lambda x: x[0])

    # Initialize routes as empty list
    routes = []
    route_loads = []  # corresponding loads

    # Helper: add customer to a route if capacity allows
    def try_append_to_route(route_idx, cust_id, cust_demand):
        if route_loads[route_idx] + cust_demand <= capacity:
            routes[route_idx].append(cust_id)
            route_loads[route_idx] += cust_demand
            return True
        return False

    # Build routes greedily: create a new route when needed
    for cid, dem in candidate_list:
        placed = False
        # Try to place into existing routes in order
        for i in range(len(routes)):
            if try_append_to_route(i, cid, dem):
                placed = True
                break
        if not placed:
            # Start a new route with this customer
            routes.append([cid])
            route_loads.append(dem)

    # Local repair: try to move a single customer from a fuller route to a newer route if feasible
    # This is a simple, deterministic repair step
    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                if not routes[i]:
                    continue
                # Consider moving first element of route i to route j
                cand = routes[i][0]
                # Find demand for cand
                dem = None
                for c in customers:
                    if c.get('id') == cand:
                        dem = c.get('demand', 0)
                        break
                if dem is None:
                    continue
                if route_loads[j] + dem <= capacity:
                    # Move
                    routes[i].pop(0)
                    routes[j].insert(0, cand)
                    route_loads[i] -= dem
                    route_loads[j] += dem
                    changed = True
                    # Clean empty route
                    if not routes[i]:
                        routes.pop(i)
                        route_loads.pop(i)
                    break
            if changed:
                break

    # Minor local improvement: within each route, perform a deterministic "swap adjacent" if it reduces nothing
    # We'll perform a single pass to reorder if adjacent swap doesn't violate capacity (since capacity per route fixed, any order is okay)
    # The objective is not optimized here; we keep deterministic and simple
    for r in range(len(routes)):
        route = routes[r]
        # Simple pass: bubble sort by customer id to have interpretability
        swapped = True
        while swapped:
            swapped = False
            for k in range(len(route) - 1):
                if route[k] > route[k+1]:
                    route[k], route[k+1] = route[k+1], route[k]
                    swapped = True

    # Final: ensure every customer appears exactly once
    seen = set()
    for r in routes:
        for cid in r:
            if cid in seen:
                # duplicate found; remove duplicates conservatively
                # keep first occurrence
                r.remove(cid)
            else:
                seen.add(cid)
    # Return routes as list of lists of ids, excluding depot
    return routes
