def solve_cvrp(instance):
    # instance: dict with keys:
    # 'demand': list of demands per customer (index 0 is depot with demand=0)
    # 'capacity': vehicle capacity
    # 'distance': 2D list or matrix of distances between nodes (including depot)
    demands = instance['demand']
    capacity = instance['capacity']
    distance = instance['distance']
    n_customers = len(demands) - 1  # excluding depot
    customers = list(range(1, n_customers + 1))
    
    # Initialize all customers unassigned
    unassigned = set(customers)
    
    routes = []
    
    # Build Feasible Routes with a greedy heuristic: Nearest Neighbor until capacity filled
    while unassigned:
        route = []
        remaining_capacity = capacity
        current_node = 0  # Start from depot
        while True:
            # Find the closest unassigned customer that fits in remaining capacity
            candidates = []
            for customer in unassigned:
                if demands[customer] <= remaining_capacity:
                    candidates.append(customer)
            if not candidates:
                break
            # Select the closest customer among candidates
            next_customer = min(candidates, key=lambda c: distance[current_node][c])
            # Append to route
            route.append(next_customer)
            unassigned.remove(next_customer)
            remaining_capacity -= demands[next_customer]
            current_node = next_customer
        routes.append(route)
    
    # Improvement Phase: Try to reassign customers to reduce routes or improve costs
    # Using a simple one-pass local improvement: reassignment of customers to better routes
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for customer in list(routes[i]):
                # Attempt to move customer to a different route if beneficial
                current_route = routes[i]
                current_route_demand = sum(demands[cust] for cust in current_route)
                for j in range(len(routes)):
                    if i == j:
                        continue
                    route_j = routes[j]
                    route_j_demand = sum(demands[cust] for cust in route_j)
                    if demands[customer] + route_j_demand <= capacity:
                        # Compute cost difference before and after move
                        # Current costs
                        def route_cost(route):
                            cost = 0
                            prev = 0
                            for c in route:
                                cost += distance[prev][c]
                                prev = c
                            cost += distance[prev][0]
                            return cost
                        cost_before = route_cost(current_route) + route_cost(route_j)
                        # New routes after move
                        new_route_i = [c for c in current_route if c != customer]
                        new_route_j = route_j + [customer]
                        cost_after = route_cost(new_route_i) + route_cost(new_route_j)
                        if cost_after < cost_before:
                            # Perform move
                            current_route.remove(customer)
                            route_j.append(customer)
                            if len(current_route) == 0:
                                routes.pop(i)
                                # Adjust indices if needed
                                if i < j:
                                    j -= 1
                            improved = True
                            break
                if improved:
                    break
            if improved:
                break
    
    # Final route formatting: exclude depot in output
    return routes

