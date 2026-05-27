def solve_cvrp(instance):
    # instance should be a dictionary with keys:
    # 'depot': depot_id, 'customers': list of customer dicts with 'id', 'demand', 'x', 'y'
    # 'vehicle_capacity': int
    
    depot_id = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Initialize unvisited customers as a dict for quick lookup
    unvisited = {c['id']: c for c in customers}
    
    routes = []

    # While there are customers left to visit
    while unvisited:
        current_load = 0
        route = []
        last_location = None  # Will hold the last customer visited in the route
        route_unvisited_ids = list(unvisited.keys())

        # start with the depot, set last_location to depot position if needed
        # but since depot is not in route, we'll just initialize last_location as undefined
        
        # Build a route greedily
        while route_unvisited_ids:
            # Filter customers that fit into remaining capacity
            suitable_customers = [cid for cid in route_unvisited_ids
                                  if unvisited[cid]['demand'] + current_load <= capacity]
            if not suitable_customers:
                break  # Can't add more customers to this route
            
            # Select the 'closest' customer to the last position
            # For the first customer, pick the one closest to the depot
            if last_location is None:
                # find customer closest to depot
                def distance_to_depot(c):
                    dx = unvisited[c]['x'] - instance['depot_x']
                    dy = unvisited[c]['y'] - instance['depot_y']
                    return dx*dx + dy*dy
                # get depot coordinates
                depot_x = instance.get('depot_x')
                depot_y = instance.get('depot_y')
                if depot_x is None or depot_y is None:
                    # if not provided, assume 0,0
                    depot_x = 0
                    depot_y = 0
                # find closest customer to depot
                closest_cid = min(suitable_customers, key=lambda c: (unvisited[c]['x'] - depot_x)**2 + (unvisited[c]['y'] - depot_y)**2)
            else:
                # find closest customer to last_location
                def dist(c):
                    dx = unvisited[c]['x'] - last_location['x']
                    dy = unvisited[c]['y'] - last_location['y']
                    return dx*dx + dy*dy
                closest_cid = min(suitable_customers, key=dist)
            
            # Assign customer
            customer = unvisited[closest_cid]
            route.append(customer['id'])
            current_load += customer['demand']
            last_location = customer
            # Remove from unvisited
            del unvisited[closest_cid]
            route_unvisited_ids.remove(closest_cid)
        
        routes.append(route)
    
    return routes
