def solve_cvrp(instance):
    """
    Solve a CVRP instance using a deterministic, interpretable heuristic approach.
    The instance is a dictionary with keys:
        - 'depot': depot node id
        - 'nodes': dict {node_id: {'demand': int, 'x': float, 'y': float}}
        - 'vehicle_capacity': int
    Returns:
        - routes: list of routes, each route is a list of customer ids
    """
    # Extract data from instance
    depot = instance['depot']
    nodes = instance['nodes']
    capacity = instance['vehicle_capacity']
    
    # Prepare customer list
    customers = [node_id for node_id in nodes if node_id != depot]
    
    # Initialize data structures
    # We will build routes one by one
    routes = []
    
    # Keep track of which customers are unserved
    unserved = set(customers)
    
    # Function to compute Euclidean distance
    def distance(n1, n2):
        dx = nodes[n1]['x'] - nodes[n2]['x']
        dy = nodes[n1]['y'] - nodes[n2]['y']
        return (dx*dx + dy*dy)**0.5
    
    # Main loop: build routes until all customers are served
    while unserved:
        route = []
        load = 0
        current_node = depot
        # Greedy selection: pick the nearest unserved customer that fits capacity
        while True:
            # Find candidates
            candidates = []
            for customer in unserved:
                demand = nodes[customer]['demand']
                if load + demand <= capacity:
                    dist = distance(current_node, customer)
                    candidates.append((dist, customer))
            if not candidates:
                # No more customers can be added to this route
                break
            # Select the nearest candidate
            candidates.sort(key=lambda x: x[0])
            nearest_customer = candidates[0][1]
            # Add to route
            route.append(nearest_customer)
            load += nodes[nearest_customer]['demand']
            unserved.remove(nearest_customer)
            current_node = nearest_customer
        # Add constructed route to routes list
        routes.append(route)
    return routes

