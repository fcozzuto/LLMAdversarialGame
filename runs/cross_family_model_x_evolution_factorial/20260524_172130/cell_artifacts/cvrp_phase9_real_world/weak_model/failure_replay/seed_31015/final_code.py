def solve_cvrp(instance):
    # instance format:
    # instance = {
    #     'depot': int,
    #     'customers': list of dicts with keys: 'id', 'demand', 'x', 'y',
    #     'vehicle_capacity': int
    # }

    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customers not yet assigned
    unvisited = customers[:]
    routes = []

    # Helper function to compute Euclidean distance between two points
    def distance(c1, c2):
        return ((c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2) ** 0.5

    # Build a dictionary for quick lookup
    customer_map = {c['id']: c for c in customers}

    # Start constructing routes until all customers are assigned
    while unvisited:
        route = []
        load = 0
        current_node = {'id': depot, 'x': 0, 'y': 0}  # start at depot (coordinates arbitrarily 0,0)
        route_customers = []

        # Function to find the next customer to visit
        def select_next(current, remaining):
            # Select the nearest customer that can be served given capacity constraints
            min_dist = None
            candidate = None
            for c in remaining:
                if load + c['demand'] <= capacity:
                    dist = distance(current, c)
                    if (min_dist is None) or (dist < min_dist):
                        min_dist = dist
                        candidate = c
            return candidate

        # Build a route by greedy nearest neighbor approach
        while True:
            next_customer = select_next(current_node, unvisited)
            if next_customer is None:
                # No feasible next customer, close route
                break
            # Append customer to route
            route.append(next_customer['id'])
            load += next_customer['demand']
            current_node = next_customer
            unvisited.remove(next_customer)

        routes.append(route)

    return routes

