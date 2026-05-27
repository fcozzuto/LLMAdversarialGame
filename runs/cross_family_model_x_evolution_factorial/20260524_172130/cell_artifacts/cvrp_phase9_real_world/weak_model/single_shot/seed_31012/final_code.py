def solve_cvrp(instance):
    # Instance is assumed to be a dictionary with:
    # 'depot': depot node id
    # 'customers': list of customer node ids
    # 'demand': dict {customer_id: demand}
    # 'distance': function taking two node ids and returning distance
    # 'vehicle_capacity': maximum capacity per vehicle

    depot = instance['depot']
    customers = instance['customers']
    demand = instance['demand']
    distance = instance['distance']
    capacity = instance['vehicle_capacity']

    # Initialize unvisited customers
    unvisited = set(customers)
    routes = []

    while unvisited:
        route = []
        remaining_capacity = capacity
        current_node = depot

        # Greedy construction: repeatedly select the nearest unvisited customer
        while True:
            # Find all unvisited customers that fit in remaining capacity
            feasible_customers = [c for c in unvisited if demand[c] <= remaining_capacity]
            if not feasible_customers:
                # Cannot add more customers in this route
                break
            # Select the closest feasible customer
            next_customer = min(feasible_customers, key=lambda c: distance(current_node, c))
            # Add to route
            route.append(next_customer)
            unvisited.remove(next_customer)
            remaining_capacity -= demand[next_customer]
            current_node = next_customer

        routes.append(route)

    return routes

