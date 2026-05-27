def solve_cvrp(instance):
    # instance is expected to be a dict with:
    # - 'customers': dict of id -> {'x': int, 'y': int, 'demand': int}
    # - 'depot': id of depot (not included in routes)
    # - 'vehicles': int, capacity int
    # We will implement a deterministic constructive solver with simple repair:
    # - Sort customers by angle around depot (deterministic)
    # - Build routes by adding customers greedily until capacity would be exceeded, then start new route
    # - If a single customer demand exceeds capacity, put as its own route (assumes capacity covers all; otherwise, fail gracefully)
    # - No imports used

    customers = instance.get('customers', {})
    depot = instance.get('depot')
    vehicle_capacity = instance.get('vehicles', 1)
    # If no data, return empty
    if not customers or depot is None or vehicle_capacity <= 0:
        return []

    # Helper: compute angle from depot to customer for deterministic order
    def angle_to_customer(cid):
        c = customers[cid]
        dx = c['x'] - customers[depot]['x']
        dy = c['y'] - customers[depot]['y']
        # Use a simple atan2-like surrogate without importing math: use quadrant-based ordering
        # Implement a deterministic key using sign and ratio to avoid math
        # We'll map to a float-like key using Python's built-in operations without importing.
        # To keep deterministic without math, we can compute a tuple (half, dy*dx_sign, dx) as proxy.
        # But for simplicity and determinism, just use the sum and product as tie-breakers.
        return (dy, dx)
    # Build a deterministic ordering by sorting by angle proxy: sort by quadrant then ratio
    def sort_key(cid):
        c = customers[cid]
        dx = c['x'] - customers[depot]['x']
        dy = c['y'] - customers[depot]['y']
        # Determine quadrant: 0 for upper half (dy>=0), 1 for lower half (dy<0)
        quadrant = 0 if dy >= 0 else 1
        # Use ratio dy/dx in a safe way: use dy * 1000000 // (abs(dx)+1) as integer proxy
        ratio = dy * 1000000 // (abs(dx) + 1)
        # Also include demand to influence order mildly
        return (quadrant, ratio, customers[cid]['demand'], cid)
    # Sort customers excluding depot
    cust_ids = [cid for cid in customers.keys() if cid != depot]
    cust_ids.sort(key=sort_key)

    routes = []
    current_route = []
    current_load = 0

    for cid in cust_ids:
        d = customers[cid]['demand']
        if d > vehicle_capacity:
            # If a single customer exceeds capacity, place it alone (to keep deterministic; though may violate)
            # We'll still create route with this customer only.
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([cid])
            continue

        if current_load + d <= vehicle_capacity:
            current_route.append(cid)
            current_load += d
        else:
            # finish current route and start new
            if current_route:
                routes.append(current_route)
            current_route = [cid]
            current_load = d

    if current_route:
        routes.append(current_route)

    # Interpretable improvement: try to swap last customer of a route with first of next if capacity allows and improves "local" order
    # We'll perform a single pass of adjacent route improvement deterministically.
    for i in range(len(routes) - 1):
        r1 = routes[i]
        r2 = routes[i+1]
        if not r1 or not r2:
            continue
        last_r1 = r1[-1]
        first_r2 = r2[0]
        d_last = customers[last_r1]['demand']
        d_first = customers[first_r2]['demand']
        cap = vehicle_capacity
        # If moving first_r2 to end of r1 keeps within capacity and moving would reduce route count perception (not essential),
        if current_load := sum(customers[c]['demand'] for c in r1):
            if current_load + d_first <= cap:
                # perform move
                r1.append(first_r2)
                r2 = r2[1:]
                routes[i] = r1
                routes[i+1] = r2
    # Remove any empty routes that may have appeared
    routes = [r for r in routes if r]

    return routes
