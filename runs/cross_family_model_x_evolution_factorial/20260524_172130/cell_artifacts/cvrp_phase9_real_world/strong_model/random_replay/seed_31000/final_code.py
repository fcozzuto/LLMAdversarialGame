def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = list(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    D = instance["distance_matrix"]

    customers.sort(key=lambda i: (-demands[i], D[depot][i], i))

    def route_load(route):
        s = 0
        for x in route:
            s += demands[x]
        return s

    def route_cost(route):
        if not route:
            return 0
        c = D[depot][route[0]]
        for a, b in zip(route, route[1:]):
            c += D[a][b]
        c += D[route[-1]][depot]
        return c

    def best_insertion_position(route, node):
        if not route:
            return 0, D[depot][node] * 2
        best_pos = 0
        best_delta = D[depot][node] + D[node][route[0]] - D[depot][route[0]]
        for i in range(1, len(route)):
            prev = route[i - 1]
            nxt = route[i]
            delta = D[prev][node] + D[node][nxt] - D[prev][nxt]
            if delta < best_delta or (delta == best_delta and i < best_pos):
                best_delta = delta
                best_pos = i
        tail_delta = D[route[-1]][node] + D[node][depot] - D[route[-1]][depot]
        if tail_delta < best_delta or (tail_delta == best_delta and len(route) < best_pos):
            best_delta = tail_delta
            best_pos = len(route)
        return best_pos, best_delta

    # Construct initial singleton routes
    routes = [[c] for c in customers]
    loads = {c: demands[c] for c in customers}

    # Clarke-Wright style savings merges
    improved = True
    while improved:
        improved = False
        best = None
        best_gain = 0
        for i in range(len(routes)):
            ri = routes[i]
            li = loads[ri[0]]
            for j in range(i + 1, len(routes)):
                rj = routes[j]
                lj = loads[rj[0]]
                if li + lj > capacity:
                    continue

                a0, a1 = ri[0], ri[-1]
                b0, b1 = rj[0], rj[-1]

                candidates = [
                    (a1, b0, ri + rj),
                    (a1, b1, ri + rj[::-1]),
                    (a0, b0, ri[::-1] + rj),
                    (a0, b1, ri[::-1] + rj[::-1]),
                ]
                for x, y, merged in candidates:
                    gain = D[depot][x] + D[depot][y] - D[x][y]
                    if gain > best_gain or (gain == best_gain and (i, j, len(merged)) < (best[0], best[1], len(best[2])) if best else True):
                        best_gain = gain
                        best = (i, j, merged)
        if best is not None and best_gain > 0:
            i, j, merged = best
            ri = routes[i]
            rj = routes[j]
            loads[merged[0]] = loads[ri[0]] + loads[rj[0]]
            routes[i] = merged
            routes.pop(j)
            # keep load map only for route keys; refresh below
            loads = {r[0]: route_load(r) for r in routes}
            improved = True

    # Repair / polish: relocate customers between routes if beneficial and feasible
    changed = True
    while changed:
        changed = False
        loads = {r[0]: route_load(r) for r in routes}
        best_move = None
        best_delta = 0
        for a in range(len(routes)):
            ra = routes[a]
            la = loads[ra[0]]
            for idx in range(len(ra)):
                node = ra[idx]
                prev = depot if idx == 0 else ra[idx - 1]
                nxt = depot if idx == len(ra) - 1 else ra[idx + 1]
                remove_delta = D[prev][nxt] - D[prev][node] - D[node][nxt]
                for b in range(len(routes)):
                    if a == b:
                        continue
                    rb = routes[b]
                    lb = loads[rb[0]]
                    if lb + demands[node] > capacity:
                        continue
                    pos, ins_delta = best_insertion_position(rb, node)
                    delta = remove_delta + ins_delta
                    if delta < best_delta or (delta == best_delta and (a, b, idx, pos) < best_move[0:4] if best_move else True):
                        best_delta = delta
                        best_move = (a, b, idx, pos, node)
        if best_move is not None and best_delta < 0:
            a, b, idx, pos, node = best_move
            ra = routes[a]
            rb = routes[b]
            del ra[idx]
            if a < b:
                b -= 1
            rb.insert(pos, node)
            if not ra:
                routes.pop(a)
            changed = True

    # Intra-route 2-opt improvement
    for r in range(len(routes)):
        route = routes[r]
        if len(route) < 4:
            continue
        improved = True
        while improved:
            improved = False
            n = len(route)
            for i in range(n - 2):
                a = depot if i == 0 else route[i - 1]
                b = route[i]
                for k in range(i + 2, n):
                    c = route[k - 1]
                    d = depot if k == n else route[k]
                    old = D[a][b] + D[c][d]
                    new = D[a][c] + D[b][d]
                    if new < old:
                        route[i:k] = route[i:k][::-1]
                        improved = True
                        break
                if improved:
                    break
        routes[r] = route

    # Final cleanup: ensure all customers appear exactly once; if any were lost, rebuild greedily
    seen = {}
    for route in routes:
        for x in route:
            seen[x] = seen.get(x, 0) + 1

    missing = [c for c in customers if seen.get(c, 0) == 0]
    duplicates = [c for c, cnt in seen.items() if cnt > 1]

    if missing or duplicates:
        all_routes = []
        remaining = set(customers)
        for route in routes:
            new_route = []
            load = 0
            for x in route:
                if x in remaining and load + demands[x] <= capacity:
                    new_route.append(x)
                    remaining.remove(x)
                    load += demands[x]
            if new_route:
                all_routes.append(new_route)
        routes = all_routes
        remaining = list(remaining)
        remaining.sort(key=lambda i: (-demands[i], D[depot][i], i))
        for node in remaining:
            best_r = None
            best_pos = 0
            best_delta = None
            for r in range(len(routes)):
                if route_load(routes[r]) + demands[node] > capacity:
                    continue
                pos, delta = best_insertion_position(routes[r], node)
                if best_delta is None or delta < best_delta or (delta == best_delta and r < best_r):
                    best_delta = delta
                    best_r = r
                    best_pos = pos
            if best_r is None:
                routes.append([node])
            else:
                routes[best_r].insert(best_pos, node)

    return routes
