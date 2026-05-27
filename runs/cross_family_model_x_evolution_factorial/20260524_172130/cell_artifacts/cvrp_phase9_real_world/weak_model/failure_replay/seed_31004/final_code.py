def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) using a deterministic, interpretable approach.

    Args:
        instance (dict): A dictionary containing:
            - 'depot': the depot node id
            - 'nodes': a list of customer nodes, each with 'id', 'demand', 'x', 'y'
            - 'vehicle_capacity': capacity of each vehicle

    Returns:
        routes (list of list): a list of routes, each route is a list of customer ids
    """

    # Extract data
    depot = instance['depot']
    nodes = {node['id']: node for node in instance['nodes']}
    capacity = instance['vehicle_capacity']

    # Initialize:
    # - List of unassigned customers
    unassigned = set(nodes.keys())

    # - Precompute distances
    def distance(a, b):
        ax, ay = nodes[a]['x'], nodes[a]['y']
        bx, by = nodes[b]['x'], nodes[b]['y']
        return ((ax - bx)**2 + (ay - by)**2)**0.5

    all_nodes = list(nodes.keys())

    # Identify customer nodes (excluding depot)
    customers = [nid for nid in nodes if nid != depot]

    # Build functions to find the closest customer
    def find_closest(current, candidates):
        min_dist = float('inf')
        closest_node = None
        for c in candidates:
            dist = distance(current, c)
            if dist < min_dist:
                min_dist = dist
                closest_node = c
        return closest_node

    routes = []

    # Main constructive phase: build each route
    while unassigned:
        current_route = []
        current_load = 0
        current_node = depot
        # Initialize candidate set
        candidates = list(unassigned)

        # Greedily build route
        while candidates:
            # Find the closest candidate to current node
            next_node = find_closest(current_node, candidates)
            demand = nodes[next_node]['demand']
            # Check capacity constraint
            if current_load + demand <= capacity:
                # Assign customer
                current_route.append(next_node)
                current_load += demand
                # Update current node
                current_node = next_node
                # Remove from unassigned
                unassigned.remove(next_node)
                # Update candidates
                candidates = list(unassigned)
            else:
                # Cannot add more customers to current route
                break
        routes.append(current_route)

    # Repair phase: try to merge routes if possible
    # For simplicity, attempt to merge pairs of routes
    def total_demand(route):
        return sum(nodes[n]['demand'] for n in route)

    merged = True
    while merged:
        merged = False
        new_routes = []
        used = set()
        for i in range(len(routes)):
            if i in used:
                continue
            route_i = routes[i]
            merged_in_this_round = False
            for j in range(i+1, len(routes)):
                if j in used:
                    continue
                route_j = routes[j]
                # Check if merge feasible
                if total_demand(route_i) + total_demand(route_j) <= capacity:
                    # For interpretability, attempt to merge by concatenation
                    candidate_route = route_i + route_j
                    # Optional: check route feasibility with heuristic (e.g., sequential order)
                    # For simplicity, assume concatenation is feasible if capacity constraints hold
                    new_routes.append(candidate_route)
                    used.add(i)
                    used.add(j)
                    merged_in_this_round = True
                    merged = True
                    break
            if i not in used:
                new_routes.append(route_i)
        routes = new_routes

    # Local optimization: Try 2-opt swaps within each route to improve total distance
    def route_distance(route):
        total = 0.0
        prev = depot
        for node in route:
            total += distance(prev, node)
            prev = node
        # Return to depot to compute complete route distance if needed
        # But the output only needs routes, so skipping depot return
        return total

    def two_opt(route):
        improved = True
        best_route = route
        best_distance = route_distance(route)
        while improved:
            improved = False
            for i in range(1, len(route) - 1):
                for j in range(i + 1, len(route)):
                    new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
                    new_distance = route_distance(new_route)
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
                        route = new_route
                        break
                if improved:
                    break
        return best_route

    # Apply local improvement
    final_routes = []
    for r in routes:
        optimized = two_opt(r)
        final_routes.append(optimized)

    return final_routes

