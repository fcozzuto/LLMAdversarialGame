def solve_cvrp(instance):
    # Extract data from instance
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Create a list of all customers with their demands and positions
    customer_list = list(customers.items())  # (customer_id, data)
    unvisited = set([cid for cid, data in customer_list])
    
    routes = []

    while unvisited:
        current_route = []
        current_load = 0
        current_position = depot
        # Build one route
        while True:
            # Find feasible customers to visit next
            feasible_candidates = []
            for cid in unvisited:
                cdata = customers[cid]
                demand = cdata['demand']
                if demand + current_load <= vehicle_capacity:
                    feasible_candidates.append((cid, cdata))
            if not feasible_candidates:
                break
            # Select the closest feasible customer to the current position
            feasible_candidates.sort(key=lambda c: ((c[1]['pos'][0] - current_position[0])**2 + (c[1]['pos'][1] - current_position[1])**2)**0.5)
            next_cid, next_cdata = feasible_candidates[0]
            # Add to route
            current_route.append(next_cid)
            current_load += next_cdata['demand']
            current_position = next_cdata['pos']
            unvisited.remove(next_cid)
        routes.append(current_route)
    return routes

