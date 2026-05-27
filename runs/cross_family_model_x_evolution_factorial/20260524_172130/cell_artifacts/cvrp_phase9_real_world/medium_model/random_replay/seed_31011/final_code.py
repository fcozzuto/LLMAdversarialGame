def solve_cvrp(instance):
    # Deterministic constructive CVRP solver with simple repair and local improvement.
    # Instance expected as a dict with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id or index (not included in routes)
    # - 'capacity': vehicle capacity
    #
    # The solver:
    # 1) Sort customers by nonincreasing demand (deterministic heuristic).
    # 2) Greedily assign to the first route that can accommodate the customer.
    # 3) If no route can accommodate, start a new route.
    # 4) After initial construction, perform a simple intra-route 2-opt-like local improvement
    #    by swapping adjacent customers if it reduces total positive "distance" surrogate
    #    using a consistent synthetic distance: distance = |pos_i - pos_j| summed with id differences.
    # 5) Ensure each customer appears exactly once, and depot is not included in routes.
    #
    # Note: We do not rely on external data or imports.

    # Helper to extract customers
    customers = instance.get('customers', [])
    capacity = instance.get('capacity', 0)

    # Normalize list of customers with id and demand
    # Expect each customer has 'id' and 'demand'
    custs = []
    for c in customers:
        cid = c.get('id')
        d = c.get('demand', 0)
        custs.append({'id': cid, 'demand': d})

    # If no customers, return empty routes
    if not custs:
        return []

    # Sort by demand descending (stable)
    custs.sort(key=lambda x: (-x['demand'], x['id']))

    # Build routes: list of lists of customer ids (excluding depot)
    routes = []
    loads = []  # current load per route

    for c in custs:
        cid = c['id']
        d = c['demand']

        # Try to place into first feasible route
        placed = False
        for ri, load in enumerate(loads):
            if load + d <= capacity:
                routes[ri].append(cid)
                loads[ri] = load + d
                placed = True
                break

        if not placed:
            # Create new route starting with this customer
            routes.append([cid])
            loads.append(d)

    # Optional lightweight repair: merge routes if a single customer negligible capacity
    # Here we implement a simple pairwise merge attempt to reduce number of routes
    changed = True
    while changed:
        changed = False
        n = len(routes)
        if n <= 1:
            break
        # Try to move a whole route into previous routes if fits
        for i in range(1, n):
            route_i = routes[i]
            load_i = loads[i]
            # Try to insert all of route_i's customers into an earlier route j
            for j in range(i-1, -1, -1):
                if loads[j] + load_i <= capacity:
                    # Move route_i into route j
                    routes[j].extend(route_i)
                    loads[j] += load_i
                    # Remove route i
                    del routes[i]
                    del loads[i]
                    changed = True
                    break
            if changed:
                break

    # Simple deterministic local improvement: within each route, perform pairwise adjacent swap
    # if swapping reduces a synthetic cost. Define a simple distance function on ids.
    def dist(a, b):
        return abs((a if isinstance(a, int) else int(a)) - (b if isinstance(b, int) else int(b)))

    for r_idx, route in enumerate(routes):
        if len(route) < 2:
            continue
        improved = True
        # Perform a fixed number of passes to keep deterministic
        for _ in range(len(route) * 2):
            if not improved or len(route) < 2:
                break
            improved = False
            for k in range(len(route) - 1):
                a = route[k]
                b = route[k+1]
                # swap if improves local surrogate cost
                # cost before: dist to neighbors
                before = 0
                # left neighbor
                if k - 1 >= 0:
                    before += dist(route[k-1], a)
                # between a and b
                before += dist(a, b)
                # right neighbor
                if k + 2 < len(route):
                    before += dist(b, route[k+2])
                # after swap
                after = 0
                # left neighbor with b
                if k - 1 >= 0:
                    after += dist(route[k-1], b)
                # b with a
                after += dist(b, a)
                # right neighbor with a
                if k + 2 < len(route):
                    after += dist(a, route[k+2])

                if after < before:
                    # perform swap
                    route[k], route[k+1] = route[k+1], route[k]
                    improved = True
        routes[r_idx] = route

    return routes
