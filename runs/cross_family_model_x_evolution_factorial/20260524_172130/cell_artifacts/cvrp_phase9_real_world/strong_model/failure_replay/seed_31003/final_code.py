def solve_cvrp(instance):
    def g(o, ks, d=None):
        try:
            for k in ks:
                try:
                    return o[k]
                except:
                    pass
        except:
            pass
        try:
            dd = o.__dict__
            for k in ks:
                if k in dd:
                    return dd[k]
        except:
            pass
        return d

    depot = g(instance, ("depot", "depot_id", "start", "origin"), 0)
    cap = g(instance, ("capacity", "vehicle_capacity", "cap"), None)
    dist = g(instance, ("distance_matrix", "distances", "matrix"), None)
    coords = g(instance, ("coords", "coordinates", "points"), None)
    dem = g(instance, ("demands", "demand"), None)
    cust = g(instance, ("customers", "customer_ids", "nodes"), None)

    if cust is None:
        if dem is not None:
            try:
                cust = [k for k in dem if k != depot]
            except:
                cust = list(range(len(dem)))
                if depot in cust:
                    cust.remove(depot)
        elif dist is not None:
            cust = list(range(len(dist)))
            if depot in cust:
                cust.remove(depot)
        elif coords is not None:
            cust = list(range(len(coords)))
            if depot in cust:
                cust.remove(depot)
        else:
            return []

    cust = [c for c in cust if c != depot]

    D = {}
    if dem is not None:
        try:
            for k in dem:
                D[k] = dem[k]
        except:
            for i, v in enumerate(dem):
                D[i] = v
    for c in cust:
        if c not in D:
            D[c] = 1
    D[depot] = 0

    P = None
    if coords is not None:
        P = {}
        try:
            for k in coords:
                P[k] = coords[k]
        except:
            for i, v in enumerate(coords):
                P[i] = v

    def dis(i, j):
        if dist is not None:
            try:
                return dist[i][j]
            except:
                try:
                    return dist[i, j]
                except:
                    pass
        if P is not None:
            a, b = P[i], P[j]
            x = a[0] - b[0]
            y = a[1] - b[1]
            return (x * x + y * y) ** 0.5
        return 0 if i == j else 1

    if cap is None:
        cap = 0
        for c in cust:
            cap += D[c]
        if cap <= 0:
            cap = 1

    if not cust:
        return []

    if P is not None and depot in P:
        x0, y0 = P[depot]
        order = sorted(cust, key=lambda c: ((P[c][1] - y0), (P[c][0] - x0), c))
    else:
        order = sorted(cust, key=lambda c: (dis(depot, c), c))

    routes, r, load = [], [], 0
    for c in order:
        q = D[c]
        if r and load + q > cap:
            routes.append(r)
            r, load = [c], q
        else:
            r.append(c)
            load += q
    if r:
        routes.append(r)

    def loadr(rt):
        s = 0
        for x in rt:
            s += D[x]
        return s

    def cost(rt):
        if not rt:
            return 0
        t = dis(depot, rt[0]) + dis(rt[-1], depot)
        for a, b in zip(rt, rt[1:]):
            t += dis(a, b)
        return t

    def two_opt(rt):
        n = len(rt)
        if n < 4:
            return rt[:]
        best = rt[:]
        bc = cost(best)
        imp = True
        while imp:
            imp = False
            for i in range(n - 2):
                for k in range(i + 2, n):
                    if i == 0 and k == n - 1:
                        continue
                    cand = best[:i + 1] + best[i + 1:k + 1][::-1] + best[k + 1:]
                    cc = cost(cand)
                    if cc + 1e-12 < bc:
                        best, bc, imp = cand, cc, True
                        break
                if imp:
                    break
        return best

    routes = [two_opt(rt) for rt in routes if rt]
    if not routes:
        routes = [[c] for c in order]

    changed = True
    while changed:
        changed = False
        best = None
        gain = 0
        m = len(routes)
        for i in range(m):
            A = routes[i]
            la = loadr(A)
            for j in range(i + 1, m):
                B = routes[j]
                lb = loadr(B)
                if la + lb > cap:
                    continue
                cand = [A + B, B + A, A[::-1] + B, A + B[::-1], B[::-1] + A, B + A[::-1], A[::-1] + B[::-1], B[::-1] + A[::-1]]
                base = cost(A) + cost(B)
                for x in cand:
                    if loadr(x) <= cap:
                        g2 = base - cost(x)
                        if g2 > gain + 1e-12:
                            gain = g2
                            best = (i, j, x)
        if best:
            i, j, x = best
            routes[i] = two_opt(x)
            routes[j] = []
            routes = [rt for rt in routes if rt]
            changed = True

    imp = True
    while imp:
        imp = False
        best = None
        bestd = 0
        for i in range(len(routes)):
            A = routes[i]
            la = loadr(A)
            for p, c in enumerate(A):
                qc = D[c]
                pa = depot if p == 0 else A[p - 1]
                na = depot if p == len(A) - 1 else A[p + 1]
                rem = dis(pa, na) - dis(pa, c) - dis(c, na)
                for j in range(len(routes)):
                    B = routes[j]
                    for q in range(len(B) + 1):
                        if i == j and (q == p or q == p + 1):
                            continue
                        lb = loadr(B)
                        if i != j and lb + qc > cap:
                            continue
                        pb = depot if q == 0 else B[q - 1]
                        nb = depot if q == len(B) else B[q]
                        add = dis(pb, c) + dis(c, nb) - dis(pb, nb)
                        dlt = rem + add
                        if dlt < bestd - 1e-12:
                            bestd = dlt
                            best = (i, j, p, q, c)
        if best:
            i, j, p, q, c = best
            if i == j:
                rt = routes[i]
                node = rt.pop(p)
                if q > p:
                    q -= 1
                rt.insert(q, node)
                routes[i] = two_opt(rt)
            else:
                A = routes[i][:]
                B = routes[j][:]
                node = A.pop(p)
                B.insert(q, node)
                routes[i] = two_opt(A)
                routes[j] = two_opt(B)
            imp = True

    seen = {}
    out = []
    for rt in routes:
        nr = []
        for c in rt:
            if c != depot and not seen.get(c, 0):
                seen[c] = 1
                nr.append(c)
        if nr:
            out.append(nr)

    miss = [c for c in cust if not seen.get(c, 0)]
    for c in miss:
        placed = False
        q = D[c]
        besti = bestp = None
        bestinc = None
        for i, rt in enumerate(out):
            if loadr(rt) + q > cap:
                continue
            for p in range(len(rt) + 1):
                a = depot if p == 0 else rt[p - 1]
                b = depot if p == len(rt) else rt[p]
                inc = dis(a, c) + dis(c, b) - dis(a, b)
                if bestinc is None or inc < bestinc - 1e-12 or (inc == bestinc and (i, p) < (besti, bestp)):
                    bestinc, besti, bestp = inc, i, p
        if besti is None:
            out.append([c])
        else:
            out[besti].insert(bestp, c)

    return out
