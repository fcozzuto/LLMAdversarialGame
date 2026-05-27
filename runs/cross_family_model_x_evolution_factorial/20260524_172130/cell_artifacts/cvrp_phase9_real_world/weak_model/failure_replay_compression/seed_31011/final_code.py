def solve_cvrp(instance):
    """
    Construct a simple deterministic CVRP solution using a greedy, interpretable approach.
    Args:
        instance: Dict with keys:
            'depot': int, depot node id
            'customers': List of customer dicts with keys:
                'id': int
                'x': float
                'y': float
                'demand': float
            'vehicle_capacity': float
    Returns:
        List of routes, each route is a list of customer ids (excluding depot).
    """
    # Extract data
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customer info tuples for easy handling
    customer_list = [
        {
            'id': c['id'],
            'x': c['x'],
            'y': c['y'],
            'demand': c['demand']
        }
        for c in customers
    ]
    
    # Keep track of unserved customers
    unserved = set(c['id'] for c in customer_list)
    customer_map = {c['id']: c for c in customer_list}
    
    def distance(c1, c2):
        return ((c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2)**0.5
    
    routes = []
    
    # Build routes greedily
    while unserved:
        route = []
        load = 0.0
        current_node = {'id': depot, 'x': 0.0, 'y': 0.0, 'demand': 0}  # start at depot
        while True:
            # Find the nearest unserved customer that can be served within capacity
            nearest_customer = None
            min_dist = float('inf')
            for cid in unserved:
                customer = customer_map[cid]
                if load + customer['demand'] <= capacity:
                    dist = distance(current_node, customer)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_customer = customer
            if nearest_customer is None:
                # No feasible customer found, end the route
                break
            # Add customer to route
            route.append(nearest_customer['id'])
            load += nearest_customer['demand']
            unserved.remove(nearest_customer['id'])
            current_node = nearest_customer
        routes.append(route)
    return routes

