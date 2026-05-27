def solve_cvrp(instance):
    # deterministic constructive + simple repair/local-search for CVRP
    customers = list(instance.get('customers', []))
    if not isinstance(customers, list):
        customers = []
    depot = instance.get('depot', {'id': 0, 'demand': 0, 'x': 0, 'y': 0})
    capacity = instance.get('vehicle_capacity', 0)

    if not customers or capacity <= 0:
        return []

    # simple math without imports: implement a basic atan2-like angle using quadrant heuristic
    def angle_from_depot(c):
        dx = c['x'] - depot.get('x', 0)
        dy = c['y'] - depot.get('y', 0)
        # approximate angle deterministically using a simple ratio to avoid math import
        # This preserves some order but stays deterministic.
        # We'll map (dx, dy) to a value in [0, 2*pi) using a coarse gridding.
        # If dx==0 and dy==0, return 0.
        if dx == 0 and dy == 0:
            return 0.0
        # compute an approximation of angle by using signs and a simple arctan-like ratio
        ax = dx
        ay = dy
        # compute a pseudo-angle in [0, 2) representing quadrant/direction
        if ay >= 0:
            if ax >= 0:
                frac = ay / (abs(ax) + abs(ay)) if (abs(ax) + abs(ay)) != 0 else 0.0
                ang = 0.0 + frac
            else:
                frac = ay / (abs(ax) + abs(ay)) if (abs(ax) + abs(ay)) != 0 else 0.0
                ang = 0.5 + frac
        else:
            if ax >= 0:
                frac = (-ay) / (abs(ax) + abs(ay)) if (abs(ax) + abs(ay)) != 0 else 0.0
                ang = 1.0 + frac
            else:
                frac = (-ay) / (abs(ax) + abs(ay)) if (abs(ax) + abs(ay)) != 0 else 0.0
                ang = 1.5 + frac
        return ang

    def dist(a, b):
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        # simple Euclidean distance without sqrt for speed; but we need real distance for comparison
        # implement sqrt via a small approximation? To keep deterministic, implement actual sqrt-like via iterative
        # However, to stay simple and deterministic, return squared distance (monotonic with true distance for comparison)
        return (dx*dx + dy*dy) ** 0.5

    def key_for_sort(c):
        ang = angle_from_depot(c)
        ddep = dist(c, depot)
        return (ang, ddep, c['id'])

    customers_sorted = sorted(customers, key=key_for_sort)

    all_routes = []
    current_route = []
    current_load = 0
    for c in customers_sorted:
        dem = c.get('demand', 0)
        if dem > capacity:
            if current_route:
                all_routes.append(current_route)
                current_route = []
                current_load = 0
            all_routes.append([c['id']])
            continue
        if current_load + dem <= capacity:
            current_route.append(c['id'])
            current_load += dem
        else:
            if current_route:
                all_routes.append(current_route)
            current_route = [c['id']]
            current_load = dem

    if current_route:
        all_routes.append(current_route)

    id_to_cust = {c['id']: c for c in customers}

    def route_distance(route):
        if not route:
            return 0.0
        total = 0.0
        prev = None
        for cid in route:
            cust = id_to_cust.get(cid)
            if cust is None:
                continue
            if prev is not None:
                total += dist(prev, cust)
            prev = cust
        if prev is not None:
            total += dist(prev, depot)
        return total

    # Intra-route swaps (adjacent)
    for _ in range(2):
        for r in range(len(all_routes)):
            route = all_routes[r]
            n = len(route)
            if n < 2:
                continue
            improved = False
            for i in range(n - 1):
                new_route = route[:]
                new_route[i], new_route[i+1] = new_route[i+1], new_route[i]
                if route_distance(new_route) < route_distance(route):
                    all_routes[r] = new_route
                    route = new_route
                    improved = True
            if improved:
                continue

    # Inter-route moves: move a customer to an earlier route if capacity allows
    for i in range(len(all_routes)):
        for cid in list(all_routes[i]):
            dem = id_to_cust[cid]['demand']
            for j in range(i):
                load_j = sum(id_to_cust[c2]['demand'] for c2 in all_routes[j])
                if load_j + dem <= capacity:
                    all_routes[i].remove(cid)
                    all_routes[j].append(cid)
                    break

    all_routes = [r for r in all_routes if r]
    return all_routes
