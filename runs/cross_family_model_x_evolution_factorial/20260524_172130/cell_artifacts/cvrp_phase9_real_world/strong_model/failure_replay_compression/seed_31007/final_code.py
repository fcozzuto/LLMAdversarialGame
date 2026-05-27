def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = list(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    dist = instance["distance_matrix"]

    def rload(r):
        s = 0
        for x in r:
            s += demands[x]
        return s

    def rcost(r):
        if not r:
            return 0
        c = dist[depot][r[0]]
        for i in range(len(r) - 1):
            c += dist[r[i]][r[i + 1]]
        c += dist[r[-1]][depot]
        return c

    def rev(r):
        return list(reversed(r))

    def total_cost(routes):
        s = 0
        for r in routes:
            s += rcost(r)
        return s

    # Seed with one customer per route, ordered by polar angle / demand tie-break.
    # Deterministic, interpretable ordering using depot-relative distances.
    def key_of(c):
        return (dist[depot][c], -demands[c], c)

    customers.sort(key=key_of)

    routes = [[c] for c in customers]
    loads = [demands[c] for c in customers]

    # Clarke-Wright style savings, merge route ends only.
    while True:
        best = None
        best_s = 0
        m = len(routes)
        for i in range(m):
            ri = routes[i]
            if not ri:
                continue
            li = loads[i]
            for j in range(i + 1, m):
                rj = routes[j]
                if not rj:
                    continue
                lj = loads[j]
                if li + lj > capacity:
                    continue

                a0, a1 = ri[0], ri[-1]
                b0, b1 = rj[0], rj[-1]
                cand = [
                    (dist[depot][a1] + dist[depot][b0] - dist[a1][b0], ri + rj),
                    (dist[depot][a1] + dist[depot][b1] - dist[a1][b1], ri + rev(rj)),
                    (dist[depot][a0] + dist[depot][b0] - dist[a0][b0], rev(ri) + rj),
                    (dist[depot][a0] + dist[depot][b1] - dist[a0][b1], rev(ri) + rev(rj)),
                ]
                for s, merged in cand:
                    if s > best_s or (s == best_s and best is not None and (i, j, merged) < best[0]):
                        best_s = s
                        best = ((i, j, merged), merged)
        if best is None or best_s <= 0:
            break
        (i, j, merged), _ = best
        routes[i] = merged
        loads[i] = rload(merged)
        routes.pop(j)
        loads.pop(j)

    def best_two_opt(route):
        n = len(route)
        if n < 4:
            return route, False
        best_route = route
        best_c = rcost(route)
        improved = False
        for i in range(n - 2):
            for k in range(i + 2, n):
                if i == 0 and k == n - 1:
                    continue
                cand = route[:i + 1] + rev(route[i + 1:k + 1]) + route[k + 1:]
                c = rcost(cand)
                if c < best_c or (c == best_c and cand < best_route):
                    best_route = cand
                    best_c = c
                    improved = True
        return best_route, improved

    def try_relocate(routes, loads):
        base = total_cost(routes)
        m = len(routes)
        for i in range(m):
            ri = routes[i]
            for p in range(len(ri)):
                node = ri[p]
                dn = demands[node]
                rem = ri[:p] + ri[p + 1:]
                if not rem:
                    continue
                for j in range(m):
                    if i == j:
                        continue
                    if loads[j] + dn > capacity:
                        continue
                    rj = routes[j]
                    for ins in range(len(rj) + 1):
                        nrj = rj[:ins] + [node] + rj[ins:]
                        new_routes = routes[:]
                        new_routes[i] = rem
                        new_routes[j] = nrj
                        nc = total_cost(new_routes)
                        if nc < base or (nc == base and new_routes < routes):
                            return new_routes
        return None

    def try_swap(routes, loads):
        base = total_cost(routes)
        m = len(routes)
        for i in range(m):
            ri = routes[i]
            for j in range(i + 1, m):
                rj = routes[j]
                for a in range(len(ri)):
                    x = ri[a]
                    dx = demands[x]
                    for b in range(len(rj)):
                        y = rj[b]
                        dy = demands[y]
                        nli = loads[i] - dx + dy
                        nlj = loads[j] - dy + dx
                        if nli > capacity or nlj > capacity:
                            continue
                        nri = ri[:a] + [y] + ri[a + 1:]
                        nrj = rj[:b] + [x] + rj[b + 1:]
                        new_routes = routes[:]
                        new_routes[i] = nri
                        new_routes[j] = nrj
                        nc = total_cost(new_routes)
                        if nc < base or (nc == base and new_routes < routes):
                            return new_routes
        return None

    # Intra-route 2-opt
    for _ in range(10):
        changed = False
        for i in range(len(routes)):
            nr, imp = best_two_opt(routes[i])
            if imp:
                routes[i] = nr
                changed = True
        if not changed:
            break

    # Inter-route improvement: relocate, swap, then 2-opt again.
    for _ in range(30):
        new_routes = try_relocate(routes, loads)
        if new_routes is not None:
            routes = [r for r in new_routes if r]
            loads = [rload(r) for r in routes]
            continue
        new_routes = try_swap(routes, loads)
        if new_routes is not None:
            routes = [r for r in new_routes if r]
            loads = [rload(r) for r in routes]
            continue
        break

    # Final intra-route cleanup.
    for _ in range(5):
        changed = False
        for i in range(len(routes)):
            nr, imp = best_two_opt(routes[i])
            if imp:
                routes[i] = nr
                changed = True
        if not changed:
            break

    # Defensive repair: if any route overloads due to unexpected data, split greedily.
    repaired = []
    for r in routes:
        if rload(r) <= capacity:
            repaired.append(r)
        else:
            cur = []
            cur_load = 0
            for x in r:
                dx = demands[x]
                if cur and cur_load + dx > capacity:
                    repaired.append(cur)
                    cur = [x]
                    cur_load = dx
                else:
                    cur.append(x)
                    cur_load += dx
            if cur:
                repaired.append(cur)
    routes = repaired

    # Ensure every customer appears exactly once: deterministic cleanup.
    seen = {}
    for r in routes:
        for x in r:
            seen[x] = seen.get(x, 0) + 1
    missing = [c for c in customers if seen.get(c, 0) == 0]
    if missing:
        # Insert missing customers into best feasible positions.
        for x in missing:
            best_choice = None
            best_inc = None
            for i in range(len(routes)):
                if loads[i] + demands[x] > capacity:
                    continue
                r = routes[i]
                for pos in range(len(r) + 1):
                    cand = r[:pos] + [x] + r[pos:]
                    inc = rcost(cand) - rcost(r)
                    if best_inc is None or inc < best_inc or (inc == best_inc and (i, pos, cand) < best_choice):
                        best_inc = inc
                        best_choice = (i, pos, cand)
            if best_choice is None:
                routes.append([x])
            else:
                i, pos, cand = best_choice
                routes[i] = cand
                loads[i] = rload(cand)

    # Remove duplicates by keeping first occurrence and re-inserting extras if needed.
    counts = {}
    cleaned = []
    for r in routes:
        nr = []
        for x in r:
            if counts.get(x, 0) == 0:
                counts[x] = 1
                nr.append(x)
        if nr:
            cleaned.append(nr)
    present = set()
    for r in cleaned:
        for x in r:
            present.add(x)
    for c in customers:
        if c not in present:
            placed = False
            for i in range(len(cleaned)):
                if rload(cleaned[i]) + demands[c] <= capacity:
                    best_pos = 0
                    best_inc = None
                    r = cleaned[i]
                    for pos in range(len(r) + 1):
                        cand = r[:pos] + [c] + r[pos:]
                        inc = rcost(cand) - rcost(r)
                        if best_inc is None or inc < best_inc or (inc == best_inc and pos < best_pos):
                            best_inc = inc
                            best_pos = pos
                    cleaned[i] = r[:best_pos] + [c] + r[best_pos:]
                    placed = True
                    break
            if not placed:
                cleaned.append([c])

    return cleaned
