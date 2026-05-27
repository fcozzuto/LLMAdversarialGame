def solve_cvrp(instance):
    """
    Construct a feasible CVRP solution using a deterministic, interpretable heuristic,
    building routes greedily based on nearest neighbor and capacity constraints.
    """
    # Extract data from instance
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']

    # Create a list of unvisited customers
    unvisited = set(customers.keys())

    routes = []

    # Function to compute distance between two points
    def distance(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    # Build a route starting from the depot
    while unvisited:
        route = []
        load = 0
        current_location = depot

        # While there are unvisited customers, select the closest feasible one
        while True:
            # Find feasible customers
            feasible_customers = []
            for c_id in unvisited:
                c = customers[c_id]
                if load + c['demand'] <= vehicle_capacity:
                    dist = distance(current_location, c)
                    feasible_customers.append((dist, c_id))
            if not feasible_customers:
                break
            # Select nearest feasible customer
            feasible_customers.sort(key=lambda x: x[0])
            next_customer_id = feasible_customers[0][1]
            next_customer = customers[next_customer_id]
            # Add to route
            route.append(next_customer_id)
            unvisited.remove(next_customer_id)
            load += next_customer['demand']
            current_location = next_customer

        # Append the built route
        routes.append(route)

    return routes

