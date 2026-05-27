def solve_cvrp(instance):
    # instance: dict with keys:
    # 'demand': list of demands per customer (index 0 is depot, ignored in routes)
    # 'distance': 2D list of distances between nodes (including depot at index 0)
    # 'vehicle_capacity': maximum capacity per vehicle

    demands = instance['demand']
    distance = instance['distance']
    capacity = instance['vehicle_capacity']

    n_customers = len(demands) - 1  # excluding depot at index 0

    # Create a list of customer ids
    customers = list(range(1, n_customers + 1))
    # Initialize list of unvisited customers
    unvisited = set(customers)

    routes = []

    while unvisited:
        route = []
        remaining_capacity = capacity
        current_node = 0  # start from depot

        # Greedy construction: sequentially add the closest feasible customer
        while True:
            # Find the feasible customers with demands less than remaining capacity
            feasible_customers = [c for c in unvisited if demands[c] <= remaining_capacity]
            if not feasible_customers:
                break

            # Select the closest feasible customer
            next_customer = min(feasible_customers, key=lambda c: distance[current_node][c])

            # Add to route
            route.append(next_customer)
            remaining_capacity -= demands[next_customer]
            unvisited.remove(next_customer)
            current_node = next_customer

        routes.append(route)

    # Optional: improve routes by local search (swap neighbors if beneficial)
    # Here, for simplicity, we just keep the constructed routes.

    return routes

