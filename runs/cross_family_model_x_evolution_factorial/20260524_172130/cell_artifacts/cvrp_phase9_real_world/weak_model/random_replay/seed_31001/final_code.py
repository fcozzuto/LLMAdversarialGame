def solve_cvrp(instance):
    # instance is a dict with keys:
    # 'depot': integer id of depot,
    # 'customers': list of dicts {'id': int, 'x': float, 'y': float, 'demand': int},
    # 'vehicle_capacity': int
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    
    # Create a sorted list of customers by demand (large to small) for heuristic start
    unvisited = sorted(customers, key=lambda c: c['demand'], reverse=True)
    
    routes = []
    while unvisited:
        route = []
        load = 0
        current_node = depot
        remaining_customers = unvisited[:]
        for customer in remaining_customers:
            if load + customer['demand'] <= vehicle_capacity:
                route.append(customer['id'])
                load += customer['demand']
                unvisited.remove(customer)
        routes.append(route)
    return routes

