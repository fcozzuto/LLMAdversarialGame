def solve_cvrp(instance):
    """
    Solves a Capacitated Vehicle Routing Problem (CVRP) instance using a deterministic,
    interpretable heuristic approach combining constructive and local search methods.

    Args:
        instance: A data structure with the following attributes:
            - depot: int, the depot node id
            - customers: dict {customer_id: {'demand': int, 'x': float, 'y': float}}
            - vehicle_capacity: int

    Returns:
        routes: List of routes, each route is a list of customer ids assigned to a vehicle.
    """

    # Extract data
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']

    # Initialize unvisited customers set
    unvisited = set(customers.keys())

    # Helper to compute Euclidean distance
    def distance(c1, c2):
        dx = customers[c1]['x'] - customers[c2]['x']
        dy = customers[c1]['y'] - customers[c2]['y']
        return (dx * dx + dy * dy) ** 0.5

    # Construct initial solution with nearest neighbor approach
    routes = []

    while unvisited:
        route = []
        load = 0
        current_node = depot

        # Build route greedily
        while True:
            # Find feasible customers not yet visited
            feasible_customers = [
                c for c in unvisited
                if load + customers[c]['demand'] <= capacity
            ]

            if not feasible_customers:
                # No feasible next customer, end current route
                break

            # Select the nearest feasible customer
            next_customer = min(
                feasible_customers,
                key=lambda c: distance(current_node, c)
            )

            # Add to route
            route.append(next_customer)
            load += customers[next_customer]['demand']
            unvisited.remove(next_customer)
            current_node = next_customer

        # Optionally, return to depot (not recorded as per rules), so just start new route
        routes.append(route)

    # Local improvement: attempt to swap customers between routes to reduce total distance
    # Only perform a single pass to keep the logic simple and interpretable
    improved = True
    while improved:
        improved = False
        # Iterate over all pairs of routes and customers
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route1 = routes[i]
                route2 = routes[j]
                for c1_idx, c1 in enumerate(route1):
                    for c2_idx, c2 in enumerate(route2):
                        # Check capacity constraints if we swap
                        demand1_c1 = customers[c1]['demand']
                        demand2_c2 = customers[c2]['demand']
                        load1 = sum(customers[c]['demand'] for c in route1)
                        load2 = sum(customers[c]['demand'] for c in route2)
                        new_load1 = load1 - demand1_c1 + demand2_c2
                        new_load2 = load2 - demand2_c2 + demand1_c1
                        if new_load1 <= capacity and new_load2 <= capacity:
                            # Compute current route distances
                            def route_distance(route):
                                total = 0.0
                                prev = depot
                                for c in route:
                                    total += distance(prev, c)
                                    prev = c
                                # no return to depot needed
                                return total

                            current_total = route_distance(route1) + route_distance(route2)

                            # Swap customers
                            new_route1 = route1[:]
                            new_route2 = route2[:]
                            new_route1[c1_idx], new_route2[c2_idx] = c2, c1

                            new_total = route_distance(new_route1) + route_distance(new_route2)

                            # If improvement, commit swap
                            if new_total < current_total:
                                routes[i] = new_route1
                                routes[j] = new_route2
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes

