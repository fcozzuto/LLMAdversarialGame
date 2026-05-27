def solve_cvrp(instance):
    # instance:
    # {
    #   'depot': depot_id,
    #   'customers': {
    #       customer_id: {
    #           'demand': int,
    #           'x': float,
    #           'y': float
    #       },
    #       ...
    #   },
    #   'vehicle_capacity': int
    # }

    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']

    # Convert customers dictionary to list of tuples for ordered access
    customer_list = list(customers.items())

    # Initialize set of unvisited customer IDs
    unvisited = set([c_id for c_id, c_data in customer_list])

    # Helper function to compute Euclidean distance
    def distance(c1, c2):
        dx = c1['x'] - c2['x']
        dy = c1['y'] - c2['y']
        return (dx*dx + dy*dy)**0.5

    # Build a mapping of customer_id to (x, y, demand)
    customer_coords = {c_id: (c_data['x'], c_data['y'], c_data['demand']) for c_id, c_data in customer_list}

    # Routes to return, each route is a list of customer IDs (excluding depot)
    routes = []

    # While there are unvisited customers, build a route
    while unvisited:
        route = []
        load = 0
        current_node_id = depot

        while True:
            # Select the nearest unvisited customer that can be served within capacity
            candidates = []
            for c_id in unvisited:
                c_x, c_y, c_demand = customer_coords[c_id]
                # Check capacity
                if load + c_demand <= capacity:
                    # Distance from current_node to candidate
                    if current_node_id == depot:
                        curr_x, curr_y = customer_coords[depot][:2]
                    else:
                        curr_x, curr_y = customer_coords[current_node_id][:2]
                    dist = ((curr_x - c_x)**2 + (curr_y - c_y)**2)**0.5
                    candidates.append((dist, c_id))
            if not candidates:
                # No feasible candidate found, end route
                break

            # Select candidate with minimal distance (deterministic feature)
            candidates.sort(key=lambda x: x[0])
            selected_c_id = candidates[0][1]
            # Assign customer to route
            route.append(selected_c_id)
            load += customer_coords[selected_c_id][2]
            unvisited.remove(selected_c_id)
            current_node_id = selected_c_id

        # Append route (excluding depot, which is not included per specification)
        routes.append(route)

    return routes

