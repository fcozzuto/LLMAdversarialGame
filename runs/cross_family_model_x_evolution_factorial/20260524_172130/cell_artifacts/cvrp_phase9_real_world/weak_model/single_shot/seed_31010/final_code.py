def solve_cvrp(instance):
    # Extract data
    customers = instance['customers']
    depot = instance['depot']
    vehicle_capacity = instance['vehicle_capacity']
    n_customers = len(customers)
    
    # Initialize list of unvisited customers
    unvisited = set(range(n_customers))
    
    routes = []
    
    while unvisited:
        route_load = 0
        route = []
        current_location = depot
        while True:
            # Find the nearest unvisited customer that can be served
            candidates = []
            for cid in unvisited:
                customer = customers[cid]
                demand = customer['demand']
                if route_load + demand <= vehicle_capacity:
                    # Compute distance from current location
                    dist = distance(current_location, customer)
                    candidates.append((dist, cid))
            if not candidates:
                break  # No feasible next customer, end current route
            # Select the nearest candidate (deterministic)
            candidates.sort(key=lambda x: x[0])
            chosen_cid = candidates[0][1]
            chosen_customer = customers[chosen_cid]
            # Add to route
            route.append(chosen_cid)
            route_load += chosen_customer['demand']
            current_location = chosen_customer
            unvisited.remove(chosen_cid)
        routes.append(route)
    
    return routes

def distance(node_a, node_b):
    # Euclidean distance between node_a and node_b
    dx = node_a['x'] - node_b['x']
    dy = node_a['y'] - node_b['y']
    return (dx * dx + dy * dy) ** 0.5

