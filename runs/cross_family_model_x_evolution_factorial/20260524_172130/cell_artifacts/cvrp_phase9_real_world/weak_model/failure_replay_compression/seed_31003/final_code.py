def solve_cvrp(instance):
    # instance expected to be a dictionary with:
    # 'nodes': list of nodes where each node is a dict with 'id', 'x', 'y', 'demand'
    # 'vehicle_capacity': maximum load per vehicle
    # 'depot_id': id of the depot node

    nodes = instance['nodes']
    vehicle_capacity = instance['vehicle_capacity']
    depot_id = instance['depot_id']

    # Create a mapping from node id to node data
    node_map = {node['id']: node for node in nodes}
    depot = node_map[depot_id]

    # List of customer nodes (excluding the depot)
    customers = [node for node in nodes if node['id'] != depot_id]

    # Helper function to compute Euclidean distance
    def dist(a, b):
        return ((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2) ** 0.5

    # Initialization: sort customers by distance to depot (greedy start)
    unvisited = set(c['id'] for c in customers)
    routes = []

    while unvisited:
        route = []
        load = 0
        current_node = depot

        while True:
            # Find feasible customers for current route
            feasible_customers = []
            for cid in unvisited:
                customer = node_map[cid]
                if load + customer['demand'] <= vehicle_capacity:
                    feasible_customers.append(customer)
            if not feasible_customers:
                break
            # Choose the nearest neighbor
            next_customer = min(feasible_customers, key=lambda c: dist(current_node, c))
            # Append to route
            route.append(next_customer['id'])
            # Update load and current position
            load += next_customer['demand']
            current_node = next_customer
            # Mark visited
            unvisited.remove(next_customer['id'])

        routes.append(route)

    # Construct initial routes with depot at start and end
    # Following the above logic, routes are built from depot (implicit at start/end)
    # but our output should only contain customer ids in each route
    # So, routes are already in correct format

    # Improve solution with simple local swaps (inter-route node swaps)
    improved = True
    def total_distance(routes):
        total = 0
        for route in routes:
            prev_node = depot
            for cid in route:
                total += dist(prev_node, node_map[cid])
                prev_node = node_map[cid]
            total += dist(prev_node, depot)
        return total

    # Simple local search: attempt to swap customers between routes to reduce total distance
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                for idx_i in range(len(routes[i])):
                    for idx_j in range(len(routes[j])):
                        c_i = node_map[routes[i][idx_i]]
                        c_j = node_map[routes[j][idx_j]]

                        # Check capacity constraints after swap
                        load_i = sum(node_map[c]['demand'] for c in routes[i]) - c_i['demand'] + c_j['demand']
                        load_j = sum(node_map[c]['demand'] for c in routes[j]) - c_j['demand'] + c_i['demand']
                        if load_i <= vehicle_capacity and load_j <= vehicle_capacity:
                            # Calculate new distances after swap
                            new_route_i = routes[i][:]
                            new_route_j = routes[j][:]
                            new_route_i[idx_i] = c_j['id']
                            new_route_j[idx_j] = c_i['id']
                            new_routes = routes[:]
                            new_routes[i] = new_route_i
                            new_routes[j] = new_route_j
                            if total_distance(new_routes) < total_distance(routes):
                                routes = new_routes
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes

