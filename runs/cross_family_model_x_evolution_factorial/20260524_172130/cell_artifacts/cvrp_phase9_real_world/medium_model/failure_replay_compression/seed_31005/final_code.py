def solve_cvrp(instance):
    # Deterministic constructive + simple repair for CVRP.
    # No imports. Returns list of routes (each a list of customer ids, excluding depot).
    # Assumes instance with keys:
    # - 'depot': int
    # - 'customers': list of dicts {'id': int, 'demand': int} OR list of ids (unit demand)
    # - 'vehicle_capacity': int
    # - optional 'distance'(a,b) for determinism (not required)

    def dist(a, b):
        if isinstance(instance, dict) and 'distance' in instance and callable(instance['distance']):
            return instance['distance'](a, b)
        return abs(int(a) - int(b))

    depot = instance.get('depot', 0)
    customers = list(instance.get('customers', []))
    capacity = instance.get('vehicle_capacity', 0)

    # Normalize customers to list of {'id','demand'}
    norm = []
    for c in customers:
        if isinstance(c, dict) and 'id' in c and 'demand' in c:
            norm.append({'id': int(c['id']), 'demand': int(c['demand'])})
        else:
            cid = int(c)
            norm.append({'id': cid, 'demand': 1})

    # Deterministic order: by id
    norm.sort(key=lambda x: x['id'])

    unvisited = norm[:]
    routes = []

    # Construct routes greedily by filling with smallest-id customers
    while unvisited:
        route = []
        load = 0
        i = 0
        while i < len(unvisited):
            c = unvisited[i]
            d = c['demand']
            if load + d <= capacity:
                route.append(c['id'])
                load += d
                del unvisited[i]
            else:
                i += 1
        if not route and unvisited:
            c = unvisited.pop(0)
            route = [c['id']]  # place even if over capacity (edge case would be rejected externally)
        routes.append(route)

    # Simple repair: try to move one tail item from a route to next if feasible
    # Up to a small fixed number of passes to keep deterministic
    if capacity > 0:
        max_passes = max(1, len(routes) * 2)
        passes = 0
        while passes < max_passes:
            improved = False
            passes += 1
