def solve_cvrp(instance):
    # Extract data from the instance
    depot = instance['depot']
    customers = instance['customers']
    vehicle_capacity = instance['vehicle_capacity']
    n_customers = len(customers)

    # Prepare customer list with their attributes
    customer_list = []
    for c in customers:
        customer_list.append({
            'id': c['id'],
            'demand': c['demand'],
            'x': c['x'],
            'y': c['y']
        })
    
    # Initialize: unvisited customers set
    unvisited = set(c['id'] for c in customer_list)

    routes = []

    # Helper to get customer data by id
    def get_customer(c_id):
        for c in customer_list:
            if c['id'] == c_id:
                return c
        return None

    # Function to compute Euclidean distance
    def distance(c1, c2):
        return ((c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2)**0.5

    # Build routes until all customers are assigned
    while unvisited:
        route = []
        load = 0
        current_location = depot
        # For deterministic behavior, sort unvisited by customer id
        remaining = sorted(unvisited)
        # Select the next customer based on nearest neighbor heuristic
        while remaining:
            # Find the nearest customer to current location
            nearest_c_id = None
            min_dist = float('inf')
            for c_id in remaining:
                c = get_customer(c_id)
                dist = distance(current_location, c)
                if dist < min_dist:
                    min_dist = dist
                    nearest_c_id = c_id
            c = get_customer(nearest_c_id)
            # Check capacity constraint
            if load + c['demand'] <= vehicle_capacity:
                # Assign customer to route
                route.append(c['id'])
                load += c['demand']
                current_location = c
                unvisited.remove(c['id'])
                remaining.remove(c['id'])
            else:
                # Capacity exceeded, finish current route
                break
        routes.append(route)

    # Attempt to improve solution via a simple local search:
    # For each pair of routes, try to swap customers if it improves total routes
    # Basic improvement: exchange customers between routes if it reduces total distance and respects capacity
    # This step is kept simple and deterministic

    # Create a helper for route total distance
    def route_distance(route):
        total = 0.0
        prev_loc = depot
        for c_id in route:
            c = get_customer(c_id)
            total += distance(prev_loc, c)
            prev_loc = c
        total += distance(prev_loc, depot)
        return total

    improved = True
    while improved:
        improved = False
        # Iterate over pairs of routes
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Try all customer pairs between route_i and route_j
                for idx_i in range(len(route_i)):
                    for idx_j in range(len(route_j)):
                        c_id_i = route_i[idx_i]
                        c_id_j = route_j[idx_j]
                        c_i = get_customer(c_id_i)
                        c_j = get_customer(c_id_j)
                        # Check capacity constraints after swap
                        load_i = sum(get_customer(cid)['demand'] for cid in route_i) - c_i['demand'] + c_j['demand']
                        load_j = sum(get_customer(cid)['demand'] for cid in route_j) - c_j['demand'] + c_i['demand']
                        if load_i <= vehicle_capacity and load_j <= vehicle_capacity:
                            # Compute new distances if swap occurred
                            new_route_i = route_i[:]
                            new_route_j = route_j[:]
                            new_route_i[idx_i] = c_j['id']
                            new_route_j[idx_j] = c_i['id']
                            dist_i = route_distance(new_route_i)
                            dist_j = route_distance(new_route_j)
                            old_dist_i = route_distance(route_i)
                            old_dist_j = route_distance(route_j)
                            # Accept swap if total distance reduces
                            if dist_i + dist_j < old_dist_i + old_dist_j:
                                # Perform swap
                                routes[i] = new_route_i
                                routes[j] = new_route_j
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes

