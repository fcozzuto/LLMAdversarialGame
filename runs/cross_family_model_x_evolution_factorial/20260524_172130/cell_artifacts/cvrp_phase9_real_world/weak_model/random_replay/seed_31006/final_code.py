def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) for the given instance.
    Returns a list of routes, each route is a list of customer ids (excluding depot),
    respecting vehicle capacity, and visiting all customers exactly once.
    """
    # Parse the instance data
    customers = instance['customers']  # List of dicts with 'id', 'x', 'y', 'demand'
    capacity = instance['vehicle_capacity']
    depot = instance['depot']  # Dict with 'id', 'x', 'y'
    
    # Create a dictionary for quick access
    customer_dict = {c['id']: c for c in customers}
    
    # Initialize list of unvisited customers
    unvisited = set(c['id'] for c in customers)
    
    # List to store routes
    routes = []
    
    # Function to compute Euclidean distance between two customers
    def distance(c1, c2):
        dx = c1['x'] - c2['x']
        dy = c1['y'] - c2['y']
        return (dx*dx + dy*dy) ** 0.5
    
    # Build routes using a greedy nearest neighbor approach with capacity constraints
    while unvisited:
        route = []
        load = 0
        current_location = depot
        # While there are unvisited customers that can fit in the vehicle
        while True:
            # Find nearest unvisited customer that can be served within capacity
            candidates = []
            for cid in unvisited:
                customer = customer_dict[cid]
                if load + customer['demand'] <= capacity:
                    dist = distance(current_location, customer)
                    candidates.append((dist, customer))
            if not candidates:
                # No suitable customer found, finish current route
                break
            # Select the nearest candidate
            candidates.sort(key=lambda x: x[0])
            next_customer = candidates[0][1]
            # Append to route
            route.append(next_customer['id'])
            load += next_customer['demand']
            current_location = next_customer
            unvisited.remove(next_customer['id'])
        # Append completed route
        routes.append(route)
    
    # Repair step: attempt to improve routes locally
    # For simplicity, perform a single pass of customer swaps between routes if it reduces total distance
    # and maintains capacity constraints
    def total_distance(routes_list):
        total = 0
        for r in routes_list:
            prev = depot
            for cid in r:
                c = customer_dict[cid]
                total += distance(prev, c)
                prev = c
            total += distance(prev, depot)
        return total
    
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for idx_i in range(len(route_i)):
                    for idx_j in range(len(route_j)):
                        cid_i = route_i[idx_i]
                        cid_j = route_j[idx_j]
                        c_i = customer_dict[cid_i]
                        c_j = customer_dict[cid_j]
                        # Check capacity constraints if we swap customers
                        load_i = sum(customer_dict[cid].get('demand', 0) for cid in route_i) - c_i['demand'] + c_j['demand']
                        load_j = sum(customer_dict[cid].get('demand', 0) for cid in route_j) - c_j['demand'] + c_i['demand']
                        if load_i <= capacity and load_j <= capacity:
                            # Perform swap
                            new_route_i = route_i.copy()
                            new_route_j = route_j.copy()
                            new_route_i[idx_i] = cid_j
                            new_route_j[idx_j] = cid_i
                            # Check if total distance improves
                            new_routes = routes.copy()
                            new_routes[i] = new_route_i
                            new_routes[j] = new_route_j
                            if total_distance(new_routes) < total_distance(routes):
                                routes = new_routes
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
    
    return routes

