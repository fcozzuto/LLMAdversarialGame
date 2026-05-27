def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) using a deterministic, interpretable heuristic.
    Args:
        instance: dict with keys:
            'depot': int - depot node id
            'nodes': list of dicts with keys:
                'id': int, node id
                'demand': int, demand of customer (0 for depot)
                'x', 'y': float - coordinates (not used in this heuristic)
            'vehicle_capacity': int
    Returns:
        routes: list of routes, each route is a list of customer ids (excluding depot), covering all customers exactly once.
    """

    # Extract data
    depot_id = instance['depot']
    nodes = instance['nodes']
    capacity = instance['vehicle_capacity']
    # Create customer list (exclude depot)
    customers = [node for node in nodes if node['id'] != depot_id]
    customer_dict = {node['id']: node for node in customers}

    # Initialize unserved customers
    unserved = set(customer['id'] for customer in customers)

    # Prepare a list to hold the final routes
    routes = []

    # Build routes iteratively until all customers are served
    while unserved:
        current_route = []
        remaining_capacity = capacity

        # Start from depot (we'll determine the start point momentarily)
        # For deterministic behavior, pick the unserved customer with the smallest id as starting point
        # to maintain consistency
        start_customer_id = min(unserved)
        start_customer = customer_dict[start_customer_id]

        current_customer_id = start_customer_id
        # Serve the starting customer
        current_route.append(current_customer_id)
        unserved.remove(current_customer_id)
        remaining_capacity -= current_route[-1] == current_customer_id and customer_dict[current_customer_id]['demand'] or 0

        # Iteratively select the next customer to serve
        while True:
            # Find unserved customers that can be served within remaining capacity
            feasible_customers = [
                cid for cid in unserved
                if customer_dict[cid]['demand'] <= remaining_capacity
            ]
            if not feasible_customers:
                # No more customers can be served in this route
                break

            # Deterministically select the closest feasible customer to the last served customer
            last_cust = customer_dict[current_customer_id]
            # Compute "distance" as the absolute difference in ids for simplicity, as coordinates are not used
            # Alternatively, can use a dummy distance metric based on customer ids to maintain determinism
            next_cust_id = min(
                feasible_customers,
                key=lambda cid: abs(cid - current_customer_id)
            )

            # Update route and remaining capacity
            current_route.append(next_cust_id)
            unserved.remove(next_cust_id)
            current_customer_id = next_cust_id

        # Append the constructed route (excluding depot)
        routes.append(current_route)

    return routes

