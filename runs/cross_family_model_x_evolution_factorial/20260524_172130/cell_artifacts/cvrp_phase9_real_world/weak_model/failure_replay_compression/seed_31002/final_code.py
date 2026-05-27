def solve_cvrp(instance):
    """
    Construct a deterministic, interpretable CVRP solution for the given instance.
    Parameters:
        instance: dict with keys:
            'depot': int, depot node id
            'customers': list of dicts, each with keys:
                'id': int, customer id
                'demand': int, customer demand
                'x': float, x-coordinate
                'y': float, y-coordinate
            'vehicle_capacity': int, capacity of each vehicle
    Returns:
        routes: list of routes, each route is a list of customer ids
    """
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Prepare list of customers, each with position, demand, and id
    customer_list = [
        {
            'id': c['id'],
            'demand': c['demand'],
            'x': c['x'],
            'y': c['y']
        }
        for c in customers
    ]
    
    # Initialize unserved customers
    unserved = customer_list.copy()
    routes = []
    
    # Function to compute Euclidean distance between two points
    def distance(a, b):
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        return (dx*dx + dy*dy) ** 0.5
    
    # Build routes until all customers are assigned
    while unserved:
        route = []
        load = 0
        current_node = {'id': depot, 'x': 0.0, 'y': 0.0}  # start from depot at origin; position is not critical
        route_demand = 0
        route_nodes = []
        remaining_customers = unserved.copy()
        
        # Greedy insertion: keep adding closest feasible customer
        while True:
            # Find feasible customers (not yet served and demand fits)
            feasible_customers = [
                c for c in remaining_customers
                if c['demand'] + route_demand <= capacity
            ]
            if not feasible_customers:
                break
            # Select closest customer among feasible
            next_customer = min(
                feasible_customers,
                key=lambda c: distance(current_node, c)
            )
            # Add to route
            route_nodes.append(next_customer['id'])
            route_demand += next_customer['demand']
            # Update current node position
            current_node = next_customer
            # Remove from unserved
            remaining_customers.remove(next_customer)
        
        # Remove served customers from unserved list
        for cid in route_nodes:
            for c in unserved:
                if c['id'] == cid:
                    unserved.remove(c)
        # Append route
        routes.append(route_nodes)
    
    return routes

