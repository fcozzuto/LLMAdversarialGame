def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = list(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    dist = instance["distance_matrix"]

    if not customers:
        return []

    # Deterministic ordering: farthest from depot first, then demand, then id.
    customers.sort(key=lambda n: (-dist[depot][n], -demands[n], n))
    unserved = customers[:]
    routes = []

    def best_seed():
        return unserved[0]

    while unserved:
        seed = best_seed()
        route = [seed]
        load = demands[seed]
        unserved.pop(0)
        current = seed

        # Greedy path growth with a simple lookahead score:
        # prefer close nodes, but also slightly prefer nodes that are
        # harder to serve later (farther from depot / larger demand).
        while True:
            best_i = -1
            best_node = None
            best_key = None
            for i, node in enumerate(unserved):
                d = demands[node]
                if load + d > capacity:
                    continue
                key = (dist[current][node] + 0.35 * dist[depot][node] - 0.15 * d, d, node)
                if best_key is None or key < best_key:
                    best_key = key
                    best_node = node
                    best_i = i
            if best_node is None:
                break
            route.append(best_node)
            load += demands[best_node]
            current = best_node
            unserved.pop(best_i)

        routes.append(route)

    # Simple repair/local improvement: try to relocate single customers
    # from longer routes to earlier routes when capacity allows and it
    # does not obviously worsen by much.
    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            if not routes[i]:
                continue
            for j in range(i):
                ri = routes[i]
                rj = routes[j]
                load_j = 0
                for x in rj:
                    load_j += demands[x]
                # Try moving one customer from ri to rj
                best_move = None
                best_gain = 0
                for idx, node in enumerate(ri):
                    if load_j + demands[node] > capacity:
                        continue
                    # Cost change if inserted at best position in rj
                    old_i = 0
                    prev = depot
                    for t in range(len(ri)):
                        cur = ri[t]
                        nxt = depot if t + 1 == len(ri) else ri[t + 1]
                        old_i += dist[prev][cur] + dist[cur][nxt] - dist[prev][nxt]
                        prev = cur
                    old_j = 0
                    prev = depot
                    for t in range(len(rj)):
                        cur = rj[t]
                        nxt = depot if t + 1 == len(rj) else rj[t + 1]
                        old_j += dist[prev][cur] + dist[cur][nxt] - dist[prev][nxt]
                        prev = cur

                    rem = ri[:idx] + ri[idx + 1:]
                    if not rem:
                        continue
                    new_i = 0
                    prev = depot
                    for t in range(len(rem)):
                        cur = rem[t]
                        nxt = depot if t + 1 == len(rem) else rem[t + 1]
                        new_i += dist[prev][cur] + dist[cur][nxt] - dist[prev][nxt]
                        prev = cur

                    best_ins = None
                    best_new_j = None
                    for pos in range(len(rj) + 1):
                        cand = rj[:pos] + [node] + rj[pos:]
                        new_j = 0
                        prev = depot
                        for t in range(len(cand)):
                            cur = cand[t]
                            nxt = depot if t + 1 == len(cand) else cand[t + 1]
                            new_j += dist[prev][cur] + dist[cur][nxt] - dist[prev][nxt]
                            prev = cur
                        if best_new_j is None or new_j < best_new_j:
                            best_new_j = new_j
                            best_ins = pos

                    gain = (old_i + old_j) - (new_i + best_new_j)
                    if gain > best_gain:
                        best_gain = gain
                        best_move = (idx, best_ins)

                if best_move is not None and best_gain > 0:
                    idx, pos = best_move
                    node = ri.pop(idx)
                    rj.insert(pos, node)
                    changed = True
                    break
            if changed:
                break

    # Remove any accidental empty routes
    routes = [r for r in routes if r]
    return routes
