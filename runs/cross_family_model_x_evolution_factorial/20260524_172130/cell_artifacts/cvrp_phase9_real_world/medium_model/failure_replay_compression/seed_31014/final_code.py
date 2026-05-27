def solve_cvrp(instance):
    # Instance format assumptions:
    # instance is a dict with:
    # - 'customers': list of dicts with 'id', 'demand' (int), 'x','y' (optional)
    # - 'depot': dict with 'id' (optional), or assume depot id 0
    # - 'vehicle_capacity': int
    #
    # The solver follows a deterministic constructive + simple repair + local-improvement approach
    # without any external data or imports.

    # Extract basic data
    customers = []
    if isinstance(instance.get('customers'), list):
        customers = instance['customers']
    else:
        return []
    depot_id = instance.get('depot', {}).get('id', 0)
    capacity = instance.get('vehicle_capacity', 0)

    # Create a simple utility to get demand safely
    def demand_of(cid):
        for c in customers:
            if c.get('id') == cid:
                return int(c.get('demand', 0))
        return 0

    # If capacity invalid or no customers, return empty routes
    if capacity <= 0 or not customers:
        return []

    # Build a deterministic order: sort by id to ensure determinism
    sorted_customers = sorted(customers, key=lambda c: c.get('id', 0))

    # Simple distance heuristic helper (no imports)
    def dist(a, b):
        ax = a.get('x', 0)
        ay = a.get('y', 0)
        bx = b.get('x', 0)
        by = b.get('y', 0)
        dx = ax - bx
        dy = ay - by
        return (dx*dx + dy*dy) ** 0.5

    # Map id to node
    id_to_node = {c['id']: c for c in customers}
    depot = {'id': depot_id, 'x': 0, 'y': 0}

    # Simple local construction: repeatedly fill a route with closest-unfserved
    remaining = [c for c in sorted_customers]
    routes = []

    # Mark all as unvisited
    visited = set()

    while len(visited) < len(remaining):
        # Start a new route from depot
        route = []
        load = 0
        # Pick the nearest unvisited to the depot to start
        candidates = [c for c in remaining if c['id'] not in visited]
        if not candidates:
            break
        # Start with the closest to depot
        current = min(candidates, key=lambda c: dist(depot, c))
        if demand_of(current['id']) > capacity:
            # If a single customer exceeds capacity, skip (unfeasible); break
            # In this deterministic simple solver, drop such customer as impossible
            visited.add(current['id'])
            continue
        route.append(current['id'])
        load += demand_of(current['id'])
        visited.add(current['id'])

        # Keep adding nearest neighbor unvisited while capacity allows
        while True:
            candidates = [c for c in remaining if c['id'] not in visited]
            if not candidates:
                break
            # Find nearest to the last added node
            last_node = id_to_node[route[-1]]
            next_c = min(candidates, key=lambda c: dist(last_node, c))
            d = demand_of(next_c['id'])
            if load + d > capacity:
                break
            route.append(next_c['id'])
            load += d
            visited.add(next_c['id'])

        routes.append(route)

    # Repair step: ensure all customers covered
    all_ids = set(c['id'] for c in customers)
    routed_ids = set(cid for r in routes for cid in r)
    missing = list(all_ids - routed_ids)
    if missing:
        # Try to attach missing customers to existing routes where capacity permits
        # Keep deterministic order
        for mid in sorted(missing):
            md = demand_of(mid)
            placed = False
            # Try to insert into any route at best position (after some node) without violating capacity
            for r_idx, route in enumerate(routes):
                # current load
                load = sum(demand_of(cid) for cid in route)
                if load + md <= capacity:
                    # append to this route
                    route.append(mid)
                    placed = True
                    break
            if not placed:
                # create a new route for this single customer
                routes.append([mid])

    # Post-process: ensure no route empty and all customers present
    # Final check
    final_ids = set()
    for r in routes:
        if not r:
            continue
        final_ids.update(r)
    # If still missing, create singleton routes
    if final_ids != all_ids:
        missing_all = sorted(all_ids - final_ids)
        for mid in missing_all:
            routes.append([mid])

    # Optional simple local-improvement: try to swap between routes to reduce total distance
    # Deterministic small improvement: attempt to move a tail customer from a longer route to earlier route if capacity allows
    improved = True
    while improved:
        improved = False
        # Compute simple cost function: sum of pairwise consecutive distances in each route (ignoring start/end at depot for simplicity)
        def route_cost(r):
            if len(r) <= 1:
                return 0
            total = 0
            for i in range(len(r)-1):
                a = id_to_node[r[i]]
                b = id_to_node[r[i+1]]
                total += dist(a, b)
            return total
        best_cost = sum(route_cost(r) for r in routes)
        # Try moving last element of a route to another route if feasible
        for i in range(len(routes)):
            if len(routes[i]) <= 0:
                continue
            cand = routes[i][-1]
            cand_d = demand_of(cand)
            # Try to move to any route j != i
            for j in range(len(routes)):
                if i == j:
                    continue
                load_j = sum(demand_of(cid) for cid in routes[j])
                if load_j + cand_d <= capacity:
                    # perform move
                    new_routes = [list(r) for r in routes]
                    new_routes[i] = new_routes[i][:-1]
                    new_routes[j] = new_routes[j] + [cand]
                    new_cost = sum(route_cost(r) for r in new_routes)
                    if new_cost < best_cost:
                        routes = new_routes
                        improved = True
                        best_cost = new_cost
                        break
            if improved:
                break

    # Final: remove any empty routes
    routes = [r for r in routes if r]
    return routes
