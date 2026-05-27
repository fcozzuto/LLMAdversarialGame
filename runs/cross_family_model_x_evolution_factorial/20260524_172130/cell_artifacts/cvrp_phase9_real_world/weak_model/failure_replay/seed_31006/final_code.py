def solve_cvrp(instance):
    """
    Construct a feasible CVRP solution using a deterministic, interpretable approach.

    Args:
        instance (dict): A dictionary containing:
            - 'customers': list of dicts with 'id', 'demand', 'x', 'y'
            - 'depot': dict with 'id', 'x', 'y'
            - 'vehicle_capacity': int

    Returns:
        List of routes, each route is a list of customer IDs (excluding the depot)
    """
    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customer data: (id, demand, x, y)
    customer_list = [(c['id'], c['demand'], c['x'], c['y']) for c in customers]
    
    # Initialize list to hold routes
    routes = []

    # Initialize unvisited customers set
    unvisited = set(c['id'] for c in customer_list)

    # Precompute a lookup for customer data
    customer_map = {c['id']: c for c in customer_list}
    
    # Helper function to compute Euclidean distance
    def dist(c1, c2):
        return ((c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2)**0.5

    # While there are unvisited customers, build a route
    while unvisited:
        current_load = 0
        route = []
        current_location = depot

        # Build route using a nearest neighbor heuristic
        while True:
            # Find the nearest unvisited customer that can be served
            candidates = []
            for cid in unvisited:
                customer = customer_map[cid]
                # Check capacity constraint
                if customer['demand'] + current_load <= capacity:
                    distance = dist(current_location, customer)
                    candidates.append((distance, customer))
            if not candidates:
                # No further customers can be added to current route
                break
            # Select the nearest neighbor
            candidates.sort(key=lambda x: x[0])
            next_customer = candidates[0][1]
            # Add to route
            route.append(next_customer['id'])
            current_load += next_customer['demand']
            current_location = next_customer
            unvisited.remove(next_customer['id'])
        routes.append(route)
    return routes

