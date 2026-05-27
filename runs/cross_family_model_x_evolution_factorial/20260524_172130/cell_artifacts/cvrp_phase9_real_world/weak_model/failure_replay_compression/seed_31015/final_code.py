def solve_cvrp(instance):
    """
    Constructs a feasible CVRP solution using a deterministic, interpretable heuristic.
    
    Args:
        instance (dict): A dictionary containing:
            - 'customers': list of customer dictionaries with keys 'id', 'x', 'y', 'demand'
            - 'depot': dictionary with keys 'x', 'y'
            - 'vehicle_capacity': int
    Returns:
        routes (list of lists): Each inner list is a route (list of customer ids), excluding depot.
    """
    # Extract data
    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']
    
    # Initialize
    unvisited = {c['id']: c for c in customers}
    routes = []

    # Utility function to compute squared Euclidean distance
    def dist_sq(c1, c2):
        return (c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2

    # Helper to select next customer based on nearest neighbor heuristic
    def select_next(current_point, candidates, remaining_capacity):
        min_dist = None
        selected = None
        for cid, c in candidates.items():
            if c['demand'] <= remaining_capacity:
                d = dist_sq(current_point, c)
                if (min_dist is None) or (d < min_dist):
                    min_dist = d
                    selected = c
        return selected

    # While there are unvisited customers, create routes
    while unvisited:
        route = []
        load = 0
        current_point = depot
        # While possible, add nearest feasible customer
        while True:
            next_customer = select_next(current_point, unvisited, capacity - load)
            if next_customer is None:
                break
            # Add customer to route
            route.append(next_customer['id'])
            load += next_customer['demand']
            # Remove from unvisited
            del unvisited[next_customer['id']]
            # Update current point
            current_point = next_customer
        routes.append(route)
    return routes

