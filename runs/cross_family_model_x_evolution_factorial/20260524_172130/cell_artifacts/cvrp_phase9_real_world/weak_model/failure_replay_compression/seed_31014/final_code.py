def solve_cvrp(instance):
    # Instance expected to be a dict with keys:
    # 'customers': list of dicts, each with 'id', 'demand', 'x', 'y'
    # 'depot': dict with 'id', 'x', 'y'
    # 'vehicle_capacity': number
    
    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customer ids sorted deterministically (e.g., by id)
    customer_list = sorted(customers, key=lambda c: c['id'])
    # Build a lookup for customer demands and positions
    demand_lookup = {c['id']: c['demand'] for c in customer_list}
    position_lookup = {c['id']: (c['x'], c['y']) for c in customer_list}
    
    unvisited = set(c['id'] for c in customer_list)
    routes = []
    
    while unvisited:
        route = []
        load = 0
        last_point = (depot['x'], depot['y'])
        while True:
            # Select the next customer with minimal distance to last_point
            candidates = []
            for cid in unvisited:
                point = position_lookup[cid]
                dist = ((point[0] - last_point[0])**2 + (point[1] - last_point[1])**2)**0.5
                candidates.append((dist, cid))
            if not candidates:
                break
            # Pick the nearest candidate
            candidates.sort(key=lambda x: x[0])
            for _, cid in candidates:
                demand = demand_lookup[cid]
                if load + demand <= capacity:
                    # assign to current route
                    route.append(cid)
                    load += demand
                    last_point = position_lookup[cid]
                    unvisited.remove(cid)
                    break
            else:
                # No candidate fits, finish current route
                break
        routes.append(route)
    return routes

