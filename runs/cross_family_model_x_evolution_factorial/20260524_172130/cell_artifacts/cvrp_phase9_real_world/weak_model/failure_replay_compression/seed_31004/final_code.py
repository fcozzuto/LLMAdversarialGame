def solve_cvrp(instance):
    """
    A deterministic, interpretable CVRP solver using constructive and local improvement heuristics.
    Args:
        instance (dict): A dictionary with keys:
            - 'depot': int, the depot node id
            - 'customers': list of dicts each with keys:
                - 'id': int, customer id
                - 'demand': float, demand of customer
                - 'x': float, x coordinate
                - 'y': float, y coordinate
            - 'vehicle_capacity': float, capacity of each vehicle
    Returns:
        routes (list of list): list of routes, each route is list of customer ids
    """
    # Extract data
    depot = instance['depot']
    customers_data = instance['customers']
    capacity = instance['vehicle_capacity']
    # Create a list of customers (id, demand, x, y)
    customers = customers_data
    # Create a dictionary for quick access
    customer_dict = {c['id']: c for c in customers}
    # Initialize unassigned customers set
    unassigned = set(c['id'] for c in customers)
    # Initialize list of routes
    routes = []

    # Function to compute Euclidean distance
    def dist(c1, c2):
        dx = c1['x'] - c2['x']
        dy = c1['y'] - c2['y']
        return (dx*dx + dy*dy)**0.5

    # Build initial routes using a greedy nearest neighbor approach
    while unassigned:
        route = []
        load = 0.0
        # Start from depot
        current_node_id = depot
        current_node = customer_dict[current_node_id] if current_node_id != depot else None
        # For initial step, pick the customer closest to depot
        if current_node_id == depot:
            # Find nearest customer to depot
            nearest_customer_id = None
            min_dist = float('inf')
            for cid in unassigned:
                c = customer_dict[cid]
                d = dist(customer_dict[depot], c)
                if d < min_dist:
                    min_dist = d
                    nearest_customer_id = cid
            # Start route with that customer
            route.append(nearest_customer_id)
            load += customer_dict[nearest_customer_id]['demand']
            unassigned.remove(nearest_customer_id)
            current_node_id = nearest_customer_id
            current_node = customer_dict[current_node_id]
        # Continue adding nearest feasible customers
        while True:
            nearest_cid = None
            min_d = float('inf')
            for cid in unassigned:
                c = customer_dict[cid]
                # Check capacity constraint
                if load + c['demand'] > capacity:
                    continue
                # Compute distance from current node
                d = dist(current_node, c)
                if d < min_d:
                    min_d = d
                    nearest_cid = cid
            if nearest_cid is None:
                # No feasible next customer
                break
            # Add customer to route
            route.append(nearest_cid)
            load += customer_dict[nearest_cid]['demand']
            unassigned.remove(nearest_cid)
            current_node_id = nearest_cid
            current_node = customer_dict[current_node_id]
        # Append the route
        routes.append(route)

    # Improve routes with local swaps (2-opt like)
    improved = True
    while improved:
        improved = False
        for r_idx, route in enumerate(routes):
            if len(route) <= 2:
                continue
            # Try all pairs of customer positions for beneficial swap
            for i in range(len(route)-1):
                for j in range(i+1, len(route)):
                    # Swap customers i and j
                    new_route = route[:]
                    new_route[i], new_route[j] = new_route[j], new_route[i]
                    # Check if route remains feasible (capacity constraint always true as only order changed)
                    # No capacity constraint violation in intra-route reordering
                    # Update route if improved (e.g., reduces total route length)
                    def route_length(r):
                        length = 0.0
                        prev_node = customer_dict[depot]
                        for cid in r:
                            c = customer_dict[cid]
                            length += dist(prev_node, c)
                            prev_node = c
                        length += dist(prev_node, customer_dict[depot])
                        return length
                    old_length = route_length(route)
                    new_length = route_length(new_route)
                    if new_length < old_length:
                        routes[r_idx] = new_route
                        improved = True
        # End while improved
    # Return only customer sequences (without depot nodes)
    return routes

