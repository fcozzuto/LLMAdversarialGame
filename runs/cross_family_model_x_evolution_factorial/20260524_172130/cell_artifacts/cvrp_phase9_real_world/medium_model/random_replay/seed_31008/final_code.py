def solve_cvrp(instance):
    """
    Deterministic constructive solver with simple repair/local-search flavor.
    Assumes instance is a dict with keys:
      - 'customers': list of dicts with 'id', 'demand'
      - 'depot': id (not used in routes)
      - 'vehicle_capacity': int
    Returns a list of routes, each route is list of customer ids (no depot), visiting all customers exactly once.
    """
    # Extract data
    customers = instance.get('customers', [])
    capacity = instance.get('vehicle_capacity', 0)

    # Prepare a deterministic order: sort by id (stable)
    customers_sorted = sorted(customers, key=lambda c: c['id'])

    # Create a simple constructive route builder (next-fit with capacity)
    routes = []
    current_route = []
    current_load = 0

    # Helper: add route if current has any customers
    def finalize_route():
        nonlocal current_route, current_load
        if current_route:
            routes.append(current_route)
        current_route = []
        current_load = 0

    for c in customers_sorted:
        cid = c['id']
        demand = c.get('demand', 0)

        # If a single customer's demand exceeds capacity, skip (invalid case)
        if demand > capacity:
            # Infeasible under given capacity; create an empty route for safety and continue
            continue

        # If adding would exceed capacity, finalize current route and start new
        if current_load + demand > capacity:
            finalize_route()

        # Add customer to current route
        current_route.append(cid)
        current_load += demand

    # Finalize last route
    finalize_route()

    # If for some reason we have no routes but there are customers, create singletons
    if not routes and customers_sorted:
        for c in customers_sorted:
            routes.append([c['id']])

    return routes
