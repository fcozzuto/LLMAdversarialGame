def solve_cvrp(instance):
    """
    Solve a Capacitated Vehicle Routing Problem (CVRP) instance deterministically,
    constructing routes that cover all customers without exceeding vehicle capacity.
    
    Args:
        instance: dict with keys:
            - 'depot': int (the depot node id)
            - 'customers': list of dicts, each with:
                - 'id': int
                - 'demand': int
            - 'distance': dict with keys (from_node, to_node) and values as distances
            - 'vehicle_capacity': int
    
    Returns:
        routes: list of lists, each sublist is a route (sequence of customer ids)
    """
    # Extract data
    depot = instance['depot']
    customers = instance['customers']
    distance = instance['distance']
    capacity = instance['vehicle_capacity']
    
    # Map customer id to demand
    customer_demands = {c['id']: c['demand'] for c in customers}
    unvisited = set(customer_demands.keys())
    
    routes = []
    
    # Function to compute total demand of a set of customers
    def total_demand(customers_subset):
        return sum(customer_demands[cid] for cid in customers_subset)
    
    # For each route, build greedily
    while unvisited:
        route = []
        current_node = depot
        load = 0
        route_customers = []
        
        # Candidates: unvisited customers
        candidates = list(unvisited)
        
        while candidates:
            # Select the nearest feasible customer
            feasible_candidates = []
            for cid in candidates:
                demand_cid = customer_demands[cid]
                if load + demand_cid <= capacity:
                    dist = distance.get((current_node, cid), float('inf'))
                    feasible_candidates.append((dist, cid))
            # If no feasible candidate, end route
            if not feasible_candidates:
                break
            # Select candidate with minimal distance
            feasible_candidates.sort(key=lambda x: x[0])
            _, selected_cid = feasible_candidates[0]
            # Add selected customer to route
            route.append(selected_cid)
            unvisited.remove(selected_cid)
            load += customer_demands[selected_cid]
            current_node = selected_cid
            candidates = list(unvisited)
        
        routes.append(route)
    
    # Return the list of routes (excluding depot)
    return routes

