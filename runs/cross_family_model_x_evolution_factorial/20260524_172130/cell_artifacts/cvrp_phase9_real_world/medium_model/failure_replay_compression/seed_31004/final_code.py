def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - "depot": id of depot (not included in routes)
    # - "customers": list of customer ids (or dict with id and demand)
    # - "demands": dict mapping customer_id -> demand
    # - "capacities": vehicle capacity (int/float)
    # - "distance": function or dict to compute distance (not needed for feasibility)
    #
    # We implement a deterministic constructive solver with simple repair and local-improvement steps.
    # Strategy:
    # 1) Create a simple sequential sweep order of customers by id or by increasing id.
    # 2) Build routes by adding customers until capacity would be exceeded, then start new route.
    # 3) If a customer's demand exceeds a single vehicle's capacity, fail gracefully by placing it alone in a route (assumes capacity >= max demand).
    # 4) Do a small 2-opt-like local improvement by swapping adjacent customers between routes if feasible and improves nothing (deterministic improvement by simple reallocation).
    #
    # This is a straightforward, interpretable constructive method without external data.

    # Helper to extract data with defaults
    depot = instance.get("depot", 0)
    demands = instance.get("demands", {})
    customers = instance.get("customers", [])
    capacity = instance.get("capacity", instance.get("capacities", None))
    if capacity is None:
        # infer a default capacity if not provided
        capacity = max(demands.values()) if demands else 1

    # Normalize customers list to a deterministic order
    if isinstance(customers, dict):
        customer_ids = sorted(customers.keys())
    else:
        customer_ids = sorted(list(customers))

    # If demands are provided per id, ensure order
    customer_demands = {cid: demands.get(cid, 1) for cid in customer_ids}

    # Sanity: if there are no customers
    if not customer_ids:
        return []

    # Build initial routes greedily by capacity
    routes = []
    current_route = []
    current_load = 0

    for cid in customer_ids:
        d = customer_demands[cid]
        if d > capacity:
            # Cannot serve this single customer with given capacity; create a route with just this customer plus a note (but we must return feasible)
            # We place it alone; this assumes capacity >= d. If not, we still place it alone but it's infeasible; we skip without crashing.
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
            # close current route and start new
            routes.append(current_route)
            current_route = [cid]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Deterministic local repair: try to move a customer from one route to previous if feasible and keeps feasibility
    # We'll do a simple pass over adjacent route pairs and attempt to move the last customer of an earlier route to the next route if it doesn't violate capacity.
    changed = True
    while changed:
        changed = False
        for i in range(len(routes) - 1):
            if not routes[i]:
                continue
            moving = routes[i][-1]
            d = customer_demands[moving]
            # capacity of next route
            load_next = sum(customer_demands[c] for c in routes[i+1])
            if load_next + d <= capacity:
                # move
                routes[i].pop()
                routes[i+1].insert(0, moving)
                changed = True
                # remove empty route if becomes empty
                if not routes[i]:
                    routes.pop(i)
                break

    # Small inter-route swap to improve locality: try swapping front of next route with end of current if both feasible
    improved = True
    while improved:
        improved = False
        for i in range(len(routes) - 1):
            if not routes[i] or not routes[i+1]:
                continue
            a = routes[i][-1]
            b = routes[i+1][0]
            da = customer_demands[a]
            db = customer_demands[b]
            # check feasibility after swap
            load_i = sum(customer_demands[c] for c in routes[i])
            load_i_next = sum(customer_demands[c] for c in routes[i+1])
            # after swap: i loses a, gains b; i+1 loses b, gains a
            new_load_i = load_i - da + db
            new_load_next = load_i_next - db + da
            if new_load_i <= capacity and new_load_next <= capacity:
                routes[i].pop()
                routes[i+1].insert(0, a)
                routes[i+1].pop(0)
                routes[i+1].insert(0, b)
                improved = True
                break

    # Final cleanup: remove any empty routes (if any)
    routes = [r for r in routes if r]

    return routes
