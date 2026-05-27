def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers_all = list(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    d = instance["distance_matrix"]

    def route_cost_detailed(route):
        if not route:
            return 0
        c = d[depot][route[0]]
        for i in range(len(route) - 1):
            c += d[route[i]][route[i + 1]]
        c += d[route[-1]][depot]
        return c

    def route_load(route):
        s = 0
        for d0 in route:
            s += demands[d0]
        return s

    remaining = set(customers_all)
    routes = []

    # Constructive phase: double-ended greedy routes.
    while remaining:
        route = []
        load = 0

        # Start with the farthest feasible customer from depot.
        start = None
        best_key = None
        for node in remaining:
            if demands[node] <= capacity:
                key = (d[depot][node], demands[node], node)
                if best_key is None or key > best_key:
                    best_key = key
                    start = node
        if start is None:
            start = min(remaining)
        route.append(start)
        remaining.remove(start)
        load += demands[start]

        while True:
            feasible = []
            for node in remaining:
                if load + demands[node] <= capacity:
                    feasible.append(node)
            if not feasible:
                break

            first = route[0]
            last = route[-1]

            best_node = None
            best_side = 0
            best_score = None

            for node in feasible:
                # Incremental cost for appending at the end or prepending at the start.
                add_end = d[last][node] + d[node][depot] - d[last][depot]
                add_start = d[depot][node] + d[node][first] - d[depot][first]
                if add_end <= add_start:
                    score = (add_end, d[depot][node], demands[node], node)
                    side = 1
                else:
                    score = (add_start, d[depot][node], demands[node], node)
                    side = -1
                if best_score is None or score < best_score:
                    best_score = score
                    best_node = node
                    best_side = side

            if best_node is None:
                break
            if best_side == 1:
                route.append(best_node)
            else:
                route.insert(0, best_node)
            remaining.remove(best_node)
            load += demands[best_node]

        routes.append(route)

    # Repair / improvement phase: intra-route 2-opt.
    for r in range(len(routes)):
        route = routes[r]
        n = len(route)
        improved = True
        limit = 0
        while improved and limit < 2:
            improved = False
            limit += 1
            if n < 4:
                break
            current_cost = route_cost_detailed(route)
            best_delta = 0
            best_i = -1
            best_j = -1
            for i in range(n - 2):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for j in range(i + 2, n):
                    c = route[j]
                    e = depot if j == n - 1 else route[j + 1]
                    delta = (d[a][c] + d[b][e]) - (d[a][b] + d[c][e])
                    if delta < best_delta:
                        best_delta = delta
                        best_i = i
                        best_j = j
            if best_delta < 0:
                route[best_i:best_j + 1] = reversed(route[best_i:best_j + 1])
                improved = True
                n = len(route)
        routes[r] = route

    # Cross-route relocate/swap improvements.
    changed = True
    rounds = 0
    while changed and rounds < 2:
        changed = False
        rounds += 1
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j:
                    continue
                ri = routes[i]
                rj = routes[j]
                li = route_load(ri)
                lj = route_load(rj)

                # Relocate from ri to rj
                best_move = None
                for p in range(len(ri)):
                    node = ri[p]
                    if lj + demands[node] > capacity:
                        continue
                    prev_i = depot if p == 0 else ri[p - 1]
                    next_i = depot if p == len(ri) - 1 else ri[p + 1]
                    remove_delta = d[prev_i][next_i] - d[prev_i][node] - d[node][next_i]

                    for q in range(len(rj) + 1):
                        prev_j = depot if q == 0 else rj[q - 1]
                        next_j = depot if q == len(rj) else rj[q]
                        insert_delta = d[prev_j][node] + d[node][next_j] - d[prev_j][next_j]
                        delta = remove_delta + insert_delta
                        if best_move is None or delta < best_move[0]:
                            best_move = (delta, p, q, node)
                if best_move is not None and best_move[0] < 0:
                    _, p, q, node = best_move
                    ri.pop(p)
                    rj.insert(q, node)
                    changed = True
                    if not ri:
                        routes[i] = []
                    continue

                # Swap between routes
                best_swap = None
                for p in range(len(ri)):
                    a = ri[p]
                    for q in range(len(rj)):
                        b = rj[q]
                        new_li = li - demands[a] + demands[b]
                        new_lj = lj - demands[b] + demands[a]
                        if new_li > capacity or new_lj > capacity:
                            continue

                        prev_i = depot if p == 0 else ri[p - 1]
                        next_i = depot if p == len(ri) - 1 else ri[p + 1]
                        prev_j = depot if q == 0 else rj[q - 1]
                        next_j = depot if q == len(rj) - 1 else rj[q + 1]

                        delta_i = d[prev_i][b] + d[b][next_i] - d[prev_i][a] - d[a][next_i]
                        delta_j = d[prev_j][a] + d[a][next_j] - d[prev_j][b] - d[b][next_j]
                        delta = delta_i + delta_j
                        if best_swap is None or delta < best_swap[0]:
                            best_swap = (delta, p, q, a, b)
                if best_swap is not None and best_swap[0] < 0:
                    _, p, q, a, b = best_swap
                    ri[p], rj[q] = b, a
                    changed = True

    # Remove any empty routes and return.
    final_routes = []
    for route in routes:
        if route:
            final_routes.append(route)
    return final_routes
