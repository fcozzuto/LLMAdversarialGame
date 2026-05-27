def solve_cvrp(instance):
    """
    Solves a Capacitated Vehicle Routing Problem (CVRP) instance using a deterministic,
    interpretable heuristic approach with constructive, repair, and local search phases.
    Args:
        instance: A dictionary with keys:
            - 'depot': int, id of the depot node.
            - 'customers': list of customer node ids.
            - 'demands': dict mapping node ids to demand values.
            - 'coords': dict mapping node ids to (x, y) coordinates.
            - 'vehicle_capacity': int, capacity of each vehicle.
    Returns:
        routes: list of routes; each route is a list of customer ids (excluding depot).
    """
    depot = instance['depot']
    customers = instance['customers']
    demands = instance['demands']
    coords = instance['coords']
    capacity = instance['vehicle_capacity']
    
    # Helper functions
    def distance(a, b):
        ax, ay = coords[a]
        bx, by = coords[b]
        return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5

    # Initialize unvisited customers
    unvisited = set(customers)
    routes = []

    # Construct phase: build initial routes using a greedy nearest-neighbor heuristic
    while unvisited:
        route = []
        load = 0
        current_node = depot
        while True:
            # Find the nearest unvisited customer that can be served without exceeding capacity
            candidates = [
                (cn, demands[cn])
                for cn in unvisited
                if load + demands[cn] <= capacity
            ]
            if not candidates:
                break  # No more candidates can be added to current route
            # Select nearest candidate
            next_customer, demand_cust = min(candidates, key=lambda x: distance(current_node, x[0]))
            route.append(next_customer)
            unvisited.remove(next_customer)
            load += demand_cust
            current_node = next_customer
        routes.append(route)

    # Repair phase: attempt to merge routes to improve efficiency
    # For simplicity, perform a single pass of merging the routes if possible
    merged = True
    while merged:
        merged = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Try merging route_j into route_i if capacity allows
                load_i = sum(demands[n] for n in route_i)
                load_j = sum(demands[n] for n in route_j)
                if load_i + load_j <= capacity:
                    # Check if merging is sensible (e.g., last customer of route_i and first of route_j are close)
                    # This heuristic improves interpretability
                    end_i = route_i[-1]
                    start_j = route_j[0]
                    if distance(end_i, start_j) < distance(route_i[0], route_i[-1]) + distance(route_j[0], route_j[-1]):
                        # Merge route_j into route_i
                        route_i.extend(route_j)
                        del routes[j]
                        merged = True
                        break
            if merged:
                break

    # Local search: attempt to improve routes by swapping customers between routes if capacity constraints are met
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_a = routes[i]
                route_b = routes[j]
                for idx_a, cust_a in enumerate(route_a):
                    for idx_b, cust_b in enumerate(route_b):
                        demand_a = demands[cust_a]
                        demand_b = demands[cust_b]
                        load_a = sum(demands[n] for n in route_a)
                        load_b = sum(demands[n] for n in route_b)
                        # Check if swap is feasible
                        if (load_a - demand_a + demand_b <= capacity) and \
                           (load_b - demand_b + demand_a <= capacity):
                            # Perform swap
                            route_a[idx_a], route_b[idx_b] = route_b[idx_b], route_a[idx_a]
                            # Calculate current total route costs
                            prev_cost = sum(distance(route_a[k], route_a[k + 1]) for k in range(len(route_a) - 1)) + \
                                        sum(distance(route_b[k], route_b[k + 1]) for k in range(len(route_b) - 1))
                            # Save old routes
                            old_route_a = route_a[:]
                            old_route_b = route_b[:]
                            # Check new cost
                            new_cost = sum(distance(route_a[k], route_a[k + 1]) for k in range(len(route_a) - 1)) + \
                                       sum(distance(route_b[k], route_b[k + 1]) for k in range(len(route_b) - 1))
                            if new_cost < prev_cost:
                                improved = True
                                break
                            else:
                                # Revert swap
                                route_a[idx_a], route_b[idx_b] = cust_a, cust_b
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    # Return routes: only customer ids
    return routes

