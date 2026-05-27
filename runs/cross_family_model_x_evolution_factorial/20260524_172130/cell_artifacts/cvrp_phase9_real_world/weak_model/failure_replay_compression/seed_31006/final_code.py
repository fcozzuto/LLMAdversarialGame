def solve_cvrp(instance):
    """
    Solve the CVRP instance deterministically using constructive, repair, and local-search heuristics.

    Args:
        instance (dict): Dictionary with keys:
            - 'demands': dict {customer_id: demand}
            - 'coords': dict {customer_id: (x, y)}
            - 'capacity': int

    Returns:
        routes (list of list): Each route is a list of customer_ids, excluding the depot.
    """

    demands = instance['demands']
    coords = instance['coords']
    capacity = instance['capacity']

    # Separate depot (assumed customer 0) and customers
    customer_ids = [cid for cid in coords if cid != 0]

    # Function to compute Euclidean distance
    def distance(a, b):
        x1, y1 = coords[a]
        x2, y2 = coords[b]
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

    # Step 1: Construct an initial feasible solution using a greedy nearest neighbor heuristic
    unvisited = set(customer_ids)
    routes = []

    while unvisited:
        route = []
        load = 0
        current = 0  # start at depot
        while True:
            # Find the closest customer that can be served
            candidates = [
                cid for cid in unvisited
                if load + demands[cid] <= capacity
            ]
            if not candidates:
                break
            # Pick the closest candidate
            next_customer = min(candidates, key=lambda c: distance(current, c))
            route.append(next_customer)
            load += demands[next_customer]
            unvisited.remove(next_customer)
            current = next_customer
        routes.append(route)

    # Step 2: Local search/repair to improve solution
    # Attempt to improve by swapping customers between routes if it reduces total distance
    # and maintains capacity constraints
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for idx_i in range(len(route_i)):
                    for idx_j in range(len(route_j)):
                        c1 = route_i[idx_i]
                        c2 = route_j[idx_j]

                        # Check capacity constraints after swap
                        load_i = sum(demands[c] for c in route_i) - demands[c1] + demands[c2]
                        load_j = sum(demands[c] for c in route_j) - demands[c2] + demands[c1]
                        if load_i <= capacity and load_j <= capacity:
                            # Compute current distances
                            def route_distance(r):
                                if not r:
                                    return 0
                                dist = distance(0, r[0])
                                for k in range(len(r)-1):
                                    dist += distance(r[k], r[k+1])
                                dist += distance(r[-1], 0)
                                return dist

                            old_distance = route_distance(route_i) + route_distance(route_j)

                            # Swap customers
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[idx_i], new_route_j[idx_j] = c2, c1

                            new_distance = route_distance(new_route_i) + route_distance(new_route_j)

                            if new_distance < old_distance:
                                # Accept the swap
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

