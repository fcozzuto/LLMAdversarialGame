def solve_cvrp(instance):
    # instance expected to have:
    # - 'nodes': list of dicts with 'id', 'x', 'y', 'demand'
    # - 'vehicle_capacity': int
    # For simplicity, assume depot has id 0.

    nodes = instance['nodes']
    depot = next(node for node in nodes if node['id'] == 0)
    customers = [node for node in nodes if node['id'] != 0]
    capacity = instance['vehicle_capacity']

    # Step 1: Build distance matrix for simplicity
    # Since no import, use Euclidean distance
    def dist(a, b):
        return ((a['x'] - b['x'])**2 + (a['y'] - b['y'])**2)**0.5

    # Precompute distances
    distance = {}
    for n1 in nodes:
        for n2 in nodes:
            distance[(n1['id'], n2['id'])] = dist(n1, n2)

    # Step 2: Construct initial routes using a greedy heuristic
    # List of unvisited customers
    unvisited = {c['id']: c for c in customers}
    routes = []

    while unvisited:
        current_load = 0
        route = []
        current_node_id = depot['id']
        while True:
            # Find the nearest unvisited customer that fits
            candidates = [
                c for c in unvisited.values()
                if c['demand'] <= (capacity - current_load)
            ]
            if not candidates:
                break
            # Select candidate with minimum distance from current_node
            next_customer = min(candidates,
                                key=lambda c: distance[(current_node_id, c['id'])])
            # Add to route
            route.append(next_customer['id'])
            current_load += next_customer['demand']
            current_node_id = next_customer['id']
            # Mark as visited
            del unvisited[next_customer['id']]
        routes.append(route)

    # Step 3: Improve routes with local exchanges: try to swap customers between routes
    # Attempt a single pass of swaps that reduce total distance
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                # Check swaps of customers between route i and route j
                for idx_i in range(len(route_i)):
                    for idx_j in range(len(route_j)):
                        c_i_id = route_i[idx_i]
                        c_j_id = route_j[idx_j]
                        # Get customer demands
                        c_i = next(c for c in nodes if c['id'] == c_i_id)
                        c_j = next(c for c in nodes if c['id'] == c_j_id)
                        # Check capacity constraints if swapped
                        load_i = sum(next(c for c in nodes if c['id'] == cid)['demand'] for cid in route_i)
                        load_j = sum(next(c for c in nodes if c['id'] == cid)['demand'] for cid in route_j)
                        # After swap, check if feasible
                        new_load_i = load_i - c_i['demand'] + c_j['demand']
                        new_load_j = load_j - c_j['demand'] + c_i['demand']
                        if new_load_i <= capacity and new_load_j <= capacity:
                            # Compute current distances
                            def route_distance(route):
                                total = 0
                                prev_id = depot['id']
                                for cid in route:
                                    total += distance[(prev_id, cid)]
                                    prev_id = cid
                                total += distance[(prev_id, depot['id'])]
                                return total
                            old_dist = route_distance(route_i) + route_distance(route_j)
                            # Swap customers
                            route_i[idx_i], route_j[idx_j] = route_j[idx_j], route_i[idx_i]
                            new_dist = route_distance(route_i) + route_distance(route_j)
                            if new_dist < old_dist:
                                improved = True
                            else:
                                # revert swap
                                route_i[idx_i], route_j[idx_j] = route_j[idx_j], route_i[idx_i]

    # Final step: Remove depot from routes to return just customer ids
    # Routes already exclude depot as per construction
    return routes

