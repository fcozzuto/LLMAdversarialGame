def solve_cvrp(instance):
    """
    Solves a Capacitated Vehicle Routing Problem (CVRP) instance using a deterministic, interpretable approach.
    Assumes 'instance' is a dictionary with keys:
        'depot': depot id
        'customers': list of customer dicts, each with 'id', 'x', 'y', 'demand'
        'capacity': vehicle capacity
    """

    # Extract data
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['capacity']

    # Create a dict for quick lookup
    customer_dict = {c['id']: c for c in customers}

    # All customer IDs
    unserved = set(c['id'] for c in customers)

    # Prepare routes list
    routes = []

    # Helper functions
    def distance(a_id, b_id):
        a = customer_dict[a_id] if a_id != depot else {'x':0,'y':0}
        b = customer_dict[b_id] if b_id != depot else {'x':0,'y':0}
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        return (dx*dx + dy*dy)**0.5

    def find_closest_customer(current_node, candidates, remaining_capacity):
        # Select the closest customer from candidates that fits in remaining_capacity
        min_dist = None
        selected = None
        for c_id in candidates:
            demand = customer_dict[c_id]['demand']
            if demand <= remaining_capacity:
                dist = distance(current_node, c_id)
                if (min_dist is None) or (dist < min_dist):
                    min_dist = dist
                    selected = c_id
        return selected

    # Build routes greedily
    while unserved:
        route = []
        load = 0
        current_node = depot  # Start at depot

        # Continue adding customers to route
        while True:
            remaining_capacity = capacity - load
            # Find the nearest unserved customer that fits
            next_customer = find_closest_customer(current_node, unserved, remaining_capacity)
            if next_customer is None:
                # No fitting customer found
                break
            # Add customer to route
            route.append(next_customer)
            load += customer_dict[next_customer]['demand']
            unserved.remove(next_customer)
            current_node = next_customer

        routes.append(route)

    return routes

