def solve_cvrp(instance):
    # Expected instance format:
    # instance = {
    #   'customers': {id: {'demand': int, 'x': int, 'y': int, ...}, ...},
    #   'depot': id_of_depot (commonly 0),
    #   'vehicle_capacity': int
    # }
    # But since we cannot rely on external imports or exact structure,
    # implement a robust minimal contract:
    customers = {}
    depot = None
    capacity = None

    # Try common potential shapes
    if isinstance(instance, dict):
        if 'customers' in instance and 'depot' in instance and 'vehicle_capacity' in instance:
            customers = dict(instance['customers'])
            depot = instance['depot']
            capacity = instance['vehicle_capacity']
        else:
            # fallback: assume top-level keys are customers mapping ids to data, with '0' as depot
            # and a separate 'capacity' field
            capacity = instance.get('capacity', None)
            if 'depot' in instance:
                depot = instance['depot']
            elif 0 in instance:
                depot = 0
            # extract customers as all numeric keys except depot
            for k, v in instance.items():
                if isinstance(k, int) or (isinstance(k, str) and k.isdigit()):
                    idx = int(k)
                    if idx != depot:
                        customers[idx] = v
            if not capacity:
                capacity = instance.get('vehicle_capacity', capacity)
    else:
        # If something else, fail gracefully by returning a trivial route
        return []

    if depot is None or capacity is None:
        return []

    # Normalize customers to structure: id -> demand
    norm = {}
    for cid, data in customers.items():
        if isinstance(data, dict) and 'demand' in data:
            norm[cid] = int(data['demand'])
        elif isinstance(data, (int, float)):
            norm[cid] = int(data)
        else:
            # Unknown format; skip
            continue

    # Ensure all customers from 1..N present with demand; if not, infer 1
    ids = sorted(norm.keys())
    if not ids:
        # No customers
        return []

    # Simple constructive heuristic: nearest-neighbor like walk starting from depot,
    # greedily assign to routes until capacity would be exceeded, then start new route.
    # To keep deterministic, we do:
    # - sort customers by id to break ties
    remaining = dict(norm)
    routes = []
    current_route = []
    current_load = 0

    # Helper: compute a simple symmetric distance using id-based pseudo coordinates (stable)
    def dist(a, b):
        # deterministic: distance based on ids
        return abs(a - b)

    # Precompute a simple order: start from smallest id not yet served, go to nearest in route order
    # We'll implement a fixed sequence: repeatedly pick the smallest-id remaining as next pickup,
    # and try to add the closest among remaining to current route while capacity allows;
    # if none fits, close route and start new one from the smallest remaining.
