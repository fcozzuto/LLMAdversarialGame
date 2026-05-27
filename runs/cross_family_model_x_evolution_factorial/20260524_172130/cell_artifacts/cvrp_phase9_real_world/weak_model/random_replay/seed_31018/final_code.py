def solve_cvrp(instance):
    """
    Solves a Capacitated Vehicle Routing Problem (CVRP) instance using a deterministic,
    interpretable, constructive heuristic with local improvements.
    
    Args:
        instance (dict): Contains 'customers', 'depot', 'vehicle_capacity'
            - 'customers': list of dicts with 'id', 'x', 'y', 'demand'
            - 'depot': dict with 'id', 'x', 'y'
            - 'vehicle_capacity': int or float
            
    Returns:
        routes (list of list): Each route is a list of customer ids assigned to a vehicle.
    """
    # Extract data
    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']
    
    # Initialize unvisited customers
    unvisited = {c['id']: c for c in customers}
    
    # Helper function to compute Euclidean distance
    def distance(c1, c2):
        dx = c1['x'] - c2['x']
        dy = c1['y'] - c2['y']
        return (dx*dx + dy*dy)**0.5
    
    # Build a list of customer ids sorted by proximity to depot for initial routes
    # this provides a deterministic, simple starting point
    sorted_customers = sorted(unvisited.values(), key=lambda c: distance(c, depot))
    
    routes = []
    
    # Construct initial routes greedily
    while unvisited:
        route = []
        load = 0
        current_location = depot  # start from depot
        to_remove = []
        for cust in sorted_customers:
            if cust['id'] in unvisited:
                demand = cust['demand']
                if load + demand <= capacity:
                    # Add customer to route
                    route.append(cust['id'])
                    load += demand
                    unvisited.pop(cust['id'])
                    to_remove.append(cust)
                # Else, skip for now
        # Re-sort remaining customers by proximity to last visited customer
        # For interpretability, we re-sort based on distance to last customer added
        if route:
            last_customer = None
            if route:
                last_customer = next(c for c in customers if c['id'] == route[-1])
            else:
                last_customer = depot
            remaining_customers = [c for c in unvisited.values()]
            sorted_customers = sorted(remaining_customers, key=lambda c: distance(c, last_customer))
            routes.append(route)
        else:
            # No customers could be assigned (should not happen)
            break
    # Now we have initial routes; attempt to improve via simple local search
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            route_i = routes[i]
            for j in range(i+1, len(routes)):
                route_j = routes[j]
                # Try to swap customers between routes if it improves total route length
                for idx_i, cust_id_i in enumerate(route_i):
                    cust_i = next(c for c in customers if c['id'] == cust_id_i)
                    for idx_j, cust_id_j in enumerate(route_j):
                        cust_j = next(c for c in customers if c['id'] == cust_id_j)
                        # Check demand constraints
                        load_i = sum(next(c['demand'] for c in customers if c['id'] == cid) for cid in route_i)
                        load_j = sum(next(c['demand'] for c in customers if c['id'] == cid) for cid in route_j)
                        new_load_i = load_i - cust_i['demand'] + cust_j['demand']
                        new_load_j = load_j - cust_j['demand'] + cust_i['demand']
                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Calculate current and new route lengths
                            def route_length(route):
                                length = distance(depot, next(c for c in customers if c['id'] == route[0]))
                                for k in range(len(route)-1):
                                    c1 = next(c for c in customers if c['id'] == route[k])
                                    c2 = next(c for c in customers if c['id'] == route[k+1])
                                    length += distance(c1, c2)
                                length += distance(next(c for c in customers if c['id'] == route[-1]), depot)
                                return length
                            current_length = route_length(route_i) + route_length(route_j)
                            # Swap customers
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[idx_i] = cust_j['id']
                            new_route_j[idx_j] = cust_i['id']
                            new_length = route_length(new_route_i) + route_length(new_route_j)
                            if new_length < current_length:
                                # Accept swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
    # Return routes without depot visits
    return routes

