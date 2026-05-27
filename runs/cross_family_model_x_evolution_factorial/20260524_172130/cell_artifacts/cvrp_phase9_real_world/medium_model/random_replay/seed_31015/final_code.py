def solve_cvrp(instance):
    # instance expected as a dict-like with:
    # - 'customer_count': number of customers (N)
    # - 'demands': list of demands for customers 1..N (index 0 unused or for customer 1)
    # - 'capacity': vehicle capacity
    # - 'distances': optional; if not provided, assume unit distance between successive ids or simple heuristic
    #
    # We'll implement a deterministic constructive + simple repair heuristic:
    # - Create initial route by sorting customers by demand-to-distance heuristic.
    # - Build routes sequentially, filling until capacity would be exceeded, then start new route.
    # - Then perform a simple intra-route 2-opt style local improvement on each route by attempting to swap adjacent customers if it reduces route "cost".
    # - Do not use any imports, no randomness, deterministic behavior.
    #
    # The function returns a list of routes, each route is a list of customer ids (1-based), depot not included.

    # Basic helpers (no imports)
    def get_n():
        return instance['customer_count']

    def get_demand(i):
        # i is 1-based customer id
        demands = instance['demands']
        return demands[i-1]  # allow demands length N

    def get_distance(i, j):
        # If explicit distance matrix provided, use it; otherwise, provide simple heuristic:
        # If i==j -> 0; if either 0 (depot) -> distance based on absolute difference; else use |i-j| as distance.
        dist = instance.get('distances', None)
        if dist is not None:
            # distance matrix expected as dict with (i,j) or 2D list; we'll support simple case
            try:
                if isinstance(dist, dict):
                    if (i, j) in dist:
                        return dist[(i, j)]
                    if (j, i) in dist:
                        return dist[(j, i)]
                    # fallback to sum
                if isinstance(dist, list):
                    # assume square matrix 1..N with 0 index unused; convert to 0-based
                    return dist[i-1][j-1] if 0 <= i-1 < len(dist) and 0 <= j-1 < len(dist) else abs(i - j)
            except Exception:
                pass
        # simple heuristic distance: treat depot as 0, distance between customers as |i - j|, and depot to customer as i or j
        if i == j:
            return 0
        # approximate: distance to depot is i for i>0
        return abs(i - j) if i > 0 and j > 0 else max(i, j)

    # Build customers list
    N = get_n()
    if N <= 0:
        return []

    # Create a deterministic ordering: sort by a score combining distance from depot and demand
    # Score = (distance from depot) + 0.5 * (demand)
    scores = []
    for c in range(1, N+1):
        d = get_distance(0, c)  # distance from depot to customer; using 0 as depot
        # If distances not defined, our get_distance uses |i-j|; depot to i distance ~ i
        s = d * 1.0 + 0.5 * get_demand(c)
        scores.append((s, c))
    scores.sort()  # deterministic

    # Capacity
    C = instance['capacity']

    # Construct routes
    routes = []
    current_route = []
    current_load = 0

    for _, cust in scores:
        demand = get_demand(cust)
        if demand > C:
            # cannot satisfy this single customer; skip (infeasible instance). But we must visit all; we could create singleton route anyway.
            pass
        if current_load + demand <= C:
            current_route.append(cust)
            current_load += demand
        else:
            if current_route:
                routes.append(current_route)
            current_route = [cust]
            current_load = demand

    if current_route:
        routes.append(current_route)

    # Simple local improvement: intra-route 2-opt-like swap within each route to reduce distance
    # We define a basic cost function: sum distances between consecutive customers
    def route_cost(route):
        if not route:
            return 0
        cost = 0
        prev = 0  # depot index 0
        for c in route:
            cost += get_distance(prev, c)
            prev = c
        # return to depot not required; but we treat only visiting sequence; keep as is
        return cost

    def improve_route(route):
        if len(route) <= 2:
            return route
        best = route
        best_cost = route_cost(route)
        n = len(route)
        # Try all adjacent swaps to keep deterministic and simple
        for i in range(n - 1):
            new_route = best[:]
            new_route[i], new_route[i+1] = new_route[i+1], new_route[i]
            c = route_cost(new_route)
            if c < best_cost:
                best = new_route
                best_cost = c
        return best

    improved = []
    for r in routes:
        improved.append(improve_route(r))

    return improved
