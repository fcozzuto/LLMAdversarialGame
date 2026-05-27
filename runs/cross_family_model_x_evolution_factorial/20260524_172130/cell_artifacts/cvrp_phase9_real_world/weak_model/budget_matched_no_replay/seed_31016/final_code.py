def solve_cvrp(instance):
    # instance is expected to be a dictionary with keys:
    # 'demands': list of demands per customer
    # 'coords': list of (x, y) positions including depot at index 0
    # 'vehicle_capacity': capacity of each vehicle

    demands = instance['demands']
    coords = instance['coords']
    capacity = instance['vehicle_capacity']
    num_customers = len(demands) - 1  # excluding depot at index 0

    # Initialize unvisited customers (excluding depot)
    unvisited = set(range(1, num_customers + 1))
    routes = []

    # Precompute distances between all nodes for deterministic selection
    def distance(i, j):
        xi, yi = coords[i]
        xj, yj = coords[j]
        return ((xi - xj)**2 + (yi - yj)**2)**0.5

    # For deterministic ordering, create a list of customer indices sorted by demand
    sorted_customers = sorted(unvisited, key=lambda c: demands[c])

    while unvisited:
        route = []
        load = 0
        current_node = 0  # start from depot
        current_capacity = capacity

        # Build route greedily: select next closest customer that fits
        remaining_customers = list(unvisited)
        # For deterministic behavior, sort remaining customers by distance from current node
        remaining_customers.sort(key=lambda c: distance(current_node, c))
        for customer in remaining_customers:
            demand_cust = demands[customer]
            if demand_cust <= current_capacity:
                # Add customer to route
                route.append(customer)
                current_capacity -= demand_cust
                current_node = customer
                unvisited.remove(customer)
            # If no more customers or capacity exhausted, stop
            if not unvisited:
                break
        routes.append(route)
    return routes

