def solve_cvrp(instance):
    """
    Solves a Capacitated Vehicle Routing Problem (CVRP) instance deterministically,
    building routes by a constructive heuristic (nearest neighbor), respecting capacity,
    and refining routes with a simple local improvement.

    Args:
        instance: dict with keys:
            - 'customers': list of dicts with 'id', 'demand', 'x', 'y'
            - 'depot': dict with 'id', 'x', 'y'
            - 'vehicle_capacity': int

    Returns:
        routes: list of routes, each route is a list of customer ids (excluding depot)
    """

    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']

    # Create a list of customer id to customer data for easy lookup
    customer_map = {c['id']: c for c in customers}

    # Initialize list of unvisited customers
    unvisited = set(c['id'] for c in customers)

    # Function to compute Euclidean distance between two points
    def dist(a_x, a_y, b_x, b_y):
        return ((a_x - b_x)**2 + (a_y - b_y)**2)**0.5

    # Build routes using nearest neighbor heuristic
    routes = []

    while unvisited:
        route = []
        load = 0
        current_x = depot['x']
        current_y = depot['y']
        # Start from depot
        while True:
            # Find nearest unvisited customer that fits in remaining capacity
            nearest_customer = None
            min_distance = float('inf')
            for cid in unvisited:
                customer = customer_map[cid]
                if load + customer['demand'] <= capacity:
                    d = dist(current_x, current_y, customer['x'], customer['y'])
                    if d < min_distance:
                        min_distance = d
                        nearest_customer = cid
            # If no suitable customer, end route
            if nearest_customer is None:
                break
            # Add customer to route
            customer = customer_map[nearest_customer]
            route.append(nearest_customer)
            unvisited.remove(nearest_customer)
            load += customer['demand']
            current_x, current_y = customer['x'], customer['y']
        routes.append(route)

    # Simple local search improvement: intra-route 2-opt swaps
    def improve_route(route):
        improved = True
        while improved:
            improved = False
            n = len(route)
            for i in range(n - 1):
                for j in range(i + 2, n):
                    if j - i == 1:
                        continue
                    # Compute current distances
                    def route_segment_distance(r):
                        total = 0
                        prev_x, prev_y = depot['x'], depot['y']
                        for cid in r:
                            c = customer_map[cid]
                            total += dist(prev_x, prev_y, c['x'], c['y'])
                            prev_x, prev_y = c['x'], c['y']
                        total += dist(prev_x, prev_y, depot['x'], depot['y'])
                        return total

                    # Current segment
                    segment = route[i:j]
                    # Reversed segment
                    new_segment = segment[::-1]
                    new_route = route[:i] + new_segment + route[j:]
                    # Check capacity constraint (should not change)
                    # Compute distances
                    def route_distance(r):
                        total = 0
                        prev_x, prev_y = depot['x'], depot['y']
                        for cid in r:
                            c = customer_map[cid]
                            total += dist(prev_x, prev_y, c['x'], c['y'])
                            prev_x, prev_y = c['x'], c['y']
                        total += dist(prev_x, prev_y, depot['x'], depot['y'])
                        return total

                    if route_distance(new_route) < route_distance(route):
                        route = new_route
                        improved = True
                        break
                if improved:
                    break
        return route

    # Apply local improvement to each route
    optimized_routes = []
    for route in routes:
        optimized_route = improve_route(route)
        optimized_routes.append(optimized_route)

    return optimized_routes

