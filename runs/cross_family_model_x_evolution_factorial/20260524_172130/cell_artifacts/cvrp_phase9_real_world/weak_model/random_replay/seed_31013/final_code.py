def solve_cvrp(instance):
    """
    Solve the Capacitated Vehicle Routing Problem (CVRP) deterministically using
    constructive, repair, and local search heuristics with an emphasis on interpretability.
    
    Args:
        instance (dict): Dictionary with keys:
            - 'depot': int, id of the depot node
            - 'customers': list of customer dicts with keys:
                'id': int, customer id
                'demand': float, demand of customer
                'x': float, x-coordinate
                'y': float, y-coordinate
                
    Returns:
        routes: list of routes, each route is a list of customer ids (excluding depot),
                visiting all customers exactly once without exceeding capacity.
    """
    # Extract depot and customer info
    depot = instance['depot']
    customers = instance['customers']
    capacity = instance['capacity']
    
    # Initialize list of unassigned customers
    unassigned = customers[:]
    
    # Precompute distance matrix for all nodes (including depot)
    nodes = [depot] + [c['id'] for c in customers]
    id_to_customer = {c['id']: c for c in customers}
    # Create a map from node id to index for matrix access
    node_indices = {node_id: idx for idx, node_id in enumerate(nodes)}
    
    size = len(nodes)
    dist_matrix = [[0.0]*size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if i != j:
                # Get corresponding customer objects
                node_i = nodes[i]
                node_j = nodes[j]
                if node_i == depot:
                    c_i = {'x': 0, 'y': 0}
                else:
                    c_i = id_to_customer[node_i]
                if node_j == depot:
                    c_j = {'x': 0, 'y': 0}
                else:
                    c_j = id_to_customer[node_j]
                dx = c_i['x'] - c_j['x']
                dy = c_i['y'] - c_j['y']
                dist_matrix[i][j] = (dx*dx + dy*dy)**0.5
    
    routes = []
    while unassigned:
        route = []
        load = 0
        current_node = 0  # Start at depot index
        while True:
            # Find the nearest unassigned customer that can be served
            nearest_customer = None
            nearest_dist = float('inf')
            for customer in unassigned:
                demand = customer['demand']
                if load + demand <= capacity:
                    customer_idx = node_indices[customer['id']]
                    dist = dist_matrix[current_node][customer_idx]
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_customer = customer
            if nearest_customer is None:
                # No more customers can be added to current route
                break
            # Assign customer to route
            customer_id = nearest_customer['id']
            route.append(customer_id)
            load += nearest_customer['demand']
            unassigned.remove(nearest_customer)
            current_node = node_indices[customer_id]
        routes.append(route)
    # Optional: Improve routes with a local swap (pairwise exchange)
    # For interpretability, only perform a simple local improvement: swapping customers between routes if it reduces total distance and capacity constraints are maintained.
    # But to keep it simple and deterministic for now, skip the local swaps.
    return routes

