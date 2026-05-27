def solve_cvrp(instance):
    depot = instance["depot_index"]
    customers = set(instance["customer_ids"])
    demands = instance["demands"]
    capacity = instance["capacity"]
    matrix = instance["distance_matrix"]
    routes = []
    while customers:
        route = []
        load = 0
        current = depot
        while True:
            feasible = [node for node in customers if load + demands[node] <= capacity]
            if not feasible:
                break
            nxt = min(feasible, key=lambda node: (matrix[current][node], demands[node], node))
            route.append(nxt)
            customers.remove(nxt)
            load += demands[nxt]
            current = nxt
        routes.append(route)
    return routes

