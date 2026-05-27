def solve_cvrp(instance):
    # instance is expected to have:
    # instance['depot']: index of depot (int)
    # instance['customers']: list of customer dicts with keys: 'id', 'x', 'y', 'demand'
    # instance['vehicle_capacity']: capacity of each vehicle
    
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Helper function to compute Euclidean distance
    def distance(cust1, cust2):
        dx = cust1['x'] - cust2['x']
        dy = cust1['y'] - cust2['y']
        return (dx*dx + dy*dy)**0.5
    
    # Prepare customer list excluding depot
    customer_list = [c for c in customers if c['id'] != depot]
    
    # Keep track of assigned customers
    unassigned = {c['id']: c for c in customer_list}
    
    routes = []
    
    # Build initial routes using a greedy, nearest neighbor heuristic
    while unassigned:
        route = []
        load = 0
        current_node = {'id': depot}  # start from depot
        # For simplicity, pick starting customer as the nearest to depot
        start_cust = min(unassigned.values(), key=lambda c: distance({'x':0,'y':0}, c))
        route.append(start_cust['id'])
        load += start_cust['demand']
        del unassigned[start_cust['id']]
        current_node = start_cust
        # Expand route greedily
        while True:
            # Find nearest unassigned customer that fits in capacity
            candidates = [c for c in unassigned.values() if c['demand'] + load <= capacity]
            if not candidates:
                break
            next_customer = min(candidates, key=lambda c: distance(current_node, c))
            route.append(next_customer['id'])
            load += next_customer['demand']
            current_node = next_customer
            del unassigned[next_customer['id']]
        routes.append(route)
    
    # Improvement: try to merge routes if possible
    def can_merge(r1, r2):
        total_demand = sum(next(c['demand'] for c in customers if c['id']==cid) for cid in r1 + r2)
        return total_demand <= capacity
    
    merged = True
    while merged:
        merged = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                if can_merge(routes[i], routes[j]):
                    # Merge routes
                    routes[i] = routes[i] + routes[j]
                    del routes[j]
                    merged = True
                    break
            if merged:
                break
    
    # Repair: fix any capacity violations (should not occur with above, but double check)
    def repair_routes(routes):
        repaired_routes = []
        for route in routes:
            load = sum(next(c['demand'] for c in customers if c['id']==cid) for cid in route)
            if load <= capacity:
                repaired_routes.append(route)
            else:
                # Rebuild the route greedily
                unassigned_customers = [next(c for c in customers if c['id'] == cid) for cid in route]
                new_routes = []
                while unassigned_customers:
                    new_route = []
                    load_local = 0
                    for c in unassigned_customers[:]:
                        if c['demand'] + load_local <= capacity:
                            new_route.append(c['id'])
                            load_local += c['demand']
                            unassigned_customers.remove(c)
                    new_routes.append(new_route)
                repaired_routes.extend(new_routes)
        return repaired_routes
    
    routes = repair_routes(routes)
    
    # Local improvement: swap customers between routes if it improves total distance
    def total_distance(routes):
        total = 0
        for route in routes:
            prev = {'id': depot}
            for cid in route:
                c_obj = next(c for c in customers if c['id'] == cid)
                total += distance(prev, c_obj)
                prev = c_obj
            total += distance(prev, {'x':0,'y':0})  # back to depot
        return total
    
    # Implement a simple swap heuristic
    improved = True
    while improved:
        improved = False
        for i in range(len(routes)):
            for j in range(i+1, len(routes)):
                for idx_i in range(len(routes[i])):
                    for idx_j in range(len(routes[j])):
                        c1_id = routes[i][idx_i]
                        c2_id = routes[j][idx_j]
                        c1_obj = next(c for c in customers if c['id'] == c1_id)
                        c2_obj = next(c for c in customers if c['id'] == c2_id)
                        # Calculate new load after swap
                        def route_load(route):
                            return sum(next(c['demand'] for c in customers if c['id'] == cid) for cid in route)
                        load_i = route_load(routes[i]) - c1_obj['demand'] + c2_obj['demand']
                        load_j = route_load(routes[j]) - c2_obj['demand'] + c1_obj['demand']
                        if load_i <= capacity and load_j <= capacity:
                            # Perform swap
                            new_route_i = routes[i][:]
                            new_route_j = routes[j][:]
                            new_route_i[idx_i], new_route_j[idx_j] = new_route_j[idx_j], new_route_i[idx_i]
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

