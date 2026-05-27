def solve_cvrp(instance):
    # Instance expected to be a dict with keys:
    # 'distance_matrix': 2D list or array where distance_matrix[i][j] is distance from node i to node j
    # 'demands': list where demands[i] is demand of customer i; assuming index 0 is depot
    # 'capacity': vehicle capacity
    # Customer ids are from 1 to n (excluding depot 0)

    distance_matrix = instance['distance_matrix']
    demands = instance['demands']
    capacity = instance['capacity']

    num_customers = len(demands) - 1  # excluding depot
    customers = list(range(1, num_customers + 1))

    # Step 1: Construct initial routes via a simple greedy heuristic
    unvisited = set(customers)
    routes = []

    while unvisited:
        route = []
        load = 0
        current_node = 0  # start from depot
        while True:
            # Select next customer greedily based on nearest neighbor
            candidates = [cust for cust in unvisited
                          if load + demands[cust] <= capacity]
            if not candidates:
                break
            # Find nearest candidate
            next_cust = min(candidates, key=lambda c: distance_matrix[current_node][c])
            route.append(next_cust)
            load += demands[next_cust]
            current_node = next_cust
            unvisited.remove(next_cust)
        routes.append(route)

    # Step 2: Improve routes with a local swap heuristic
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Try all pairs of customers between routes to see if swapping improves total distance
                for idx_i, cust_i in enumerate(route_i):
                    for idx_j, cust_j in enumerate(route_j):
                        # Check capacity constraints after swap
                        load_i = sum(demands[c] for c in route_i) - demands[cust_i] + demands[cust_j]
                        load_j = sum(demands[c] for c in route_j) - demands[cust_j] + demands[cust_i]
                        if load_i <= capacity and load_j <= capacity:
                            # Calculate current distances
                            def route_distance(route):
                                dist = distance_matrix[0][route[0]] + distance_matrix[route[-1]][0]
                                for k in range(len(route)-1):
                                    dist += distance_matrix[route[k]][route[k+1]]
                                return dist
                            # Current distances
                            current_dist = route_distance(route_i) + route_distance(route_j)
                            # Swap
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[idx_i] = cust_j
                            new_route_j[idx_j] = cust_i
                            new_dist = route_distance(new_route_i) + route_distance(new_route_j)
                            if new_dist < current_dist:
                                # Accept swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
    # Return routes without the depot
    return routes

