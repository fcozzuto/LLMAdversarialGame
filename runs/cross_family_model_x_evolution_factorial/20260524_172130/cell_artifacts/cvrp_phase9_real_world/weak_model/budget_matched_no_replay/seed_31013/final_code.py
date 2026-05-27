def solve_cvrp(instance):
    n_customers = len(instance['demands'])
    capacity = instance['vehicle_capacity']
    demands = instance['demands']
    locations = instance['locations']

    dist = [[0.0 for _ in range(n_customers)] for _ in range(n_customers)]
    for i in range(n_customers):
        for j in range(n_customers):
            xi, yi = locations[i]
            xj, yj = locations[j]
            dist[i][j] = ((xi - xj) ** 2 + (yi - yj) ** 2) ** 0.5

    unserved = set(range(n_customers))
    routes = []

    while unserved:
        current_route = []
        load = 0
        current_node = None
        while True:
            candidates = []
            for c in unserved:
                if load + demands[c] <= capacity:
                    prev = -1 if current_node is None else current_node
                    candidates.append((dist[prev][c], c))
            if not candidates:
                break
            candidates.sort(key=lambda x: x[0])
            next_customer = candidates[0][1]
            current_route.append(next_customer)
            load += demands[next_customer]
            unserved.remove(next_customer)
            current_node = next_customer
        routes.append(current_route)

    def route_distance(route):
        total = 0
        prev = -1
        for c in route:
            total += dist[prev][c]
            prev = c
        return total

    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route_i = routes[i]
                route_j = routes[j]
                for index_i in range(len(route_i)):
                    for index_j in range(len(route_j)):
                        c_i = route_i[index_i]
                        c_j = route_j[index_j]
                        load_i = sum(demands[c] for c in route_i) - demands[c_i] + demands[c_j]
                        load_j = sum(demands[c] for c in route_j) - demands[c_j] + demands[c_i]
                        if load_i <= capacity and load_j <= capacity:
                            old_distance = route_distance(route_i) + route_distance(route_j)

                            route_i_new = route_i[:]
                            route_j_new = route_j[:]
                            route_i_new[index_i], route_j_new[index_j] = c_j, c_i
                            new_distance = route_distance(route_i_new) + route_distance(route_j_new)

                            if new_distance < old_distance:
                                routes[i] = route_i_new
                                routes[j] = route_j_new
                                improved = True
                                break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes
