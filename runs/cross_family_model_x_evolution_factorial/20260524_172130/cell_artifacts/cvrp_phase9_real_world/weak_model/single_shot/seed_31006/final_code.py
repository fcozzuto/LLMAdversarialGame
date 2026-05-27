def solve_cvrp(instance):
    """
    Solve a Capacitated Vehicle Routing Problem (CVRP) instance deterministically.
    Builds routes by sequentially adding closest feasible customers, then performs simple improvement.

    Args:
        instance: dict with keys:
            - 'depot': int, depot customer id
            - 'coordinates': dict {customer_id: (x, y)}
            - 'demands': dict {customer_id: demand}
            - 'capacity': vehicle capacity (int)

    Returns:
        routes: list of routes, each route is a list of customer ids excluding depot
    """

    depot = instance['depot']
    coords = instance['coordinates']
    demands = instance['demands']
    capacity = instance['capacity']

    # Initialize unvisited customers
    unvisited = set(c for c in coords if c != depot)

    routes = []

    # Precompute a simple distance function
    def distance(a, b):
        xa, ya = coords[a]
        xb, yb = coords[b]
        return ((xa - xb) ** 2 + (ya - yb) ** 2) ** 0.5

    while unvisited:
        route = []
        load = 0
        current = depot

        # Build route greedily
        while True:
            # Find feasible customers
            feasible_customers = [
                c for c in unvisited
                if demands[c] + load <= capacity
            ]
            if not feasible_customers:
                break

            # Select the closest feasible customer
            next_customer = min(
                feasible_customers,
                key=lambda c: distance(current, c)
            )

            # Add to route
            route.append(next_customer)
            load += demands[next_customer]
            unvisited.remove(next_customer)
            current = next_customer

        routes.append(route)

    # Simple local improvement: try to swap two customers between routes if it improves total route length
    # This is a basic pairwise swap attempt
    def total_distance(r):
        dist = 0.0
        prev = depot
        for c in r:
            dist += distance(prev, c)
            prev = c
        dist += distance(prev, depot)
        return dist

    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for m in range(len(route_i)):
                    for n in range(len(route_j)):
                        c1 = route_i[m]
                        c2 = route_j[n]
                        # Check capacity constraints after swap
                        load_i = sum(demands[c] for c in route_i)
                        load_j = sum(demands[c] for c in route_j)
                        new_load_i = load_i - demands[c1] + demands[c2]
                        new_load_j = load_j - demands[c2] + demands[c1]
                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Perform swap
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[m], new_route_j[n] = c2, c1
                            # Compute new distances
                            new_dist_i = total_distance(new_route_i)
                            new_dist_j = total_distance(new_route_j)
                            old_dist_i = total_distance(route_i)
                            old_dist_j = total_distance(route_j)
                            if new_dist_i + new_dist_j < old_dist_i + old_dist_j:
                                # Accept swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes

