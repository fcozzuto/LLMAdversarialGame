def solve_cvrp(instance):
    # instance is expected to be a dict-like object with:
    # - 'n': number of customers
    # - 'demands': list of customer demands of length n (1-based ids in problem definition)
    # - 'capacity': vehicle capacity
    # - 'distances': a 2D list/array (n+1)x(n+1) or at least distance between customers 1..n
    # We implement a deterministic constructive solver with simple repair and local-search ideas.
    n = instance.get('n', 0)
    demands = list(instance.get('demands', []))
    capacity = instance.get('capacity', 0)
    dist = instance.get('distances', [])
    # Normalize to 0-based indexing for customers 0..n-1
    # If distances is provided as (n+1)x(n+1) with depot index 0, adjust accordingly.
    # We'll implement a simple nearest-fit constructive:
    # - Start with all customers unassigned
    # - Build routes by taking the nearest non-assigned customer to the last customer in the route
    # - Ensure capacity; if adding would exceed, close route and start new one from depot
    # - We'll treat depot as 0; customers as 1..n in input but our arrays are 0..n-1 for demands
    # To maintain compatibility, we'll map:
    # If dist is (n+1)x(n+1): depot index 0, customers 1..n. We'll adapt access accordingly.
    # If dist is (n)x(n): customers 1..n mapped to 0..n-1; for distance to depot we'll approximate by distance to 0th element if available.
    def get_dist(a, b):
        # a and b are customer indices 0..n-1 or depot as None
        # We'll implement a simple fallback:
        if not dist:
            return 0
        # If depot present as index -1 for both, return 0
        if a is None and b is None:
            return 0
        # Map to matrix indices:
        # If matrix is (n+1)x(n+1) with depot at index 0:
        if len(dist) == n + 1 and len(dist[0]) == n + 1:
            ai = 0 if a is None else a + 1
            bi = 0 if b is None else b + 1
            return dist[ai][bi]
        # If matrix is (n)x(n)
        if len(dist) == n and len(dist[0]) == n:
            ai = 0 if a is None else a
            bi = 0 if b is None else b
            return dist[ai][bi]
        # Fallback: approximate with sum of single distances
        return 0

    # Initialize
    customers = list(range(n))  # 0..n-1
    unassigned = set(customers)
    routes = []

    # Heuristic: sort customers by increasing demand to place small ones first (deterministic)
    # But to be deterministic with no randomness, pick by increasing index
    order = sorted(list(unassigned), key=lambda x: x)

    # Build routes
    while unassigned:
        capacity_left = capacity
        route = []
        # Start from depot
        last = None  # depot as None
        # Pick first feasible customer with smallest index that fits
        candidates = [c for c in order if c in unassigned and demands[c] <= capacity_left]
        if not candidates:
            # If no single customer fits current remaining capacity (shouldn't happen if capacity>=max demand)
            # Force take the largest demand customer to avoid infinite loop
            c = max(unassigned, key=lambda x: demands[x])
        else:
            c = candidates[0]
        # Add first customer
        route.append(c)
        unassigned.remove(c)
        capacity_left -= demands[c]
        last = c
        # Continue adding nearest feasible customers
        while True:
            # Build list of feasible next customers from unassigned that fit
            feasible = [x for x in unassigned if demands[x] <= capacity_left]
            if not feasible:
                break
            # Pick the nearest to last (deterministic: smallest distance; if dist unknown, pick smallest index)
            best = None
            best_dist = None
            for x in feasible:
                d = get_dist(last, x)
                if best is None or d < best_dist:
                    best = x
                    best_dist = d
            if best is None:
                break
            route.append(best)
            unassigned.remove(best)
            capacity_left -= demands[best]
            last = best
        routes.append(route)
    # Repair: ensure all customers covered (should be)
    # Local improvement: try to swap adjacent customers between routes if reduces total distance
    # We'll perform a single pass of simple 2-opt-like swap between routes
    improved = True
    max_iter = 5  # small deterministic iterations
    it = 0
    while improved and it < max_iter:
        improved = False
        it += 1
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j or not routes[i] or not routes[j]:
                    continue
                # Try moving last of route i to front of route j if capacity allows
                a = routes[i][-1]
                b = routes[j][0]
                cap_i = sum(demands[c] for c in routes[i])
                cap_j = sum(demands[c] for c in routes[j])
                if cap_j + demands[a] > capacity:
                    continue
                # Compute delta distance for moving a from end of i to start of j
                # Distances:
                # ... i: ... - a to depot or next; approximate by
                old = 0
                if len(routes[i]) >= 2:
                    old += get_dist(routes[i][-2], routes[i][-1])
                else:
                    old += get_dist(None, routes[i][-1])
                if len(routes[j]) >= 2:
                    old += get_dist(routes[j][0], routes[j][1])
                else:
                    old += get_dist(None, routes[j][0])
                # New distances after move
                new = 0
                if len(routes[i]) >= 2:
                    new += get_dist(routes[i][-2], None)
                    new += get_dist(None, routes[i][-1])
                else:
                    new += 0
                new += 0  # placeholder to keep structure
                # Simpler: compute full route distances after modification
                new_routes = [r[:] for r in routes]
                new_routes[i] = routes[i][:-1]
                new_routes[j] = [a] + routes[j]
                def route_dist(r):
                    if not r:
                        return 0
                    dsum = 0
                    for idx in range(len(r)-1):
                        dsum += get_dist(r[idx], r[idx+1])
                    return dsum
                old_total = sum(route_dist(r) for r in routes)
                new_total = sum(route_dist(r) for r in new_routes)
                if new_total < old_total:
                    routes = new_routes
                    improved = True
                    break
            if improved:
                break
    return routes
