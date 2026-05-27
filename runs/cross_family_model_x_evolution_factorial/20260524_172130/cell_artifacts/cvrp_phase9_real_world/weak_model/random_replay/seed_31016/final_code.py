def solve_cvrp(instance):
    # Unpack instance data
    customers = instance['customers']
    depot = instance['depot']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Prepare list of customers with their demands and coordinates
    customer_list = []
    for customer in customers:
        customer_id = customer['id']
        demand = customer['demand']
        x = customer['x']
        y = customer['y']
        customer_list.append({
            'id': customer_id,
            'demand': demand,
            'x': x,
            'y': y
        })
    
    # Initialize unvisited customers
    unvisited = customer_list.copy()
    routes = []

    # Helper functions
    def distance(a, b):
        return ((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2) ** 0.5

    # Build routes using a greedy nearest neighbor approach
    while unvisited:
        route = []
        load = 0
        current_node = depot
        remaining_customers = unvisited.copy()

        while True:
            # Find feasible customers
            feasible_customers = [
                c for c in remaining_customers
                if load + c['demand'] <= vehicle_capacity
            ]
            if not feasible_customers:
                break
            # Select nearest feasible customer
            next_customer = min(
                feasible_customers,
                key=lambda c: distance(current_node, c)
            )

            # Append customer to route
            route.append(next_customer['id'])
            load += next_customer['demand']
            # Update current node
            current_node = next_customer
            # Remove from unvisited
            remaining_customers.remove(next_customer)

        # Remove visited customers from unvisited list
        for c_id in route:
            unvisited = [c for c in unvisited if c['id'] != c_id]
        routes.append(route)

    # Improve routes: attempt to merge routes if capacity allows
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]

                # Calculate total demand
                demand_i = sum(c['demand'] for c in customers if c['id'] in route_i)
                demand_j = sum(c['demand'] for c in customers if c['id'] in route_j)

                if demand_i + demand_j <= vehicle_capacity:
                    # Merge routes
                    routes[i] = route_i + route_j
                    del routes[j]
                    improved = True
                    break
            if improved:
                break

    return routes

