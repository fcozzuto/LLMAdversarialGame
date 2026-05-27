def solve_cvrp(instance):
    """
    Solve a Capacitated Vehicle Routing Problem (CVRP) instance using a deterministic,
    interpretable approach that combines constructive, repair, and local search techniques.
    """
    # Unpack instance data
    customers = instance['customers']  # list of dicts with keys: 'id', 'demand', 'x', 'y'
    depot = instance['depot']  # dict with keys: 'x', 'y'
    capacity = instance['vehicle_capacity']
    
    # Create a list of unvisited customer ids
    unvisited = [cust['id'] for cust in customers]
    # Map customer id to customer data
    customer_map = {cust['id']: cust for cust in customers}
    
    routes = []  # list of routes, each route is a list of customer ids
    # Helper function to compute Euclidean distance
    def distance(c1, c2):
        dx = c1['x'] - c2['x']
        dy = c1['y'] - c2['y']
        return (dx*dx + dy*dy) ** 0.5
    
    # Step 1: Construct initial routes with a greedy nearest neighbor approach
    while unvisited:
        route = []
        load = 0
        current_location = depot
        # Copy unvisited for this route
        remaining_customers = unvisited[:]
        while remaining_customers:
            # Find the nearest customer that can be served without exceeding capacity
            nearest_cust = None
            min_dist = float('inf')
            for cid in remaining_customers:
                cust = customer_map[cid]
                if load + cust['demand'] <= capacity:
                    dist = distance(current_location, cust)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_cust = cid
            if nearest_cust is None:
                # Cannot add more customers to this route
                break
            # Add the selected customer to route
            route.append(nearest_cust)
            load += customer_map[nearest_cust]['demand']
            current_location = customer_map[nearest_cust]
            remaining_customers.remove(nearest_cust)
        # Remove served customers from unvisited
        for cid in route:
            if cid in unvisited:
                unvisited.remove(cid)
        routes.append(route)
    
    # Step 2: Improve routes with a simple local search: swap customers between routes if beneficial
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i, len(routes)):
                route_a = routes[i]
                route_b = routes[j]
                for ia in range(len(route_a)):
                    for ib in range(len(route_b)):
                        c_a = customer_map[route_a[ia]]
                        c_b = customer_map[route_b[ib]]
                        # Check capacity constraints after swap
                        load_a = sum(customer_map[cid]['demand'] for cid in route_a) - c_a['demand'] + c_b['demand']
                        load_b = sum(customer_map[cid]['demand'] for cid in route_b) - c_b['demand'] + c_a['demand']
                        if load_a <= capacity and load_b <= capacity:
                            # Calculate current total distance
                            def route_distance(route):
                                dist = 0.0
                                prev = depot
                                for cid in route:
                                    dist += distance(prev, customer_map[cid])
                                    prev = customer_map[cid]
                                dist += distance(prev, depot)
                                return dist
                            # Compute old and new distances
                            old_dist = route_distance(route_a) + route_distance(route_b)
                            # Swap customers
                            new_route_a = route_a[:]
                            new_route_b = route_b[:]
                            new_route_a[ia], new_route_b[ib] = route_b[ib], route_a[ia]
                            new_dist = route_distance(new_route_a) + route_distance(new_route_b)
                            if new_dist < old_dist:
                                # Accept swap
                                routes[i] = new_route_a
                                routes[j] = new_route_b
                                improved = True
    return routes

