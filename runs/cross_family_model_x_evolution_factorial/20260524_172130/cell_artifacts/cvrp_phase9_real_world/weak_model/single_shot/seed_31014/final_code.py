def solve_cvrp(instance):
    """
    Solve a Capacitated Vehicle Routing Problem (CVRP) instance 
    using a deterministic, interpretable, constructive approach with local improvement.

    Args:
        instance: dict with keys:
            'depot': int, location id of depot
            'customers': list of dicts with keys:
                'id': int, customer id
                'demand': int, customer demand
                'x': float, x coordinate
                'y': float, y coordinate
            'vehicle_capacity': int, capacity of each vehicle

    Returns:
        routes: list of lists, each inner list contains customer ids in the route (excluding depot)
    """

    # Extract data
    depot_id = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    # Create dictionary for easy access
    customer_dict = {c['id']: c for c in customers}
    
    # Compute Euclidean distance between two nodes
    def distance(a_id, b_id):
        a = customer_dict[a_id]
        b = customer_dict[b_id]
        return ((a['x'] - b['x'])**2 + (a['y'] - b['y'])**2)**0.5
    
    # List of customer ids
    unserved = [c['id'] for c in customers]
    routes = []

    # Step 1: Initialization - create a route for each customer (farthest first)
    # to build initial feasible routes
    initial_routes = []
    for c_id in unserved:
        c_demand = customer_dict[c_id]['demand']
        # build route with single customer
        initial_routes.append([c_id])
    # Mark all as unassigned initially
    unassigned = set(unserved)
    
    # Step 2: Construct routes greedily by combining close customers
    # Initialize list for routes
    routes = []

    while unassigned:
        # Start a new route with the unassigned customer with the largest demand (heuristic)
        start_id = max(unassigned, key=lambda cid: customer_dict[cid]['demand'])
        route = [start_id]
        unassigned.remove(start_id)
        load = customer_dict[start_id]['demand']
        current_node = start_id
        # Expand route greedily by adding closest unassigned customer if capacity allows
        while unassigned:
            # Find the closest customer to current_node that fits capacity
            candidates = [
                cid for cid in unassigned 
                if customer_dict[cid]['demand'] + load <= capacity
            ]
            if not candidates:
                break
            # pick the closest
            next_cid = min(candidates, key=lambda cid: distance(current_node, cid))
            route.append(next_cid)
            load += customer_dict[next_cid]['demand']
            unassigned.remove(next_cid)
            current_node = next_cid
        routes.append(route)

    # Step 3: Local improvement - attempt to merge routes if possible
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # check if merging is feasible
                load_i = sum(customer_dict[c]['demand'] for c in route_i)
                load_j = sum(customer_dict[c]['demand'] for c in route_j)
                if load_i + load_j <= capacity:
                    # check if merge improves total distance (not necessary, but heuristic)
                    # For simplicity, attempt to merge by concatenation
                    new_route = route_i + route_j
                    # Calculate total distance before and after merge
                    def route_distance(route):
                        total = 0.0
                        prev = depot_id
                        for c in route:
                            total += distance(prev, c)
                            prev = c
                        total += distance(prev, depot_id)
                        return total
                    old_distance = route_distance(route_i) + route_distance(route_j)
                    new_distance = route_distance(new_route)
                    if new_distance <= old_distance:
                        # Merge routes
                        routes[i] = new_route
                        del routes[j]
                        improved = True
                        break
            if improved:
                break

    # Final step: Remove depot nodes from routes (they are not in routes but distances include depot)
    # Since we constructed routes without depot, just return the routes
    return routes

