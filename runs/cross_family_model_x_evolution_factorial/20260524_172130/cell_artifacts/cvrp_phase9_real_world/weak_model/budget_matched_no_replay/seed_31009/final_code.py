def solve_cvrp(instance):
    """
    Solve a Capacitated Vehicle Routing Problem (CVRP) instance using a deterministic, interpretable approach.
    Args:
        instance (dict): Dictionary with keys:
            - 'customer_demands': list of demands per customer (indexed from 0 for customer 0, etc.)
            - 'distance_matrix': 2D list of distances between all nodes (including depot at index 0)
            - 'vehicle_capacity': capacity of each vehicle
    Returns:
        routes (list): List of routes, each route is a list of customer IDs (excluding depot).
    """
    customer_demands = instance['customer_demands']
    distance_matrix = instance['distance_matrix']
    vehicle_capacity = instance['vehicle_capacity']

    num_customers = len(customer_demands)
    # Customers are numbered from 1 to num_customers; depot is at 0.

    # Initialization: list of unvisited customers
    unvisited = set(range(1, num_customers))
    routes = []

    while unvisited:
        current_route = []
        load = 0
        current_node = 0  # start at depot
        # Build route greedily: select next customer closest to current node
        while True:
            # find neighbors that are unvisited and fit into capacity
            candidates = []
            for customer in unvisited:
                demand = customer_demands[customer]
                if load + demand <= vehicle_capacity:
                    dist = distance_matrix[current_node][customer]
                    candidates.append((dist, customer))
            if not candidates:
                break
            # pick the closest
            candidates.sort(key=lambda x: x[0])
            next_customer = candidates[0][1]
            # add to route
            current_route.append(next_customer)
            load += customer_demands[next_customer]
            unvisited.remove(next_customer)
            current_node = next_customer
        routes.append(current_route)

    # Optional: improve routes by attempting local swaps or sequences if desired
    # Here, for simplicity, we skip complex local search techniques.
    return routes

