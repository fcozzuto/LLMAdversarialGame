def solve_cvrp(instance):
    # instance is expected to have:
    # instance['customers']: list of customer dicts with 'id', 'demand'
    # instance['depot']: id of depot (assumed 0)
    # instance['capacity']: vehicle capacity
    
    customers = instance['customers']
    depot_id = instance['depot']
    capacity = instance['capacity']
    
    # Create a mapping from customer id to customer data
    customer_map = {c['id']: c for c in customers}
    
    # Set of all customer ids excluding depot
    unvisited = set(c['id'] for c in customers if c['id'] != depot_id)
    
    routes = []
    while unvisited:
        route = []
        load = 0
        # Start from depot
        current_node = depot_id
        # Build route greedily
        while True:
            # Collect feasible customers: unvisited and demand fitting in remaining capacity
            feasible_customers = [cid for cid in unvisited
                                  if customer_map[cid]['demand'] + load <= capacity]
            if not feasible_customers:
                break
            # Choose the customer with the smallest demand to keep the route compact
            next_cust = min(feasible_customers, key=lambda cid: customer_map[cid]['demand'])
            # Assign customer to route
            route.append(next_cust)
            load += customer_map[next_cust]['demand']
            unvisited.remove(next_cust)
            current_node = next_cust
        routes.append(route)
    return routes

