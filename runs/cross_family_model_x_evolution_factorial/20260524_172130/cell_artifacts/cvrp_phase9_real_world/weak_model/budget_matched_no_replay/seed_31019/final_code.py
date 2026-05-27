def solve_cvrp(instance):
    # Instance is assumed to be a dictionary with:
    # 'depot': depot node id
    # 'demands': dict of customer_id -> demand
    # 'dist': function(node1, node2) returning the distance between nodes
    # 'capacity': vehicle capacity
    depot = instance['depot']
    demands = instance['demands']
    dist = instance['dist']
    capacity = instance['capacity']
    
    # Gather all customer IDs
    customers = list(demands.keys())
    # Initialize unvisited customers set
    unvisited = set(customers)
    
    routes = []
    
    while unvisited:
        current_route = []
        remaining_capacity = capacity
        current_node = depot
        
        # Build a route greedily
        while True:
            # Find the closest unvisited customer that fits the remaining capacity
            candidate = None
            min_distance = None
            for customer in unvisited:
                demand = demands[customer]
                if demand <= remaining_capacity:
                    d = dist(current_node, customer)
                    if min_distance is None or d < min_distance:
                        min_distance = d
                        candidate = customer
            if candidate is None:
                # No suitable customer found, end current route
                break
            # Add candidate to route
            current_route.append(candidate)
            unvisited.remove(candidate)
            remaining_capacity -= demands[candidate]
            current_node = candidate
        
        routes.append(current_route)
    
    return routes

