def solve_cvrp(instance):
    # Instance expected format:
    # {
    #   'depot': depot_id,
    #   'customers': {
    #       customer_id: {
    #           'demand': int,
    #           'location': (x, y)
    #       },
    #       ...
    #   },
    #   'vehicle_capacity': int
    # }
    
    # Extract data
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Prepare list of customers with demands
    customer_list = list(customers.items())  # [(cust_id, {'demand': d, 'location': (x, y)}), ...]
    
    # Helper functions
    def distance(cust1, cust2):
        loc1 = customers[cust1]['location'] if cust1 != depot else (0, 0)
        loc2 = customers[cust2]['location'] if cust2 != depot else (0, 0)
        dx = loc1[0] - loc2[0]
        dy = loc1[1] - loc2[1]
        return (dx*dx + dy*dy) ** 0.5
    
    def route_cost(route):
        total = 0.0
        prev = depot
        for cust_id in route:
            total += distance(prev, cust_id)
            prev = cust_id
        total += distance(prev, depot)
        return total
    
    # Step 1: Construct initial solution using a greedy nearest-neighbor approach
    unassigned = set([cust_id for cust_id, _ in customer_list])
    routes = []
    
    while unassigned:
        route = []
        load = 0
        current = depot
        while True:
            # Find nearest customer that fits in capacity
            candidates = []
            for c_id in unassigned:
                demand = customers[c_id]['demand']
                if load + demand <= capacity:
                    dist = distance(current, c_id)
                    candidates.append((dist, c_id))
            if not candidates:
                break
            # Pick nearest neighbor
            candidates.sort()
            chosen_id = candidates[0][1]
            route.append(chosen_id)
            load += customers[chosen_id]['demand']
            unassigned.remove(chosen_id)
            current = chosen_id
        routes.append(route)
    
    # Step 2: Improvement by local swapping (simple relocation)
    # For interpretability, do a limited number of swaps
    improved = True
    attempt = 0
    max_attempts = 10
    while improved and attempt < max_attempts:
        improved = False
        for i in range(len(routes)):
            for j in range(i, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for idx_i in range(len(route_i)):
                    for idx_j in range(len(route_j)):
                        cust_i_id = route_i[idx_i]
                        cust_j_id = route_j[idx_j]
                        demand_i = customers[cust_i_id]['demand']
                        demand_j = customers[cust_j_id]['demand']
                        load_i = sum(customers[c]['demand'] for c in route_i) - demand_i + demand_j
                        load_j = sum(customers[c]['demand'] for c in route_j) - demand_j + demand_i
                        if load_i <= capacity and load_j <= capacity:
                            # Swap customers
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[idx_i] = cust_j_id
                            new_route_j[idx_j] = cust_i_id
                            # Check if better (less total distance)
                            old_cost = route_cost(route_i) + route_cost(route_j)
                            new_cost = route_cost(new_route_i) + route_cost(new_route_j)
                            if new_cost < old_cost:
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
        attempt += 1
    
    # Final output: list of routes without depot
    return routes

