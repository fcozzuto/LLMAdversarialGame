def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = list(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    dist = instance["distance_matrix"]

    # Initial solution: singleton routes
    routes = [[c] for c in customers]
    loads = {c: demands[c] for c in customers}
    route_of = {c: i for i, c in enumerate(customers)}

    def route_load(route):
        s = 0
        for n in route:
            s += demands[n]
        return s

    def savings(i, j):
        return dist[depot][i] + dist[depot][j] - dist[i][j]

    # Clarke-Wright style merges on route endpoints
    pairs = []
    n = len(customers)
    for a in range(n):
        i = customers[a]
        for b in range(a + 1, n):
            j = customers[b]
            pairs.append((savings(i, j), i, j))
    pairs.sort(key=lambda x: (-x[0], x[1], x[2]))

    active = [True] * len(routes)

    def find_route_of(node):
        return route_of.get(node, -1)

    for _, i, j in pairs:
        ri = find_route_of(i)
        rj = find_route_of(j)
        if ri < 0 or rj < 0 or ri == rj:
            continue
        if not active[ri] or not active[rj]:
            continue
        A = routes[ri]
        B = routes[rj]
        if not A or not B:
            continue
        la = 0
        lb = 0
        for x in A:
            la += demands[x]
        for x in B:
            lb += demands[x]
        if la + lb > capacity:
            continue

        merged = None
        # Four endpoint orientation cases
        if A[-1] == i and B[0] == j:
            merged = A + B
        elif A[0] == i and B[-1] == j:
            merged = B + A
        elif A[0] == i and B[0] == j:
            merged = A[::-1] + B
        elif A[-1] == i and B[-1] == j:
            merged = A + B[::-1]

        if merged is None:
            continue

        routes[ri] = merged
        active[rj] = False
        for x in merged:
            route_of[x] = ri

    routes = [r for k, r in enumerate(routes) if active[k]]

    # If any customer somehow missing, repair by inserting greedily.
    seen = {}
    for r in routes:
        for c in r:
            seen[c] = 1
    missing = []
    for c in customers:
        if c not in seen:
            missing.append(c)
    for c in missing:
        best_r = -1
        best_pos = 0
        best_cost = None
        for idx in range(len(routes)):
            load = 0
            for x in routes[idx]:
                load += demands[x]
            if load + demands[c] > capacity:
                continue
            r = routes[idx]
            if not r:
                cost = dist[depot][c] * 2
                if best_cost is None or cost < best_cost:
                    best_cost = cost
                    best_r = idx
                    best_pos = 0
                continue
            for pos in range(len(r) + 1):
                prev = depot if pos == 0 else r[pos - 1]
                nxt = depot if pos == len(r) else r[pos]
                cost = dist[prev][c] + dist[c][nxt] - dist[prev][nxt]
                if best_cost is None or cost < best_cost:
                    best_cost = cost
                    best_r = idx
                    best_pos = pos
        if best_r == -1:
            routes.append([c])
        else:
            routes[best_r].insert(best_pos, c)

    # Intra-route 2-opt improvement
    for idx in range(len(routes)):
        r = routes[idx]
        if len(r) < 4:
            continue
        improved = True
        while improved:
            improved = False
            m = len(r)
            for a in range(m - 2):
                a_prev = depot if a == 0 else r[a - 1]
                a_node = r[a]
                for b in range(a + 2, m):
                    b_node = r[b - 1]
                    b_next = depot if b == m else r[b]
                    old = dist[a_prev][a_node] + dist[b_node][b_next]
                    new = dist[a_prev][b_node] + dist[a_node][b_next]
                    if new + 1e-12 < old:
                        r[a:b] = r[a:b][::-1]
                        improved = True
                        break
                if improved:
                    break
        routes[idx] = r

    # Final normalization: remove empty routes if any
    final_routes = []
    for r in routes:
        if r:
            final_routes.append(r)
    return final_routes
