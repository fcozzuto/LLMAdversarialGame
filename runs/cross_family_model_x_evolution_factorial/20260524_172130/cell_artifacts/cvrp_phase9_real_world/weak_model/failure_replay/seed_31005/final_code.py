def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) for a given instance.
    Args:
        instance (dict): Contains 'depot', 'customers', 'vehicle_capacity'
            'depot': int
            'customers': list of dicts with keys 'id', 'x', 'y', 'demand'
            'vehicle_capacity': int
    Returns:
        routes (list of list): each sublist contains customer ids for that route (excluding depot)
    """

    # Extract instance data
    depot_id = instance['depot']
    customers = {c['id']: c for c in instance['customers']}
    capacity = instance['vehicle_capacity']

    # Initialize unvisited customers
    unvisited = set(customers.keys())

    # List to store final routes
    routes = []

    # Helper function: Euclidean distance
    def dist(a, b):
        dx = a['x'] - b['x']
        dy = a['y'] - b['y']
        return (dx*dx + dy*dy)**0.5

    # Helper: get customer data
    def get_customer(cid):
        return customers[cid]

    # Build initial routes using a greedy nearest neighbor heuristic
    while unvisited:
        route = []
        load = 0
        current_location = get_customer(depot_id)  # Start at depot
        route_customers = []

        while True:
            # Find feasible customers to visit next
            feasible_customers = []
            for cid in unvisited:
                cust = get_customer(cid)
                if load + cust['demand'] <= capacity:
                    feasible_customers.append((cid, dist(current_location, cust)))

            if not feasible_customers:
                break  # No more feasible customers on this route

            # Select the closest feasible customer
            feasible_customers.sort(key=lambda x: x[1])
            next_cid = feasible_customers[0][0]
            next_cust = get_customer(next_cid)

            # Add to route
            route.append(next_cid)
            load += next_cust['demand']
            current_location = next_cust
            unvisited.remove(next_cid)

        # Save route (excluding depot)
        routes.append(route)

    # Feasibility check
    def route_demand(r):
        return sum(customers[cid]['demand'] for cid in r)

    # Repair step: if any route exceeds capacity (unlikely with above logic), reassign
    # (In this heuristic, it's unlikely, but included for completeness)
    for idx, r in enumerate(routes):
        total_demand = route_demand(r)
        if total_demand > capacity:
            # Repair: redistribute customers in route
            customers_in_route = r[:]
            routes.pop(idx)
            # Reinsert customers one by one
            new_route = []
            load = 0
            for cid in customers_in_route:
                c_demand = customers[cid]['demand']
                if load + c_demand <= capacity:
                    new_route.append(cid)
                    load += c_demand
                else:
                    # start a new route
                    routes.append(new_route)
                    new_route = [cid]
                    load = c_demand
            if new_route:
                routes.append(new_route)

    # Local optimization: attempt to improve routes by swapping customers between routes
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for ci_idx in range(len(route_i)):
                    for cj_idx in range(len(route_j)):
                        # Swap customers
                        ci_id = route_i[ci_idx]
                        cj_id = route_j[cj_idx]
                        c_i_demand = customers[ci_id]['demand']
                        c_j_demand = customers[cj_id]['demand']

                        # Check capacity constraints after swap
                        demand_i = route_demand(route_i) - c_i_demand + c_j_demand
                        demand_j = route_demand(route_j) - c_j_demand + c_i_demand

                        if demand_i <= capacity and demand_j <= capacity:
                            # Perform swap
                            route_i[ci_idx], route_j[cj_idx] = cj_id, ci_id
                            improved = True
        # Cleanup empty routes if any
        routes = [r for r in routes if r]

    return routes

