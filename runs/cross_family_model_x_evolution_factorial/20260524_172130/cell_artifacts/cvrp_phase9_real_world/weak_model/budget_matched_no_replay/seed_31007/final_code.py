def solve_cvrp(instance):
    # Parse input instance
    # instance is expected to be a dict with keys:
    # 'distance_matrix': 2D list of distances
    # 'demands': list of demands per customer (index 0 is depot with demand=0)
    # 'vehicle_capacity': integer
    
    distance_matrix = instance['distance_matrix']
    demands = instance['demands']
    capacity = instance['vehicle_capacity']
    n_customers = len(demands) - 1  # number of customers
    depot = 0
    
    # Initialize unvisited customers
    unvisited = set(range(1, n_customers + 1))
    routes = []
    
    # Helper function to compute total demand of a route
    def route_demand(route):
        return sum(demands[cust] for cust in route)
    
    # Greedy construction: build routes by selecting customers based on nearest neighbor
    while unvisited:
        current_route = []
        current_load = 0
        current_node = depot
        
        # Build a route until no more customers can be added
        while True:
            # Candidates are unvisited customers that fit in the remaining capacity
            candidates = [c for c in unvisited if demands[c] + current_load <= capacity]
            if not candidates:
                # No more customers can be added to current route
                break
            # select the closest candidate to current_node
            next_customer = min(candidates, key=lambda c: distance_matrix[current_node][c])
            # add to route
            current_route.append(next_customer)
            unvisited.remove(next_customer)
            current_load += demands[next_customer]
            current_node = next_customer
        
        # Append the constructed route
        routes.append(current_route)
    
    # Improving solution with a simple 2-opt-like local improvement (deterministic)
    improved = True
    while improved:
        improved = False
        for route_idx, route in enumerate(routes):
            route_size = len(route)
            if route_size < 3:
                continue
            # Try all pairs to find local improvements
            for i in range(route_size - 1):
                for j in range(i + 2, route_size):
                    # Swap segment between i+1 and j
                    new_route = route[:i+1] + route[i+1:j+1][::-1] + route[j+1:]
                    # Check if demands still fit (they should, as demand sum didn't change)
                    # but the route change might reduce total distance
                    current_distance = sum(distance_matrix[route[k]][route[k+1]] for k in range(route_size - 1))
                    new_distance = sum(distance_matrix[new_route[k]][new_route[k+1]] for k in range(route_size - 1))
                    if new_distance < current_distance:
                        routes[route_idx] = new_route
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break
    
    # Return the list of routes without depot (only customer sequence)
    return routes

