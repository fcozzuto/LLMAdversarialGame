def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'customers': list of dicts with 'id' and 'demand'
    # - 'depot': id (not included in routes)
    # - 'vehicle_capacity': int
    #
    # Deterministic constructive heuristic with simple local repair:
    # - sort customers by nondecreasing id (stable, deterministic)
    # - greedily build routes by filling up to capacity
    # - then attempt a simple 2-opt style intra-route improvement by swapping adjacent customers if it reduces distance (using a provided distance function)
    #
    # Since no imports are allowed, define a simple distance using ids as coordinates proxy:
    # distance between customers i and j is abs(i - j) (deterministic and simple)
    #
    # Note: This is a minimal, deterministic solver that ensures each customer is visited exactly once.
    #
    depot = instance.get('depot', 0)
    customers = instance.get('customers', [])
    capacity = instance.get('vehicle_capacity', 0)
    if not isinstance(customers, list) or capacity <= 0:
        return []
    # Build a map from id to demand
    id_to_demand = {}
    for c in customers:
        cid = c.get('id')
        dem = c.get('demand', 0)
        id_to_demand[cid] = dem
    # Sort customer ids deterministically
    customer_ids = sorted([c['id'] for c in customers])
    # Construct routes by greedy packing
    routes = []
    i = 0
    while i < len(customer_ids):
        load = 0
        route = []
        # pack as many as fit
        while i < len(customer_ids):
            cid = customer_ids[i]
            d = id_to_demand.get(cid, 0)
            if load + d <= capacity:
                route.append(cid)
                load += d
                i += 1
            else:
                break
        if route:
            routes.append(route)
        else:
            # If a single customer exceeds capacity, place it alone (defensive)
            cid = customer_ids[i]
            routes.append([cid])
            i += 1
    # Local improvement: intra-route swap of adjacent customers if distance-improving
    def dist(a, b):
        return abs(a - b)
    for r in range(len(routes)):
        route = routes[r]
        improved = True
        while improved:
            improved = False
            for k in range(len(route) - 1):
                a, b = route[k], route[k+1]
                # compute current cost for the two edges around the swap
                before = dist(a, b)  # inside the pair
                # after swap cost between neighbors
                after = dist(a, route[k-1]) if k-1 >= 0 else 0
                after += dist(b, route[k+2]) if k+2 < len(route) else 0
                # simpler: compare total pair distance vs swapped
                if k+2 < len(route):
                    before_total = dist(a, b) + dist(route[k+1], route[k+2])
                    after_total = dist(route[k], route[k+1]) + dist(a, b)  # incorrect, adjust properly
                    # To keep deterministic simple, perform basic adjacent swap if it reduces dist between swapped neighbors
                    # compute full segment cost before swap and after swap for the two edges around k
                # Implement straightforward local check:
                    pass
            # Implement a simple greedy improvement: try swapping any adjacent pair if sum of distances with their neighbors decreases
            swapped_any = False
            for idx in range(len(route) - 1):
                a = route[idx]
                b = route[idx+1]
                left = dist(route[idx-1], a) if idx-1 >= 0 else 0
                between = dist(a, b)
                right = dist(b, route[idx+2]) if idx+2 < len(route) else 0
                left_swap = dist(route[idx-1], b) if idx-1 >= 0 else 0
                between_swap = dist(b, a)
                right_swap = dist(a, route[idx+2]) if idx+2 < len(route) else 0
                # compare total of the 3 edges (left, between, right) vs (left', between', right')
                total_before = (left if idx-1 >= 0 else 0) + between + (right if idx+2 < len(route) else 0)
                total_after = (left_swap if idx-1 >= 0 else 0) + between_swap + (right_swap if idx+2 < len(route) else 0)
                if total_after < total_before:
                    route[idx], route[idx+1] = route[idx+1], route[idx]
                    swapped_any = True
                    break
            if swapped_any:
                improved = True
    return routes
