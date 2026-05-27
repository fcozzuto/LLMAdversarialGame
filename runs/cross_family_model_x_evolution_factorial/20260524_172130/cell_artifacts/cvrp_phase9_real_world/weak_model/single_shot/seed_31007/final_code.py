def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) for the given instance using a deterministic, interpretable, single-shot approach.

    Args:
        instance: A dictionary with keys:
            - 'depot': integer id of the depot
            - 'customers': list of customer dicts with keys: 'id', 'x', 'y', 'demand'
            - 'vehicle_capacity': integer
    Returns:
        routes: list of routes, each route is a list of customer ids (excluding the depot)
    """
    depot_id = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customer data: id, demand, x, y
    customer_list = customers
    
    # Initialize list of unvisited customers
    unvisited = set(c['id'] for c in customer_list)
    
    # Map customer id to data for quick access
    customer_map = {c['id']: c for c in customer_list}
    
    routes = []

    # Function to compute Euclidean distance between two points
    def distance(c1, c2):
        dx = c1['x'] - c2['x']
        dy = c1['y'] - c2['y']
        return (dx*dx + dy*dy) ** 0.5

    # Build a list/dictionary of customer locations for distance calculations
    customer_points = {c['id']: c for c in customer_list}
    depot_point = next(c for c in customer_list if c['id'] == depot_id)

    while unvisited:
        route = []
        load = 0
        current_location = depot_point
        # Build a route greedily: pick the closest unvisited customer that fits in capacity
        while True:
            # Find the closest customer that fits capacity
            candidates = []
            for cid in unvisited:
                customer = customer_map[cid]
                demand = customer['demand']
                if load + demand <= capacity:
                    dist_to_customer = distance(current_location, customer)
                    candidates.append( (dist_to_customer, customer) )
            if not candidates:
                # No more customers can be added to this route
                break
            # Pick the closest
            candidates.sort(key=lambda x: x[0])
            _, next_customer = candidates[0]
            # Add to route
            route.append(next_customer['id'])
            unvisited.remove(next_customer['id'])
            load += next_customer['demand']
            current_location = next_customer
        routes.append(route)

    return routes

