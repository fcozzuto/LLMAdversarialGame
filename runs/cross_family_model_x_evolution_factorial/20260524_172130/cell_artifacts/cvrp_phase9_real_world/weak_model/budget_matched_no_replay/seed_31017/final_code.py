def solve_cvrp(instance):
    # Unpack instance data
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    # Extract customer IDs and their demands
    customer_ids = [c['id'] for c in customers]
    demands = {c['id']: c['demand'] for c in customers}
    
    # Initialize unvisited customers set
    unvisited = set(customer_ids)
    routes = []

    while unvisited:
        current_load = 0
        route = []
        current_location = depot
        # Greedily build a route until no more customers can be added
        while True:
            # Select the next customer deterministically: smallest ID among feasible customers
            feasible_customers = [cid for cid in unvisited if demands[cid] + current_load <= vehicle_capacity]
            if not feasible_customers:
                break
            # Pick the customer with the smallest ID to ensure determinism
            next_cust = min(feasible_customers)
            # Add customer to route
            route.append(next_cust)
            current_load += demands[next_cust]
            unvisited.remove(next_cust)
        routes.append(route)
    return routes

