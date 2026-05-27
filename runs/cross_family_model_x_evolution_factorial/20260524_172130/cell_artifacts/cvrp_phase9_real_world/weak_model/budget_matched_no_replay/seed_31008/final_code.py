def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) with deterministic, interpretable logic.
    Returns a list of routes, each route is a list of customer IDs (excluding depot), covering all customers exactly once.
    """
    # Extract necessary data from instance
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customer data: (customer_id, demand, distance to depot)
    customer_list = []
    for cust_id, demand, coords in customers.items():
        customer_list.append((cust_id, demand, coords))
    
    # Initialize list of unvisited customers
    unvisited = set(cust_id for cust_id, _, _ in customer_list)
    
    # Function to compute Euclidean distance
    def distance(coord1, coord2):
        return ((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)**0.5
    
    # Build a dict for quick coordinate lookup
    coords_dict = {cust_id: coords for cust_id, _, coords in customer_list}
    
    # Build demand dict
    demand_dict = {cust_id: demand for cust_id, demand, _ in customer_list}
    
    # Build a dict for customer distances to depot
    depot_coords = depot
    dist_to_depot = {cust_id: distance(coords_dict[cust_id], depot_coords) for cust_id in unvisited}
    
    routes = []
    
    # Build routes until all customers are visited
    while unvisited:
        route = []
        current_load = 0
        current_location = depot_coords
        
        # While there are still customers to add in the current route
        while True:
            # Select among unvisited customers the next customer to visit
            candidates = []
            for cust_id in unvisited:
                demand_cust = demand_dict[cust_id]
                # Check capacity constraint
                if current_load + demand_cust <= capacity:
                    # Distance from current location to customer
                    dist_cust = distance(current_location, coords_dict[cust_id])
                    # Optional: prioritize closer customers
                    candidates.append((cust_id, dist_cust))
            
            if not candidates:
                # No valid customers left for this route
                break
            
            # Pick the nearest customer
            candidates.sort(key=lambda x: x[1])
            next_cust_id = candidates[0][0]
            
            # Add customer to route
            route.append(next_cust_id)
            current_load += demand_dict[next_cust_id]
            current_location = coords_dict[next_cust_id]
            unvisited.remove(next_cust_id)
        
        routes.append(route)
    
    # Optional local improvement: attempt to re-route customers to shorter routes
    # For simplicity, in this deterministic build, no further improvements are implemented
    
    return routes

