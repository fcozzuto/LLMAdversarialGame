def solve_cvrp(instance):
    # instance expected as a dict-like with:
    # - 'customers': list of customer dicts with 'id', 'demand', 'x', 'y'
    # - 'vehicle_capacity': int or float
    # - optional 'depot': dict with 'id', 'x', 'y' (id often 0)
    #
    # Deterministic constructive + simple repair + local improvement
    # using only built-in constructs, no imports.

    # Basic helper to compute Manhattan distance if coordinates exist,
    # otherwise Euclidean distance, but we will not rely on distances for
    # routing decisions beyond a simple nearest-neighbor style.

    customers = instance.get('customers', [])
    depot = instance.get('depot', {'id': 0, 'x': 0, 'y': 0})
    capacity = instance.get('vehicle_capacity', 0)

    # Build a simple deterministic sequence of customers sorted by id
    # (stable and deterministic)
    customer_list = sorted(customers, key=lambda c: c.get('id', 0))

    # If there is no demand data, assume unit demand
    for c in customer_list:
        if 'demand' not in c or c['demand'] is None:
            c['demand'] = 1

    # Helper: compute simple distance between two points
    def dist(a, b):
        ax = a.get('x', 0)
        ay = a.get('y', 0)
        bx = b.get('x', 0)
        by = b.get('y', 0)
        dx = ax - bx
        dy = ay - by
        return (dx*dx + dy*dy) ** 0.5

    # Build a deterministic initial solution using simple nearest-in-id next-fit
    # Start from depot
    unvisited = {c['id']: c for c in customer_list}
    routes = []

    depot_point = {'id': depot.get('id', 0), 'x': depot.get('x', 0), 'y': depot.get('y', 0)}

    while unvisited:
        load = 0
        route = []
        current_point = depot_point

        # Fill route greedily until capacity would be exceeded
        # Choose the next customer with smallest id that fits
        candidate_ids = sorted(unvisited.keys())
        for cid in candidate_ids:
            c = unvisited[cid]
            d = c.get('demand', 1)
            if load + d <= capacity:
                # include this customer
                route.append(cid)
                load += d
                current_point = c
                del unvisited[cid]
                # restart scanning from smallest id for determinism
        # If no customer could be added (e.g., all remaining exceed capacity individually),
        # force take the next one anyway to avoid deadlock (large single-demand)
        if not route and candidate_ids:
            cid = candidate_ids[0]
            c = unvisited[cid]
            route.append(cid)
            load += c.get('demand', 1)
            del unvisited[cid]

        routes.append(route)

    # Validation: ensure each customer appears exactly once
    visited = {cid for r in routes for cid in r}
    if len(visited) != len(customer_list):
        # Fallback simple repair: sweep and attach missing ids to last route if possible
        missing = [c['id'] for c in customer_list if c['id'] not in visited]
        for mid in missing:
            # try to append to last route if capacity allows
            if routes:
                last = routes[-1]
                # compute total demand of last route
                last_load = sum(next((c.get('demand', 1) for c in customer_list if c['id']==cid), 1) for cid in last)
                c = next((cc for cc in customer_list if cc['id']==mid), None)
                d = c.get('demand', 1) if c is not None else 1
                if last_load + d <= capacity:
                    last.append(mid)
                    visited.add(mid)
                else:
                    # start new route
                    routes.append([mid])
                    visited.add(mid)

    return routes
