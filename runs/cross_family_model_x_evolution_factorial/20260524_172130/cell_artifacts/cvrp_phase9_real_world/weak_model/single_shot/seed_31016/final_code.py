def solve_cvrp(instance):
    # Extract data
    customers = instance['customers']
    depot = instance['depot']
    vehicle_capacity = instance['vehicle_capacity']
    num_customers = len(customers)

    # Initialize unvisited customers
    unvisited = set(range(1, num_customers + 1))
    
    routes = []

    while unvisited:
        # Start a new route from depot
        current_route = []
        current_load = 0
        current_node = 0  # start from depot (assumed to be index 0 in data)
        
        while True:
            # Find feasible customers to visit next
            candidates = []
            for cust_id in unvisited:
                cust = customers[cust_id]
                demand = cust['demand']
                if demand + current_load <= vehicle_capacity:
                    # Calculate distance from current node to candidate
                    dist = _distance(customers[current_node], cust)
                    candidates.append((dist, cust_id))
            
            if not candidates:
                # No feasible candidates, end route
                break
            
            # Select the nearest customer
            candidates.sort(key=lambda x: x[0])
            _, selected_cust_id = candidates[0]
            
            # Add selected customer to route
            current_route.append(selected_cust_id)
            current_load += customers[selected_cust_id]['demand']
            unvisited.remove(selected_cust_id)
            current_node = selected_cust_id
        
        routes.append(current_route)
    return routes

def _distance(node_a, node_b):
    # Euclidean distance
    dx = node_a['x'] - node_b['x']
    dy = node_a['y'] - node_b['y']
    return (dx * dx + dy * dy) ** 0.5

