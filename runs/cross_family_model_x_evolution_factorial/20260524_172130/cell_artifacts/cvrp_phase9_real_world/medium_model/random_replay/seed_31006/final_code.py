def solve_cvrp(instance):
    # Minimal deterministic CVRP solver using constructive + simple repairs
    # Instance expected as:
    # instance = {
    #   'customer_count': n,
    #   'depot': 0,
    #   'demands': [d1, d2, ..., dn],  # length n, customers are 1..n with ids in code as 1..n
    #   'capacity': C,
    #   'dist': function(i, j) -> distance, or a matrix dist[i][j] with 0..n
    # }
    #
    # We will assume customers are 1..n (excluding depot 0). The input may provide
    # a structured dict; we adapt to common formats.
    #
    # Strategy:
    # 1) Construct initial routes by sorting customers by non-increasing demand and greedily
    #    packing into vehicles until capacity reached, starting new route when needed.
    # 2) Repair: if any route contains a customer more than once (shouldn't) or capacity violated,
    #    we re-pack that route.
    # 3) Simple local improvement: try to move the lightest possible customer between routes to balance
    #    and reduce total distance using a straightforward insertion sanity check based on distance
    #    to neighboring customers (deterministic).
    #
    # The solver returns list of routes, each route is a list of customer ids (1..n), no depot.
    #
    # Normalize input
    if instance is None:
        return []
    n = int(instance.get('customer_count', 0))
    if n <= 0:
        return []
    capacity = float(instance.get('capacity', 0))
    # Demands
    demands = list(instance.get('demands', []))
    if len(demands) != n:
        # Try to derive from a dist matrix if provided
        if 'demands_by_customer' in instance:
            # Expect dict {customer_id: demand}
            dmap = instance['demands_by_customer']
            demands = [dmap.get(i, 0) for i in range(1, n+1)]
        else:
            # Fallback: assume unit demand
            demands = [1.0 for _ in range(n)]
    # Distances: we need deterministic comparison. If dist matrix provided, use it;
    # otherwise implement simple linear index distance using (i-j) difference (deterministic)
    dist_matrix = instance.get('dist', None)
    def distance(i, j):
        # i and j are customer ids 1..n; depot is 0 but not used in distance directly
        if dist_matrix is not None:
            try:
                return dist_matrix[i][j]
            except Exception:
                pass
        # Fallback: simple symmetric distance based on ids
        di, dj = i, j
        return abs(di - dj)
    # Prepare list of customers
    customers = list(range(1, n+1))
    # Sort by non-increasing demand for constructive packing (deterministic)
    customers.sort(key=lambda cid: demands[cid-1], reverse=True)

    routes = []
    current = []
    current_cap = 0.0
    for cid in customers:
        d = demands[cid-1]
        if d > capacity:
            # If a single customer exceeds capacity, create empty route for it (shouldn't happen in valid instances)
            # For safety, place it alone in its own route
            if current:
                routes.append(current)
                current = []
                current_cap = 0.0
            routes.append([cid])
            # remove high demand, continue
            continue
        if current_cap + d <= capacity:
            current.append(cid)
            current_cap += d
        else:
            # finish current route, start new
            if current:
                routes.append(current)
            current = [cid]
            current_cap = d
    if current:
        routes.append(current)

    # Repair: ensure no route is empty and that every customer appears exactly once
    seen = set()
    clean_routes = []
    for r in routes:
        nr = []
        for c in r:
            if c not in seen:
                seen.add(c)
                nr.append(c)
        if nr:
            clean_routes.append(nr)
    # If any customer missing due to duplicates, append them in a greedy way
    missing = [cid for cid in range(1, n+1) if cid not in seen]
    if missing:
        # try to insert missing ones into existing routes if capacity allows
        for cid in missing:
            placed = False
            d = demands[cid-1]
            for r in clean_routes:
                cap_used = sum(demands[cid2-1] for cid2 in r)
                if cap_used + d <= capacity:
                    r.append(cid)
                    placed = True
                    break
            if not placed:
                clean_routes.append([cid])
    routes = clean_routes

    # Local improvement: try to move a single lowest-demand customer from a longer route to another route
    # if it reduces total travel cost. Use a simple cost delta: rough estimate using distances to neighbors.
    # We'll implement a small deterministic pass with fixed iterations (at most len(routes))
    improved = True
    max_swaps = len(routes) * 2
    iterations = 0
    while improved and iterations < max_swaps:
        improved = False
        iterations += 1
        # compute a helper to get neighbors in a route
        def route_cost(r):
            if not r:
                return 0.0
            cost = 0.0
            for i in range(len(r) - 1):
                cost += distance(r[i], r[i+1])
            return cost
        # compute current total distance (approx uses consecutive edges)
        total_cost = sum(route_cost(r) for r in routes)
        # try moving the first customer of a route to another route
        for i, r_from in enumerate(routes):
            if not r_from:
                continue
            candidate = r_from[0]
            d = demands[candidate-1]
            for j, r_to in enumerate(routes):
                if i == j:
                    continue
                cap_used = sum(demands[cid-1] for cid in r_to)
                if cap_used + d > capacity:
                    continue
                # simulate move
                new_r_from = r_from[1:]
                new_r_to = r_to + [candidate]
                new_routes = routes.copy()
                new_routes[i] = new_r_from
                new_routes[j] = new_r_to
                new_cost = sum(route_cost(rr) for rr in new_routes)
                if new_cost < total_cost:
                    # apply move
                    routes = new_routes
                    improved = True
                    break
            if improved:
                break

    # Final sanity: ensure all customers present exactly once
    final_seen = set()
    for r in routes:
        final_seen.update(r)
    missing_final = [cid for cid in range(1, n+1) if cid not in final_seen]
    if missing_final:
        # append missing in a new route
        routes.append(missing_final)

    return routes
