def solve_cvrp(instance):
    """
    Solve a Capacitated Vehicle Routing Problem (CVRP) instance deterministically.
    
    Args:
        instance (dict): A dictionary with keys:
            - 'depot': id of the depot node
            - 'customers': list of customer node ids
            - 'demands': dict mapping node id to demand
            - 'distance': dict of dicts with_route distances between nodes
    
    Returns:
        routes (list): List of routes, each route is a list of customer ids.
    """
    depot = instance['depot']
    customers = instance['customers']
    demands = instance['demands']
    distance = instance['distance']
    vehicle_capacity = max(demands.values())  # assume max demand as capacity, or set explicitly
    
    # For simplicity, assume vehicle capacity is known and set
    # Here, we set capacity as sum of demands divided by number of vehicles (heuristic)
    total_demand = sum(demands[cust] for cust in customers)
    # Estimate number of vehicles needed
    num_vehicles = max(1, int(total_demand / 100) + 1)  # heuristic: 100 demand per vehicle
    vehicle_capacity = total_demand / num_vehicles
    
    # Keep track of unvisited customers
    unvisited = set(customers)
    
    routes = []
    
    # Build routes iteratively
    while unvisited:
        route = []
        load = 0
        current_node = depot
        # Continue adding customers until capacity or no customers left
        while True:
            # Find feasible customers: unvisited and fitting in capacity
            feasible_customers = [
                c for c in unvisited
                if load + demands[c] <= vehicle_capacity
            ]
            if not feasible_customers:
                break
            # Select the nearest feasible customer
            next_customer = min(
                feasible_customers,
                key=lambda c: distance[current_node][c]
            )
            # Append customer to route
            route.append(next_customer)
            load += demands[next_customer]
            unvisited.remove(next_customer)
            current_node = next_customer
        routes.append(route)
    
    return routes

