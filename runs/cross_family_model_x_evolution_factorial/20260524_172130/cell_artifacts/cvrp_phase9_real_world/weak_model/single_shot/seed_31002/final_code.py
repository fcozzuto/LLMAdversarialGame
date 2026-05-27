def solve_cvrp(instance):
    # instance: dict with keys:
    # 'depot': int,
    # 'customers': dict {id: {'demand': int, 'x': float, 'y': float}},
    # 'vehicle_capacity': int
    
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create list of customer ids
    customer_ids = list(customers.keys())
    # Exclude depot if present as a customer (likely not)
    # The depot is not included in routes directly.
    
    # Compute Euclidean distance between two customers
    def distance(cust1_id, cust2_id):
        c1 = customers[cust1_id]
        c2 = customers[cust2_id]
        dx = c1['x'] - c2['x']
        dy = c1['y'] - c2['y']
        return (dx*dx + dy*dy)**0.5
    
    # Build a sorted list of customers based on distance to depot (nearest first)
    customer_distances = []
    for cid in customer_ids:
        dist = distance(cid, depot)
        customer_distances.append((dist, cid))
    customer_distances.sort()
    ordered_customers = [cid for _, cid in customer_distances]
    
    routes = []
    while ordered_customers:
        current_capacity = 0
        current_route = []
        remaining_customers = []
        for cid in ordered_customers:
            demand = customers[cid]['demand']
            if current_capacity + demand <= capacity:
                current_route.append(cid)
                current_capacity += demand
            else:
                remaining_customers.append(cid)
        routes.append(current_route)
        ordered_customers = remaining_customers
    
    return routes

