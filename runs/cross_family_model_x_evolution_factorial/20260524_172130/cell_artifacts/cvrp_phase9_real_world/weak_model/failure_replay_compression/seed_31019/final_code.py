def solve_cvrp(instance):
    # Extract data
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Initialize unvisited customers set
    unvisited = set(customers.keys())
    routes = []
    
    # Helper function to compute the distance between two points
    def dist(p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
    
    # Helper function to select the next customer greedily
    def select_next(current_location, remaining_customers, remaining_capacity):
        nearest_customer = None
        min_distance = float('inf')
        for c_id in remaining_customers:
            customer_loc = customers[c_id]
            d = dist(current_location, customer_loc)
            if d < min_distance:
                min_distance = d
                nearest_customer = c_id
        # Check if selecting this customer exceeds capacity
        if nearest_customer is not None:
            demand = customers[nearest_customer][2]
            if demand <= remaining_capacity:
                return nearest_customer
        return None

    # Construct routes
    while unvisited:
        route = []
        remaining_capacity = vehicle_capacity
        current_location = depot

        while True:
            next_customer = select_next(current_location, unvisited, remaining_capacity)
            if next_customer is None:
                # No suitable next customer
                break
            # Add customer to route
            route.append(next_customer)
            remaining_capacity -= customers[next_customer][2]
            current_location = customers[next_customer]
            unvisited.remove(next_customer)

        if route:
            routes.append(route)
        else:
            # No progress, break to avoid infinite loop
            break

    # Improvement step: simple local swapping within routes
    # For simplicity, attempt to swap customers in different routes if it reduces total distance
    # Since the problem states determinism and interpretability, keep it simple
    changed = True
    while changed:
        changed = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for ci in range(len(route_i)):
                    for cj in range(len(route_j)):
                        # Swap customers
                        c_i, c_j = route_i[ci], route_j[cj]
                        demand_i = customers[c_i][2]
                        demand_j = customers[c_j][2]
                        # Check capacity constraints
                        cap_i = sum(customers[c][2] for c in route_i) - demand_i + demand_j
                        cap_j = sum(customers[c][2] for c in route_j) - demand_j + demand_i
                        if cap_i <= vehicle_capacity and cap_j <= vehicle_capacity:
                            # Compute current distances
                            def route_distance(route):
                                total = 0
                                prev = depot
                                for c in route:
                                    total += dist(prev, customers[c])
                                    prev = customers[c]
                                total += dist(prev, depot)
                                return total
                            # Current total
                            current_total = route_distance(route_i) + route_distance(route_j)
                            # Swap and compute new total
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[ci], new_route_j[cj] = new_route_j[cj], new_route_i[ci]
                            new_total = route_distance(new_route_i) + route_distance(new_route_j)
                            if new_total < current_total:
                                # Accept swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                changed = True
        # Repeat until no improvement

    return routes

