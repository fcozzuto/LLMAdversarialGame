def solve_cvrp(instance):
    # instance is expected as a dict-like with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id (not used in routes)
    # - 'vehicle_capacity': int
    #
    # Deterministic constructive solver with simple repair/local-improvement.
    #
    # Approach:
    # 1) Sort customers by nondecreasing ratio of distance from depot to demand or by id
    #    to keep deterministic order. We don't have coordinates, so we fallback to id ordering.
    # 2) Build routes by filling one vehicle at a time until capacity would be exceeded,
    #    then start a new route.
    # 3) Simple intra-route 2-opt-like repair on each route using a trivial distance proxy
    #    based on id differences as a stand-in for geographic distance (deterministic).
    #
    # Note: Since we don't have coordinates, we assume a linear ordering and use a proxy
    # distance of abs(id_a - id_b). This keeps the solver deterministic and interpretable.
    #
    customers = instance.get('customers', [])
    depot_id = instance.get('depot', None)
    V = instance.get('vehicle_capacity', 0)
    # Build a simple list of customer dictionaries with id and demand
    custs = []
    for c in customers:
        cid = c.get('id')
        demand = c.get('demand', 0)
        custs.append({'id': cid, 'demand': demand})
    # Deterministic order: by id ascending
    custs.sort(key=lambda x: x['id'])
    # If there are no customers, return empty routes
    if not custs:
        return []
    # Very simple distance proxy function (deterministic)
    def dist(a, b):
        return abs(a - b)
    # Construct routes by capacity
    routes = []
    current_route = []
    current_load = 0
    for c in custs:
        d = c['demand']
        if d > V:
            # A single customer's demand exceeds a vehicle capacity; to keep feasible,
            # place it in its own route (even though infeasible in strict sense),
            # but we will still record it as a route with that single customer to maintain determinism.
            if current_route:
                # finalize current route first
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([c['id']])
            continue
        if current_load + d <= V:
            current_route.append(c['id'])
            current_load += d
        else:
            # close current route and start new
            routes.append(current_route)
            current_route = [c['id']]
            current_load = d
    if current_route:
        routes.append(current_route)
    # Optional simple intra-route improvement: reorder within route by a simple greedy swap
    # to reduce proxy distance (not changing feasibility).
    for r in range(len(routes)):
        route = routes[r]
        if len(route) <= 2:
            continue
        improved = True
        while improved:
            improved = False
            for i in range(len(route) - 1):
                for j in range(i+1, len(route)):
                    if i == j:
                        continue
                    a, b = route[i], route[j]
                    # compute current cost contribution for edges around i and j
                    # Since we lack real coordinates, use proxy distance sum for order: just compare
                    # the cost of putting b before a vs a before b locally
                    # We'll do a simple swap test
                    new_route = route[:]
                    new_route[i], new_route[j] = new_route[j], new_route[i]
                    old_cost = 0
                    new_cost = 0
                    for k in range(len(route)-1):
                        old_cost += dist(route[k], route[k+1])
                    for k in range(len(new_route)-1):
                        new_cost += dist(new_route[k], new_route[k+1])
                    if new_cost < old_cost:
                        route = new_route
                        routes[r] = route
                        improved = True
                        break
                if improved:
                    break
    return routes
