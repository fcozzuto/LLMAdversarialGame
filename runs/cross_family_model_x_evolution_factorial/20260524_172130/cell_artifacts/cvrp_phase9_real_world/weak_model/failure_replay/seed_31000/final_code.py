def solve_cvrp(instance):
    """
    Solve a Capacitated Vehicle Routing Problem (CVRP) instance using a deterministic,
    interpretable heuristic approach with failure replay logic.

    Args:
        instance (dict): A dictionary containing keys:
            - 'depot': int, the depot node id
            - 'customers': list of dicts, each with 'id', 'demand', 'x', 'y'
            - 'vehicle_capacity': float

    Returns:
        list of lists: Each inner list is a route (list of customer ids),
                       representing the sequence of customer visits per vehicle.
    """

    depot_id = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']

    # Create a mapping from customer id to customer data for quick access
    customer_map = {cust['id']: cust for cust in customers}

    # Initialize set of unvisited customers
    unvisited = set([cust['id'] for cust in customers])

    # Helper function: compute Euclidean distance
    def distance(cust_id1, cust_id2):
        if cust_id1 == depot_id:
            node1 = {'x': 0, 'y': 0}
        else:
            node1 = customer_map[cust_id1]
        if cust_id2 == depot_id:
            node2 = {'x': 0, 'y': 0}
        else:
            node2 = customer_map[cust_id2]
        dx = node1['x'] - node2['x']
        dy = node1['y'] - node2['y']
        return (dx*dx + dy*dy) ** 0.5

    # Build a list of customers sorted by proximity to depot (heuristic starting point)
    sorted_customers = sorted(unvisited, key=lambda cid: distance(depot_id, cid))
    
    routes = []

    # Construct initial routes using a greedy approach
    while unvisited:
        current_capacity = 0
        current_route = []

        # Start from depot (implicitly, route starts at depot)
        last_node = depot_id

        # while we can add customers without exceeding capacity
        while True:
            # Find the closest unvisited customer to last_node that can fit in capacity
            feasible_customers = [
                cid for cid in unvisited
                if customer_map[cid]['demand'] + current_capacity <= capacity
            ]
            if not feasible_customers:
                # No feasible customers left for this route
                break

            # Select the closest feasible customer
            next_cust = min(feasible_customers, key=lambda cid: distance(last_node, cid))

            # Update route and capacity
            current_route.append(next_cust)
            unvisited.remove(next_cust)
            current_capacity += customer_map[next_cust]['demand']
            last_node = next_cust

        routes.append(current_route)

    # Local improvement: attempt to swap customers between routes to reduce total distance
    # Repeat until no improvement or max iterations
    max_iterations = 10
    for _ in range(max_iterations):
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_a = routes[i]
                route_b = routes[j]
                for a_idx in range(len(route_a)):
                    for b_idx in range(len(route_b)):
                        cust_a = route_a[a_idx]
                        cust_b = route_b[b_idx]
                        demand_a = customer_map[cust_a]['demand']
                        demand_b = customer_map[cust_b]['demand']
                        # Check if swap is feasible regarding capacity
                        cap_a = sum(customer_map[c]['demand'] for c in route_a) - demand_a + demand_b
                        cap_b = sum(customer_map[c]['demand'] for c in route_b) - demand_b + demand_a
                        if cap_a <= capacity and cap_b <= capacity:
                            # Calculate current distances
                            def route_distance(route):
                                total = distance(depot_id, route[0]) if route else 0
                                for k in range(len(route) - 1):
                                    total += distance(route[k], route[k+1])
                                total += distance(route[-1], depot_id)
                                return total

                            current_total = route_distance(route_a) + route_distance(route_b)

                            # Create new routes with swapped customers
                            new_route_a = route_a[:]
                            new_route_b = route_b[:]
                            new_route_a[a_idx], new_route_b[b_idx] = cust_b, cust_a

                            new_total = route_distance(new_route_a) + route_distance(new_route_b)

                            if new_total < current_total:
                                # Accept swap
                                routes[i] = new_route_a
                                routes[j] = new_route_b
                                improved = True
        # If no improvement, break early
        if not improved:
            break

    return routes

