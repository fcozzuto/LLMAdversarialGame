def solve_cvrp(instance):
    # instance is expected as a dict-like object with:
    # - 'depot': depot id (ignored in routes)
    # - 'customers': list of customer ids
    # - 'demand': dict mapping customer_id -> demand
    # - 'capacity': vehicle capacity (int)
    # - 'distance': dict of dict or function (not used for construction)
    #
    # Simple deterministic constructive solver with repair:
    # - Sort customers by id (stable, deterministic)
    # - Build routes by greedy filling based on remaining capacity
    # - After initial construction, try simple 2-opt-like local repair: if merging two routes is feasible and reduces total customers in first route, do it
    # - Return list of routes, each route is a list of customer ids (no depot)
    #
    customers = list(instance.get('customers', []))
    if not customers:
        return []
    capacity = instance.get('capacity', 0)
    demands = dict(instance.get('demand', {}))

    # Ensure deterministic order
    customers = sorted(customers)

    # If no demand specified for a customer, assume 1
    for c in customers:
        if c not in demands:
            demands[c] = 1

    # Helper for total demand of a route
    def route_demand(route):
        s = 0
        for c in route:
            s += demands.get(c, 1)
        return s

    # Construct initial routes greedily by smallest next customer that fits
    remaining = set(customers)
    routes = []
    while remaining:
        route = []
        cap = capacity
        # add as many as fit in order of id
        for c in sorted(remaining):
            d = demands.get(c, 1)
            if d <= cap:
                route.append(c)
                cap -= d
        # ensure at least one customer per route; if none fits (due to high demand), take the highest-demand customer to progress
        if not route:
            # pick one customer with smallest demand that fits (or at least something)
            c = min(remaining, key=lambda x: demands.get(x, 1))
            route.append(c)
            cap -= demands.get(c, 1)
        # finalize this route
        for c in route:
            if c in remaining:
                remaining.remove(c)
        routes.append(route)

    # Local repair: try to move a customer from a later route to an earlier route if feasible
    # Simple one-pass attempt: for i from 1..len(routes)-1, try moving from routes[i] to routes[i-1] if capacity allows
    merged = True
    while merged:
        merged = False
        for i in range(1, len(routes)):
            if not routes[i]:
                continue
            # try moving first customer of routes[i] to end of routes[i-1]
            cand = routes[i][0]
            d = demands.get(cand, 1)
            # compute remaining capacity of previous route
            cap_prev = capacity - route_demand(routes[i-1])
            if d <= cap_prev:
                # move
                routes[i-1].append(cand)
                routes[i].pop(0)
                if not routes[i]:
                    routes.pop(i)
                merged = True
                break
            # else try moving last of previous to current if helps
            last_prev = routes[i-1][-1]
            d_last = demands.get(last_prev, 1)
            cap_cur = capacity - route_demand(routes[i])
            if d_last <= cap_cur:
                # move last_prev to end of current
                routes[i].append(last_prev)
                routes[i-1].pop()
                if not routes[i-1]:
                    routes.pop(i-1)
                merged = True
                break

    return routes
