def solve_cvrp(instance):
    depot = instance.get('depot', 0)

    # ---------- helpers ----------
    def is_seq(x):
        return isinstance(x, (list, tuple))

    def get_customers():
        if 'customers' in instance:
            return list(instance['customers'])
        if 'demands' in instance and isinstance(instance['demands'], dict):
            return [k for k in instance['demands'].keys() if k != depot]
        if 'nodes' in instance:
            return [k for k in instance['nodes'] if k != depot]
        return []

    customers = get_customers()

    def demand_of(node):
        d = instance.get('demands', {})
        if isinstance(d, dict):
            return d.get(node, 0)
        if is_seq(d):
            if isinstance(node, int) and 0 <= node < len(d):
                return d[node]
            return 0
        return 0

    capacity = instance.get('capacity', instance.get('vehicle_capacity', 0))

    coords = instance.get('coords', instance.get('coordinates', None))
    dist_matrix = instance.get('distance_matrix', instance.get('distances', None))

    def coord_of(node):
        if coords is None:
            return None
        if isinstance(coords, dict):
            return coords.get(node, None)
        if is_seq(coords) and isinstance(node, int) and 0 <= node < len(coords):
            return coords[node]
        return None

    def dist(a, b):
        if a == b:
            return 0
        if dist_matrix is not None:
            if isinstance(dist_matrix, dict):
                row = dist_matrix.get(a, None)
                if isinstance(row, dict) and b in row:
                    return row[b]
            elif is_seq(dist_matrix):
                if isinstance(a, int) and isinstance(b, int):
                    if 0 <= a < len(dist_matrix):
                        row = dist_matrix[a]
                        if is_seq(row) and 0 <= b < len(row):
                            return row[b]
        ca = coord_of(a)
        cb = coord_of(b)
        if ca is not None and cb is not None and len(ca) >= 2 and len(cb) >= 2:
            dx = ca[0] - cb[0]
            dy = ca[1] - cb[1]
            return (dx * dx + dy * dy) ** 0.5
        return abs(a - b)

    def route_load(route):
        s = 0
        for n in route:
            s += demand_of(n)
        return s

    def route_cost(route):
        if not route:
            return 0
        c = dist(depot, route[0])
        for i in range(len(route) - 1):
            c += dist(route[i], route[i + 1])
        c += dist(route[-1], depot)
        return c

    def total_cost(routes):
        return sum(route_cost(r) for r in routes)

    # ---------- initial construction ----------
    routes = []

    if coords is not None:
        dep = coord_of(depot)
        if dep is not None and len(dep) >= 2:
            def angle_key(n):
                c = coord_of(n)
                if c is None or len(c) < 2:
                    return (0.0, n)
                dx = c[0] - dep[0]
                dy = c[1] - dep[1]
                # atan2 without imports: use quadrant-aware surrogate ordering
                # sort by half-plane, then slope
                half = 0 if (dy > 0 or (dy == 0 and dx >= 0)) else 1
                if dx == 0:
                    slope = float('inf') if dy >= 0 else -float('inf')
                else:
                    slope = dy / dx
                return (half, slope, dx * dx + dy * dy, n)
            ordered = sorted(customers, key=angle_key)
        else:
            ordered = sorted(customers)
    else:
        # Deterministic fallback: prioritize larger demands, then id
        ordered = sorted(customers, key=lambda n: (-demand_of(n), n))

    current = []
    current_load = 0
    for n in ordered:
        dn = demand_of(n)
        if current and current_load + dn > capacity:
            routes.append(current)
            current = [n]
            current_load = dn
        else:
            current.append(n)
            current_load += dn
    if current:
        routes.append(current)

    # If any singleton is overweight, still keep it; repair below will try to redistribute.
    # ---------- repair for overweight / capacity ----------
    # Try to move customers from overweight routes into others or split if needed.
    def feasible_insert(route, node):
        return route_load(route) + demand_of(node) <= capacity

    changed = True
    guard = 0
    while changed and guard < 200:
        guard += 1
        changed = False
        for i in range(len(routes)):
            if route_load(routes[i]) <= capacity:
                continue
            # Move lightest customers first out of overweight route
            r = routes[i]
            idxs = sorted(range(len(r)), key=lambda k: (demand_of(r[k]), r[k]))
            for idx in idxs:
                node = r[idx]
                best_j = None
                best_pos = None
                best_delta = None
                for j in range(len(routes)):
                    if j == i:
                        continue
                    if route_load(routes[j]) + demand_of(node) > capacity:
                        continue
                    base = route_cost(routes[j])
                    rr = routes[j]
                    for pos in range(len(rr) + 1):
                        cand = rr[:pos] + [node] + rr[pos:]
                        delta = route_cost(cand) - base
                        if best_delta is None or delta < best_delta or (delta == best_delta and (j, pos) < (best_j, best_pos)):
                            best_delta = delta
                            best_j = j
                            best_pos = pos
                if best_j is not None:
                    routes[best_j] = routes[best_j][:best_pos] + [node] + routes[best_j][best_pos:]
                    del routes[i][idx]
                    if not routes[i]:
                        del routes[i]
                    changed = True
                    break
            # if still overweight, leave; no better feasible move found
            if changed:
                break

    # ---------- local search ----------
    def two_opt(route):
        best = route[:]
        best_cost = route_cost(best)
        improved = True
        while improved:
            improved = False
            n = len(best)
            for i in range(n - 1):
                for k in range(i + 1, n):
                    cand = best[:i] + best[i:k + 1][::-1] + best[k + 1:]
                    c = route_cost(cand)
                    if c + 1e-12 < best_cost:
                        best = cand
                        best_cost = c
                        improved = True
                        break
                if improved:
                    break
        return best

    def try_relocate(routes):
        # Best deterministic improving relocate across routes
        best_move = None  # (delta, i, p, j, q)
        base_total = total_cost(routes)
        loads = [route_load(r) for r in routes]
        for i in range(len(routes)):
            ri = routes[i]
            for p, node in enumerate(ri):
                dn = demand_of(node)
                ri_removed = ri[:p] + ri[p + 1:]
                cost_ri_removed = route_cost(ri_removed)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    if loads[j] + dn > capacity:
                        continue
                    rj = routes[j]
                    cost_rj = route_cost(rj)
                    for q in range(len(rj) + 1):
                        cand_j = rj[:q] + [node] + rj[q:]
                        delta = (cost_ri_removed + route_cost(cand_j)) - (route_cost(ri) + cost_rj)
                        if delta < -1e-12:
                            cand = (delta, i, p, j, q)
                            if best_move is None or cand < best_move:
                                best_move = cand
        if best_move is None:
            return False
        _, i, p, j, q = best_move
        node = routes[i][p]
        del routes[i][p]
        if i < j:
            j -= 1
        if not routes[i]:
            del routes[i]
        routes[j] = routes[j][:q] + [node] + routes[j][q:]
        return True

    # Intra-route optimization
    for idx in range(len(routes)):
        routes[idx] = two_opt(routes[idx])

    # Inter-route relocate and a limited merge/split style improvement
    passes = 0
    improved = True
    while improved and passes < 50:
        passes += 1
        improved = False

        # relocate
        if try_relocate(routes):
            improved = True
            for idx in range(len(routes)):
                routes[idx] = two_opt(routes[idx])
            continue

        # try pairwise route reversal ordering by swapping whole routes? not needed

    # ---------- final cleanup ----------
    # Remove empty routes if any and ensure deterministic ordering by first customer/id
    routes = [r for r in routes if r]

    # If some customers somehow missing due to parsing, append them singly (safety net)
    seen = set()
    for r in routes:
        for n in r:
            seen.add(n)
    missing = [n for n in customers if n not in seen]
    for n in missing:
        routes.append([n])

    # Final capacity repair: if any route overloaded, split greedily
    final_routes = []
    for r in routes:
        cur = []
        cur_load = 0
        for n in r:
            dn = demand_of(n)
            if cur and cur_load + dn > capacity:
                final_routes.append(cur)
                cur = [n]
                cur_load = dn
            else:
                cur.append(n)
                cur_load += dn
        if cur:
            final_routes.append(cur)

    # Deterministic route ordering by first customer then length
    final_routes.sort(key=lambda r: (r[0] if r else -1, len(r), r))
    return final_routes
