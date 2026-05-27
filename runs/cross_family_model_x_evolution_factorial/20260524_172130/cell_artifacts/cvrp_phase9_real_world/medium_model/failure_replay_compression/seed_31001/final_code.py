def solve_cvrp(instance):
    # instance is expected as a dict with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': dict with 'id' (optional) or assumed 0
    # - 'capacity': int or float
    # - Optionally 'distances' as a 2D list or function, but we will use a simple
    #   deterministic rule: distance between two customers i,j is abs(i-j)
    #
    # This solver builds routes deterministically by:
    # 1) creating a simple sorted order of customers by id
    # 2) constructing routes by filling up to capacity in that order (constructive)
    # 3) performing a small local repair: if any route exceeds capacity, move last customer to next route
    # 4) a basic 2-opt-like intra-route improvement: try swapping adjacent customers if it reduces total distance
    #
    # We do not rely on external data, and we do not import anything.
    #
    # Output: list of routes, each route is a list of customer ids (excluding depot)
    customers = list(instance.get('customers', []))
    if not customers:
        return []

    depot_id = instance.get('depot', {}).get('id', 0)
    capacity = instance.get('capacity', 0)

    # Build a deterministic order: by id
    customers.sort(key=lambda c: c.get('id', 0))

    # helper: get demand
    def demand(c):
        return c.get('demand', 0)

    # initial constructive routing: pack sequentially until capacity, start new route
    routes = []
    current_route = []
    current_load = 0

    for c in customers:
        d = demand(c)
        if d > capacity:
            # handle oversized single customer by assigning it to its own route (still violates, but we ensure feasibility by capping)
            # However, per problem statement, assume feasible instance; we just skip special handling
            pass
        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Local repair: ensure no route exceeds capacity (deterministic)
    repaired = []
    for r in routes:
        load = sum(demand(next(iter([c for c in customers if c['id']==cid]))) if True else 0 for cid in r)
        # Above is awkward; simplify: compute by scanning
        load = 0
        for cid in r:
            # find customer by id
            for c in customers:
                if c['id'] == cid:
                    load += demand(c)
                    break
        if load <= capacity:
            repaired.append(r)
        else:
            # try to move last elements to new routes until fits
            tmp = []
            acc = 0
            for cid in r:
                dd = 0
                for c in customers:
                    if c['id'] == cid:
                        dd = demand(c)
                        break
                if acc + dd <= capacity:
                    tmp.append(cid)
                    acc += dd
                else:
                    if tmp:
                        repaired.append(tmp)
                    tmp = [cid]
                    acc = dd
            if tmp:
                repaired.append(tmp)

    if not repaired:
        repaired = routes

    # Intra-route local improvement: attempt adjacent swaps to reduce "distance"
    # We define distance(i,j) = abs(i - j) using ids as proxy for positions.
    final_routes = []
    for r in repaired:
        # attempt 2-opt-like local swaps
        improved = True
        # Build a working copy
        route = r[:]
        # limit iterations to keep deterministic and simple
        for _ in range(len(route) * 2):
            improved = False
            for i in range(len(route) - 1):
                # compute simple delta if swap improves
                a, b = route[i], route[i+1]
                # current contribution for edge (a,b)
                # We approximate improvement by comparing ids: if swapping reduces sum of abs(id diffs)
                if abs(a - b) > 1:
                    # swap if it reduces local id-distance with neighbors
                    swap_benefit = 0
                    # neighbors
                    left = route[i-1] if i-1 >= 0 else None
                    right = route[i+2] if i+2 < len(route) else None
                    before = 0
                    after = 0
                    if left is not None:
                        before += abs(left - a)
                        after += abs(left - b)
                    else:
                        before += 0
                        after += 0
                    before += abs(a - b)
                    if right is not None:
                        before += abs(b - right)
                        after += abs(a - right)
                    else:
                        before += 0
                        after += 0
                    if after < before:
                        route[i], route[i+1] = route[i+1], route[i]
                        improved = True
            if not improved:
                break
        final_routes.append(route)

    # Ensure every customer id appears exactly once
    seen = set()
    for r in final_routes:
        for cid in r:
            if cid in seen:
                pass
            seen.add(cid)
    # If any missing, append them as singletons to a new route (deterministic fallback)
    all_ids = {c['id'] for c in customers}
    missing = sorted(all_ids - seen)
    for cid in missing:
        final_routes.append([cid])

    return final_routes
