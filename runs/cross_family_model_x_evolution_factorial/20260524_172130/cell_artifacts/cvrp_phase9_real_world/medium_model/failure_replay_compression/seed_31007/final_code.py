def solve_cvrp(instance):
    # instance is expected to be a dict with:
    # - 'customers': list of dicts with 'id', 'x', 'y', 'demand'
    # - 'depot': dict with 'id', 'x', 'y' (not included in routes)
    # - 'vehicle_capacity': int
    #
    # Deterministic constructive + simple repair + local-improvement:
    # 1) Sort customers by a simple heuristic: ascending demand, then by id.
    # 2) Build routes by repeatedly filling the current route until capacity would be exceeded.
    # 3) If any customer alone exceeds capacity, place them in their own route (robust handling).
    # 4) Apply a simple 2-opt style intra-route improvement by swapping adjacent customers if it reduces distance (deterministic pass).
    # 5) Do a final simple cross-route merge check: try to move a customer from a longer route to a shorter feasible route if it reduces total distance.
    #
    # Note: Depot is not included in routes per requirement.
    customers = instance.get('customers', [])
    depot = instance.get('depot', None)
    capacity = instance.get('vehicle_capacity', 0)

    # Helper: distance between two points
    def dist(a, b):
        return ((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2) ** 0.5

    # Build quick access maps
    cust_by_id = {c['id']: c for c in customers}
    # Sorting: by demand then id to ensure deterministic order
    sorted_ids = sorted([c['id'] for c in customers], key=lambda cid: (cust_by_id[cid]['demand'], cid))

    # Create initial routes by greedy packing
    routes = []
    current_route = []
    current_load = 0

    for cid in sorted_ids:
        d = cust_by_id[cid]['demand']
        if d > capacity:
            # Create a dedicated route for this over-capacity customer (edge-case)
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([cid])
            continue

        if current_load + d <= capacity:
            current_route.append(cid)
            current_load += d
        else:
            # finish current route and start new
            routes.append(current_route)
            current_route = [cid]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Intra-route 2-opt-like improvement (deterministic)
    # For each route, try adjacent swaps if they reduce route length (compared to apex distance from depot through route)
    # We approximate route distance as sum distances between consecutive points, ignoring depot return (per problem statement it's not required to return to depot)
    if depot is None:
        depot_point = {'x': 0, 'y': 0}
    else:
        depot_point = depot

    # Precompute distance helper for points (including depot)
    def point(c_id):
        return cust_by_id[c_id]

    def route_distance(route):
        if not route:
            return 0.0
        total = 0.0
        prev = depot_point
        for cid in route:
            cur = point(cid)
            total += dist(prev, cur)
            prev = cur
        return total

    for r_idx, route in enumerate(routes):
        improved = True
        # Limit iterations to length of route to ensure determinism
        while improved:
            improved = False
            L = len(route)
            if L < 2:
                break
            # try all adjacent swaps deterministically
            best_delta = 0.0
            best_pos = None
            orig_dist = route_distance(route)
            for i in range(L - 1):
                new_route = route[:]
                new_route[i], new_route[i+1] = new_route[i+1], new_route[i]
                new_dist = route_distance(new_route)
                delta = new_dist - orig_dist
                if delta < best_delta:
                    best_delta = delta
                    best_pos = i
            if best_pos is not None:
                route[best_pos], route[best_pos+1] = route[best_pos+1], route[best_pos]
                improved = True

    # Simple cross-route repair: try moving a single customer to a different route if decreases total distance
    # Do a single pass over all customers in order to keep deterministic behavior
    def total_distance(all_routes):
        total = 0.0
        for rt in all_routes:
            total += route_distance(rt)
        return total

    improved = True
    while improved:
        improved = False
        # compute current total
        current_routes = routes
        n_routes = len(current_routes)
        # attempt moves
        for si in range(n_routes):
            rt_from = current_routes[si]
            if not rt_from:
                continue
            for ci in range(len(rt_from)):
                cid = rt_from[ci]
                d = cust_by_id[cid]['demand']
                # try to move to another route if capacity allows
                for tj in range(n_routes):
                    if tj == si:
                        continue
                    rt_to = current_routes[tj]
                    sum_to = sum(cust_by_id[c2]['demand'] for c2 in rt_to)
                    if sum_to + d <= capacity:
                        # perform move
                        new_rt_from = rt_from[:ci] + rt_from[ci+1:]
                        new_rt_to = rt_to[:] + [cid]
                        new_routes = current_routes[:]
                        new_routes[si] = new_rt_from
                        new_routes[tj] = new_rt_to
                        # remove empty routes
                        new_routes = [r for r in new_routes if r]
                        if total_distance(new_routes) < total_distance(current_routes):
                            routes = new_routes
                            improved = True
                            break
                if improved:
                    break
            if improved:
                break

    # Final cleanup: ensure no empty routes and all customers present
    seen = set()
    for r in routes:
        for cid in r:
            seen.add(cid)
    # Add any missing customers (defensive)
    all_ids = set([c['id'] for c in customers])
    missing = sorted(all_ids - seen, key=lambda cid: (cust_by_id[cid]['demand'], cid))
    for cid in missing:
        if not routes:
            routes.append([cid])
        else:
            # try to append to first route if capacity allows
            d = cust_by_id[cid]['demand']
            if sum(cust_by_id[x]['demand'] for x in routes[0]) + d <= capacity:
                routes[0].append(cid)
            else:
                routes.append([cid])

    return routes
