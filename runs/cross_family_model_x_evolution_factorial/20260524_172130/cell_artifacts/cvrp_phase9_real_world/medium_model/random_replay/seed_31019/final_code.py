def solve_cvrp(instance):
    # instance: dict-like with keys:
    # - 'customers': list of dicts with 'id', 'demand'
    # - 'vehicles': int, capacity
    # - 'depot': id (not included in routes)
    # We assume customer list covers all customers to serve exactly once.
    customers = []
    for c in instance.get('customers', []):
        customers.append({'id': c['id'], 'demand': c['demand']})
    depot_id = instance.get('depot', None)
    capacity = instance.get('vehicles', 0)
    # If capacity is zero or no customers, return empty routes
    if not customers:
        return []
    if capacity <= 0:
        return [[c['id'] for c in customers]]
    # Deterministic constructive heuristic with simple规则:
    # - sort customers by nondecreasing demand (small first) for stable grouping
    # - assign to current route if capacity allows; otherwise close route and start new
    sorted_customers = sorted(customers, key=lambda x: x['demand'])
    routes = []
    current_route = []
    current_load = 0
    for c in sorted_customers:
        d = c['demand']
        if d > capacity:
            # Individual customer exceeds capacity: place in its own route (edge case)
            if current_route:
                routes.append(current_route)
                current_route = []
                current_load = 0
            routes.append([c['id']])
            continue
        if current_load + d <= capacity:
            current_route.append(c['id'])
            current_load += d
        else:
            # close current route and start new
            if current_route:
                routes.append(current_route)
            current_route = [c['id']]
            current_load = d
    if current_route:
        routes.append(current_route)
    # Ensure no route includes depot and all customers appear exactly once
    # The above uses ids from customers; ensure uniqueness by construction
    return routes
