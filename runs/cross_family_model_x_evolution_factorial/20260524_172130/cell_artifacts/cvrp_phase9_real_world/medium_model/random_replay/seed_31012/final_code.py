def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'depot': id (not to be included in routes)
    # - 'capacity': vehicle capacity
    # For determinism, we sort customers by id and apply a simple constructive heuristic:
    # 1. Start new route from lowest-id unassigned customer
    # 2. Greedily append the nearest-available customer that fits remaining capacity and is not yet assigned
    # 3. When no more fits, start a new route
    #
    # This is a simple constructive solver with deterministic behavior (no randomness).
    customers = instance.get('customers', [])
    depot = instance.get('depot', 0)
    capacity = instance.get('capacity', 0)

    # Build simple distance heuristic using ids as proxy for distance (deterministic proxy).
    # We don't include the depot in routes; only customer ids.
    # Prepare data structures
    customer_by_id = {}
    for c in customers:
        cid = c['id']
        demand = c.get('demand', 0)
        customer_by_id[cid] = {'id': cid, 'demand': demand}

    # Ensure deterministic order: sort by id
    all_ids = sorted(customer_by_id.keys())

    unassigned = set(all_ids)
    routes = []

    while unassigned:
        # Start a new route with the smallest id remaining
        first = min(unassigned)
        route = [first]
        remaining_capacity = capacity - customer_by_id[first]['demand']
        unassigned.remove(first)

        # Try to fill route by greedily adding compatible customers
        while True:
            # Consider candidates in sorted order to keep determinism
            candidates = [cid for cid in sorted(unassigned)]
            best_next = None
            best_score = None

            for cid in candidates:
                d = customer_by_id[cid]['demand']
                if d <= remaining_capacity:
                    # Simple score: prefer smaller id to keep deterministic
                    score = -cid  # smaller id -> higher score when maximizing
                    if best_score is None or score > best_score:
                        best_score = score
                        best_next = cid

            if best_next is None:
                break  # no fit
            # Add to route
            route.append(best_next)
            remaining_capacity -= customer_by_id[best_next]['demand']
            unassigned.remove(best_next)

        routes.append(route)

    return routes
