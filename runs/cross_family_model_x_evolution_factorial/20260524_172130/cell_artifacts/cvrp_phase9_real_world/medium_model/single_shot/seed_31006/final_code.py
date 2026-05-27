def solve_cvrp(instance):
    # instance is expected to be a dict-like with:
    # - 'customers': list of dicts with 'id', 'demand', 'x', 'y' (optional)
    # - 'depot': dict or id
    # - 'vehicle_capacity': int
    # If the structure differs, try reasonable defaults.
    customers = []
    depot_id = None
    capacity = None

    if isinstance(instance, dict):
        if 'customers' in instance:
            customers = instance['customers']
        elif 'nodes' in instance:
            customers = instance['nodes']
        else:
            customers = []
        if 'depot' in instance:
            depot_id = instance['depot']
        elif 'depot_id' in instance:
            depot_id = instance['depot_id']
        else:
            depot_id = None
        if 'vehicle_capacity' in instance:
            capacity = instance['vehicle_capacity']
        else:
            capacity = None
        # if format is simple list of ids with demands, adapt below
        if not customers and isinstance(instance, dict) and 'data' in instance:
            customers = instance['data']
    else:
        customers = []
        depot_id = None
        capacity = None

    # Fallbacks for minimal structures
    if capacity is None:
        capacity = 10

    # Normalize customer objects: ensure id and demand
    norm = []
    for c in customers:
        cid = c.get('id') if isinstance(c, dict) else None
        if cid is None:
            # if customer is just a number
            if isinstance(c, int):
                cid = c
                demand = 1
            else:
                continue
        else:
            demand = c.get('demand', 1)
        norm.append({'id': cid, 'demand': int(demand)})
    # If there are no customers, return empty
    if not norm:
        return []

    # Very simple 2-opt-like constructive: sort by id to be deterministic
    norm.sort(key=lambda x: x['id'])

    # Build routes greedily: accumulate until capacity would be exceeded, then start new route
    routes = []
    current = []
    current_load = 0
    for c in norm:
        d = c['demand']
        if current_load + d > capacity:
            if current:
                routes.append([x['id'] for x in current])
            current = [c]
            current_load = d
        else:
            current.append(c)
            current_load += d
    if current:
        routes.append([x['id'] for x in current])

    # Repair step: ensure every customer appears once across routes (no duplicates)
    seen = set()
    unique_routes = []
    for r in routes:
        nr = []
        for cid in r:
            if cid not in seen:
                nr.append(cid)
                seen.add(cid)
        if nr:
            unique_routes.append(nr)
    # If any missing due to duplicates, assign them to last route
    missing = [c['id'] for c in norm if c['id'] not in seen]
    for mid in missing:
        if unique_routes:
            unique_routes[-1].append(mid)
        else:
            unique_routes.append([mid])

    # Final check: ensure none empty and capacity respected
    final_routes = []
    for r in unique_routes:
        load = sum(next((c['demand'] for c in norm if c['id']==cid), 1) for cid in r)
        if load > capacity and len(r) > 0:
            # split this route into smaller ones if over capacity
            temp = []
            cur = []
            cur_load = 0
            for cid in r:
                dem = next((c['demand'] for c in norm if c['id']==cid), 1)
                if cur_load + dem > capacity:
                    if cur:
                        temp.append(cur)
                    cur = [cid]
                    cur_load = dem
                else:
                    cur.append(cid)
                    cur_load += dem
            if cur:
                temp.append(cur)
            final_routes.extend(temp)
        else:
            final_routes.append(r)

    # Ensure deterministic order and no depot included
    routes = final_routes

    return routes
