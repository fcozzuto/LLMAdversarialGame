def solve_cvrp(instance):
    """
    Solve a Capacitated Vehicle Routing Problem (CVRP) instance with a deterministic,
    interpretable heuristic approach combining constructive, repair, and local search strategies.

    Parameters:
        instance: dict with keys:
            'customers': dict {customer_id: (demand, (x, y))}
            'depot': (x, y)
            'vehicle_capacity': int or float

    Returns:
        routes: list of routes, each a list of customer_ids
    """

    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']

    unvisited = set(customers.keys())

    # Compute Euclidean distance
    def dist(p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5

    # Build a list of customer data for easy access
    customer_list = list(customers.items())
    # Prepare a lookup dict for demands
    demands = {cid: demand for cid, (demand, _) in customer_list}

    routes = []

    while unvisited:
        route = []
        load = 0
        current_location = depot

        # Sort unvisited customers by nearest neighbor heuristic to depot
        # but deterministically, sort by distance to current location
        def nearest_unvisited(candidates, current_loc):
            return sorted(candidates, key=lambda cid: dist(customers[cid][1], current_loc))

        while True:
            # Get list of remaining customers
            remaining = list(unvisited)
            if not remaining:
                break

            # Find nearest feasible customer
            feasible_customers = []
            for cid in nearest_unvisited(remaining, current_location):
                demand = demands[cid]
                if load + demand <= capacity:
                    feasible_customers.append(cid)

            if not feasible_customers:
                # Cannot add more customers to this route
                break

            # Select the nearest feasible customer
            next_cid = feasible_customers[0]
            route.append(next_cid)
            load += demands[next_cid]
            current_location = customers[next_cid][1]
            unvisited.remove(next_cid)

        routes.append(route)

    # Local improvement: try swapping customers between routes if capacity constraints are respected
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for ci in range(len(route_i)):
                    for cj in range(len(route_j)):
                        c1 = route_i[ci]
                        c2 = route_j[cj]
                        demand_c1 = demands[c1]
                        demand_c2 = demands[c2]
                        load_i = sum(demands[c] for c in route_i)
                        load_j = sum(demands[c] for c in route_j)

                        # Check if swapping keeps within capacity
                        new_load_i = load_i - demand_c1 + demand_c2
                        new_load_j = load_j - demand_c2 + demand_c1
                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Perform swap
                            route_i[ci], route_j[cj] = c2, c1
                            improved = True
    return routes

