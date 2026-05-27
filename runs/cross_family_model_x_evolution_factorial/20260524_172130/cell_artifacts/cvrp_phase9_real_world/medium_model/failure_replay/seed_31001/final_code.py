def solve_cvrp(instance):
    # instance expected as a dict with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': dict with 'id' (not to be used in routes)
    # - 'vehicle_capacity': int
    #
    # Deterministic constructive + repair + local-improvement heuristic
    # - Sort customers by some deterministic key (demand then id)
    # - Build initial feasible routes by greedily filling vehicles
    # - Repair by moving last assigned to next route if over capacity
    # - Local improvement: try to swap customers between routes if improves balance
    #
    # Output: list of routes, each is list of customer ids (no depot)

    customers = instance['customers']
    capacity = instance['vehicle_capacity']

    # Deterministic ordering: sort by (demand, id)
    ordered = sorted(customers, key=lambda c: (c['demand'], c['id']))

    # Helper: get demand by id map
    demand = {c['id']: c['demand'] for c in ordered}

    routes = []
    current_route = []
    current_load = 0

    # Constructive: greedy fill
    for c in ordered:
        d = c['demand']
        if d > capacity:
            # Skip impossible directly; to satisfy deterministic behavior, create solo route impossible -> still include as is
            # But per problem, assume feasible instance; if not, place as its own route
            routes.append([c['id']])
            current_route = []
            current_load = 0
            continue

        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            # close current route and start new
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Repair: ensure no route over capacity (defensive)
    repaired = []
    for r in routes:
        load = sum(demand[cid] for cid in r)
        if load <= capacity:
            repaired.append(r)
        else:
            # split overfull route deterministically into chunks of capacity
            chunk = []
            chunk_load = 0
            for cid in r:
                cid_d = demand[cid]
                if chunk_load + cid_d <= capacity:
                    chunk.append(cid)
                    chunk_load += cid_d
                else:
                    if chunk:
                        repaired.append(chunk)
                    chunk = [cid]
                    chunk_load = cid_d
            if chunk:
                repaired.append(chunk)
    routes = repaired

    # Local search: try to move a customer from a larger route to earlier one if capacity allows
    # Repeat small number of passes
    improved = True
    pass_limit = 5
    passes = 0
    while improved and passes < pass_limit:
        improved = False
        passes += 1
        for i in range(len(routes)):
            for j in range(len(routes)):
                if i == j or not routes[i]:
                    continue
                # try moving last of i to j
                mover = routes[i][-1]
                d = demand[mover]
                load_j = sum(demand[c] for c in routes[j])
                if load_j + d <= capacity:
                    # perform move
                    routes[i].pop()
                    routes[j].append(mover)
                    improved = True
                    break
            if improved:
                break

    return routes
