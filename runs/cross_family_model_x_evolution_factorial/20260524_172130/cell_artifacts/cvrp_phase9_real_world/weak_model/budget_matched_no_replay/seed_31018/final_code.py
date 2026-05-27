def solve_cvrp(instance):
    """
    Solves the Capacitated Vehicle Routing Problem (CVRP) for the given instance.
    
    Parameters:
    - instance: dict with keys:
        - 'demands': list of customer demands, index corresponds to customer id
        - 'coords': list of (x, y) tuples for each customer
        - 'vehicle_capacity': integer capacity of each vehicle
        - 'depot': index of depot (assumed 0)
    Returns:
    - routes: list of routes, each route is a list of customer ids (excluding depot)
    """
    demands = instance['demands']
    coords = instance['coords']
    capacity = instance['vehicle_capacity']
    depot = instance['depot']
    
    num_customers = len(demands)
    customer_ids = [i for i in range(num_customers) if i != depot]
    
    # Initialize unvisited customers
    unvisited = set(customer_ids)
    
    routes = []
    
    # Compute a simple distance function
    def distance(a, b):
        return ((coords[a][0] - coords[b][0]) ** 2 + (coords[a][1] - coords[b][1]) ** 2) ** 0.5
    
    # Build initial routes
    while unvisited:
        route = []
        load = 0
        current_node = depot
        # Greedy approach: keep adding nearest feasible customer
        while True:
            # Find feasible customers (not visited yet, demand fits)
            feasible_customers = [c for c in unvisited if demands[c] + load <= capacity]
            if not feasible_customers:
                break
            # Select nearest feasible customer
            next_customer = min(feasible_customers, key=lambda c: distance(current_node, c))
            # Append customer to route
            route.append(next_customer)
            load += demands[next_customer]
            unvisited.remove(next_customer)
            current_node = next_customer
        # Add constructed route
        routes.append(route)
    
    # Improvement phase: try to merge routes if possible
    # Since construction is straightforward, attempt pairwise merge if capacity allows
    merged = True
    while merged:
        merged = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                load_i = sum(demands[c] for c in route_i)
                load_j = sum(demands[c] for c in route_j)
                # Check if merging is feasible
                if load_i + load_j <= capacity:
                    # Merge feasible -- combined route
                    merged_route = route_i + route_j
                    # Remove old routes
                    routes.pop(j)
                    routes.pop(i)
                    # Add new merged route
                    routes.append(merged_route)
                    merged = True
                    break
            if merged:
                break
    
    # Local improvement: swap customers between routes if it reduces total distance
    # and respects capacity
    improvement = True
    while improvement:
        improvement = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                load_i = sum(demands[c] for c in route_i)
                load_j = sum(demands[c] for c in route_j)
                for idx_i in range(len(route_i)):
                    for idx_j in range(len(route_j)):
                        c1 = route_i[idx_i]
                        c2 = route_j[idx_j]
                        # Check capacity constraints after swap
                        new_load_i = load_i - demands[c1] + demands[c2]
                        new_load_j = load_j - demands[c2] + demands[c1]
                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Calculate distances before swap
                            def route_distance(route):
                                dist = 0
                                prev = depot
                                for c in route:
                                    dist += distance(prev, c)
                                    prev = c
                                dist += distance(prev, depot)
                                return dist
                            old_total = route_distance(route_i) + route_distance(route_j)
                            # Perform swap
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[idx_i] = c2
                            new_route_j[idx_j] = c1
                            new_total = route_distance(new_route_i) + route_distance(new_route_j)
                            if new_total < old_total:
                                # Accept swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improvement = True
        # Repeat until no further improvements
    
    return routes

