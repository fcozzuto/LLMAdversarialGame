def solve_cvrp(instance):
    # instance expected to have:
    # - instance['customers']: list of customer dicts with keys: 'id', 'demand', 'x', 'y'
    # - instance['depot']: dict with keys: 'id', 'x', 'y'
    # - instance['vehicle_capacity']: int
    
    customers = instance['customers']
    depot = instance['depot']
    capacity = instance['vehicle_capacity']
    
    # Initialize list of unserved customers
    unserved = customers[:]
    routes = []
    
    while unserved:
        route = []
        load = 0
        current_point = depot
        # Keep selecting customers until capacity is reached or no customers left
        while True:
            # Filter feasible customers
            feasible_customers = [c for c in unserved if c['demand'] + load <= capacity]
            if not feasible_customers:
                break
            # Select the closest feasible customer
            next_customer = min(feasible_customers, key=lambda c: distance(current_point, c))
            # Add to route
            route.append(next_customer['id'])
            load += next_customer['demand']
            current_point = next_customer
            # Remove from unserved
            unserved = [c for c in unserved if c['id'] != next_customer['id']]
        routes.append(route)
    return routes

def distance(p1, p2):
    return ((p1['x'] - p2['x']) ** 2 + (p1['y'] - p2['y']) ** 2) ** 0.5

