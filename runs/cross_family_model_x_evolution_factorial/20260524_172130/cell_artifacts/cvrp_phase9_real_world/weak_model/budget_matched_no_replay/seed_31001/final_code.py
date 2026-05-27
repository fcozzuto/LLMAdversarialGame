def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) for the given instance.
    Args:
        instance (dict): A dictionary with keys:
            - 'customer_coords': list of (x, y) tuples for customers (index 1..N)
            - 'demands': list of demands for each customer (index 0..N-1)
            - 'vehicle_capacity': capacity of each vehicle
    Returns:
        list of routes, each route is a list of customer IDs (integers)
    """
    # Extract data
    customer_coords = instance['customer_coords']
    demands = instance['demands']
    capacity = instance['vehicle_capacity']
    num_customers = len(demands)

    # For simplicity, assume depot is at index 0, but customer ids are 1..N
    # Customers are from 1..N
    customer_ids = list(range(1, num_customers + 1))
    
    # Initialize set of unvisited customers
    unvisited = set(customer_ids)
    
    # Prepare a helper to compute Euclidean distance
    def distance(a, b):
        xa, ya = customer_coords[a - 1]
        xb, yb = customer_coords[b - 1]
        return ((xa - xb)**2 + (ya - yb)**2)**0.5
    
    # Build a distance matrix for efficiency
    dist_matrix = {}
    for i in range(1, num_customers + 1):
        for j in range(1, num_customers + 1):
            dist_matrix[(i, j)] = distance(i, j)
    
    # Initialize list of routes
    routes = []
    
    # Construct initial routes by selecting closest customers greedily
    while unvisited:
        route = []
        load = 0
        # Start from depot (implicit)
        current_node = 0  # depot assumed at index 0, not explicit in routes
        route_customers = []
        
        # Select the next customer greedily based on minimum distance that fits capacity
        while True:
            candidates = []
            for customer in unvisited:
                req = demands[customer - 1]
                if load + req <= capacity:
                    dist_to_customer = dist_matrix.get((current_node if current_node !=0 else 1), customer)
                    candidates.append((dist_to_customer, customer))
            if not candidates:
                break
            # Choose the closest candidate
            candidates.sort(key=lambda x: x[0])
            next_customer = candidates[0][1]
            # Add to route
            route_customers.append(next_customer)
            load += demands[next_customer - 1]
            unvisited.remove(next_customer)
            current_node = next_customer
        routes.append(route_customers)
    
    # Improve routes with local swap to reduce total distance
    def total_distance(routes):
        total = 0
        for route in routes:
            prev = 0  # start from depot
            for customer in route:
                total += dist_matrix[(prev if prev !=0 else 1), customer]
                prev = customer
            total += dist_matrix.get((prev, 0), 0)  # return to depot
        return total
    
    def improve_routes(routes):
        improved = True
        while improved:
            improved = False
            for i in range(len(routes)):
                for j in range(i+1, len(routes)):
                    route_a = routes[i]
                    route_b = routes[j]
                    for idx_a in range(len(route_a)):
                        for idx_b in range(len(route_b)):
                            # Swap customers if capacity constraints are maintained
                            cust_a = route_a[idx_a]
                            cust_b = route_b[idx_b]
                            # Check capacity constraints after swap
                            load_a = sum(demands[c-1] for c in route_a) - demands[cust_a - 1] + demands[cust_b - 1]
                            load_b = sum(demands[c-1] for c in route_b) - demands[cust_b - 1] + demands[cust_a - 1]
                            if load_a <= capacity and load_b <= capacity:
                                # Create new routes with swapped customers
                                new_route_a = route_a[:]
                                new_route_b = route_b[:]
                                new_route_a[idx_a] = cust_b
                                new_route_b[idx_b] = cust_a
                                new_routes = routes[:]
                                new_routes[i] = new_route_a
                                new_routes[j] = new_route_b
                                old_total = total_distance(routes)
                                new_total = total_distance(new_routes)
                                if new_total < old_total:
                                    routes = new_routes
                                    improved = True
        return routes
    
    # Apply local improvement
    routes = improve_routes(routes)
    
    return routes

