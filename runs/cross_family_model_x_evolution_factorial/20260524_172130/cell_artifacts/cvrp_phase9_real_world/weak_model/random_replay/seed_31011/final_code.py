def solve_cvrp(instance):
    """
    Solve a Capacitated Vehicle Routing Problem (CVRP) instance using a deterministic,
    interpretable heuristic approach with constructive, repair, and local improvement steps.

    Args:
        instance: A dict with keys:
            - 'depot': int, customer id representing the depot (usually 0)
            - 'customers': dict {customer_id: {'x': float, 'y': float, 'demand': float}}
            - 'capacity': float, vehicle capacity

    Returns:
        routes: list of routes, each route is a list of customer ids (excluding depot)
    """
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['capacity']
    customer_ids = list(customers.keys())

    # Step 1: Initialize by sorting customers by their demand ascending for a more balanced initial assignment
    customers_sorted = sorted(customer_ids, key=lambda cid: customers[cid]['demand'])

    # Initialize list of routes (each route is a list of customer ids)
    routes = []

    # Keep track of unassigned customers
    unassigned = set(customers_sorted)

    # Step 2: Construct routes greedily by capacity
    while unassigned:
        route = []
        load = 0.0
        # Build a route by adding customers with demands that fit
        # in a deterministic order: pick the customer with smallest demand that fits
        assigned_in_this_route = set()
        customers_by_demand = sorted(unassigned, key=lambda cid: customers[cid]['demand'])
        for cid in customers_by_demand:
            demand = customers[cid]['demand']
            if load + demand <= capacity:
                route.append(cid)
                load += demand
                assigned_in_this_route.add(cid)
        # Remove assigned customers from unassigned set
        unassigned -= assigned_in_this_route
        routes.append(route)

    # Step 3: Local improvement: attempt to swap customers between routes to reduce total distance
    # We'll do a single pass of pairwise swaps for simplicity
    def total_distance(routes):
        # Sum of route distances, considering depots start and end at depot (assumed)
        distance = 0.0
        for route in routes:
            prev_node = depot
            for cid in route:
                distance += euclidean_distance(customers[cid], customers[prev_node]) if prev_node != depot else euclidean_distance(customers[cid], customers[depot])
                prev_node = cid
            # Return to depot
            distance += euclidean_distance(customers[prev_node], customers[depot])
        return distance

    def euclidean_distance(c1, c2):
        dx = c1['x'] - c2['x']
        dy = c1['y'] - c2['y']
        return (dx*dx + dy*dy)**0.5

    # Perform a simple local improvement: try swapping customers between routes if it reduces total distance
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for ci in range(len(route_i)):
                    for cj in range(len(route_j)):
                        c1, c2 = route_i[ci], route_j[cj]
                        demand_c1 = customers[c1]['demand']
                        demand_c2 = customers[c2]['demand']
                        # Check capacity constraints after swap
                        load_i = sum(customers[c]['demand'] for c in route_i)
                        load_j = sum(customers[c]['demand'] for c in route_j)
                        load_i_new = load_i - demand_c1 + demand_c2
                        load_j_new = load_j - demand_c2 + demand_c1
                        if load_i_new <= capacity and load_j_new <= capacity:
                            # Calculate current total distance
                            current_dist = route_distance(route_i, customers, depot) + route_distance(route_j, customers, depot)
                            # Swap customers
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[ci], new_route_j[cj] = c2, c1
                            new_dist = route_distance(new_route_i, customers, depot) + route_distance(new_route_j, customers, depot)
                            if new_dist < current_dist:
                                # Accept swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
    return routes

def route_distance(route, customers, depot):
    total = 0.0
    prev_node = depot
    for cid in route:
        total += ((customers[cid]['x'] - customers[prev_node]['x'])**2 + (customers[cid]['y'] - customers[prev_node]['y'])**2)**0.5
        prev_node = cid
    # Return to depot
    total += ((customers[prev_node]['x'] - customers[depot]['x'])**2 + (customers[prev_node]['y'] - customers[depot]['y'])**2)**0.5
    return total

