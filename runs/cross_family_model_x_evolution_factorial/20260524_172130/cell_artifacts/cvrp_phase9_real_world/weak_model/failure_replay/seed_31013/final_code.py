def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) deterministically.

    Parameters:
        instance: dict with keys:
            - 'depot': int (depot node id)
            - 'customers': list of customer ids
            - 'demands': dict {customer_id: demand}
            - 'distances': dict {(node_a, node_b): distance}
            - 'vehicle_capacity': int

    Returns:
        routes: list of routes, each route is a list of customer ids
    """

    depot = instance['depot']
    customers = instance['customers']
    demands = instance['demands']
    distances = instance['distances']
    capacity = instance['vehicle_capacity']

    unvisited = set(customers)
    routes = []

    # For deterministic behavior, precompute a sorted list of customers
    sorted_customers = sorted(customers, key=lambda c: c)

    while unvisited:
        route = []
        load = 0
        current_node = depot

        while True:
            # Filter feasible customers: unvisited and demand can fit in remaining capacity
            feasible_customers = [
                c for c in unvisited
                if demands[c] + load <= capacity
            ]

            if not feasible_customers:
                # No more feasible customers to add, finish current route
                break

            # Select next customer: nearest neighbor among feasible
            next_customer = min(
                feasible_customers,
                key=lambda c: distances[(current_node, c)]
            )

            # Add selected customer to route
            route.append(next_customer)
            load += demands[next_customer]
            unvisited.remove(next_customer)
            current_node = next_customer

        routes.append(route)

    # Repair step: if some customers are unvisited due to capacity constraints,
    # try to reassign them by splitting routes if necessary
    # For simplicity, this implementation assumes demands allow all customers
    # to be served in the initial greedy construction.

    # Optional: local improvement by swapping customers between routes if capacity allows
    # For simplicity, this is omitted here for interpretability.

    return routes

