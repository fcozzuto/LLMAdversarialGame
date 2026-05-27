def solve_cvrp(instance):
    # Extract data from the instance
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['capacity']
    
    # Initialize list of unserved customers
    unserved_customers = customers.copy()
    
    # Initialize routes list
    routes = []

    # Helper function to compute total demand of a set of customers
    def total_demand(customers_list):
        return sum(cust['demand'] for cust in customers_list)

    # Helper function to build a route starting from depot and connecting customers in a greedy manner
    def build_route(start_customer):
        route = []
        current_customer = start_customer
        load = current_customer['demand']
        route_customers = [current_customer]
        remaining_customers = [cust for cust in unserved_customers if cust != current_customer]
        
        while True:
            # Find next customer closest to current_customer that fits in capacity
            next_customer = None
            min_distance = float('inf')
            for cust in remaining_customers:
                if load + cust['demand'] <= vehicle_capacity:
                    # Calculate distance
                    dist = (current_customer['x'] - cust['x'])**2 + (current_customer['y'] - cust['y'])**2
                    # Use squared distance for deterministic selection
                    if dist < min_distance:
                        min_distance = dist
                        next_customer = cust
            if next_customer is None:
                # No suitable next customer, close route by returning to depot
                break
            # Add next customer to route
            route_customers.append(next_customer)
            load += next_customer['demand']
            remaining_customers.remove(next_customer)
            current_customer = next_customer
        return route_customers

    # Main constructive phase: build routes by repeatedly selecting the unserved customer farthest from depot
    while unserved_customers:
        # Select the customer farthest from depot (deterministic seed)
        start_customer = max(unserved_customers, key=lambda c: (c['x'] - depot['x'])**2 + (c['y'] - depot['y'])**2)
        # Build a route starting from this customer
        route_customers = build_route(start_customer)
        # Mark these customers as served
        for cust in route_customers:
            unserved_customers.remove(cust)
        # Append route (excluding depot)
        route_ids = [cust['id'] for cust in route_customers]
        routes.append(route_ids)

    # Improve routes with a simple local search: try to swap customers between routes to reduce total distance
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Convert to customer objects
                customers_i = [next(c for c in customers if c['id'] == cid) for cid in route_i]
                customers_j = [next(c for c in customers if c['id'] == cid) for cid in route_j]
                for idx_i, cust_i in enumerate(customers_i):
                    for idx_j, cust_j in enumerate(customers_j):
                        # Check capacity constraints
                        demand_i = sum(c['demand'] for c in customers_i)
                        demand_j = sum(c['demand'] for c in customers_j)
                        if (demand_i - cust_i['demand'] + cust_j['demand'] <= vehicle_capacity and
                            demand_j - cust_j['demand'] + cust_i['demand'] <= vehicle_capacity):
                            # Swap customers
                            new_customers_i = customers_i.copy()
                            new_customers_j = customers_j.copy()
                            new_customers_i[idx_i], new_customers_j[idx_j] = customers_j[idx_j], customers_i[idx_i]
                            # Calculate total route distances
                            def route_distance(route_customers):
                                total_dist = 0.0
                                prev_point = depot
                                for c in route_customers:
                                    total_dist += ((prev_point['x'] - c['x'])**2 + (prev_point['y'] - c['y'])**2)**0.5
                                    prev_point = c
                                # Return to depot
                                total_dist += ((prev_point['x'] - depot['x'])**2 + (prev_point['y'] - depot['y'])**2)**0.5
                                return total_dist
                            new_route_i = new_customers_i
                            new_route_j = new_customers_j
                            dist_i = route_distance(new_route_i)
                            dist_j = route_distance(new_route_j)
                            old_dist_i = route_distance(customers_i)
                            old_dist_j = route_distance(customers_j)
                            if dist_i + dist_j < old_dist_i + old_dist_j:
                                # Accept swap
                                routes[i] = [c['id'] for c in new_route_i]
                                routes[j] = [c['id'] for c in new_route_j]
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes

