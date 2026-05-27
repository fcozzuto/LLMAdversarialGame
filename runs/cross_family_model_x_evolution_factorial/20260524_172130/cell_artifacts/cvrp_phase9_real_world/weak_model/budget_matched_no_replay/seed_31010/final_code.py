def solve_cvrp(instance):
    # Instance is expected to be a dictionary with keys:
    # 'depot': int, the depot id
    # 'customers': list of dicts with 'id', 'demand', 'x', 'y'
    # 'vehicle_capacity': int
    
    depot_id = instance['depot']
    customers = instance['customers']
    capacity = instance['vehicle_capacity']
    
    # Create a list of customers (excluding depot)
    customer_list = customers
    
    # Helper: get customer by id
    customer_dict = {c['id']: c for c in customers}
    
    # Initialize unvisited customers set
    unvisited = set(c['id'] for c in customers)
    
    # Initialize final routes list
    routes = []
    
    # Function to compute Euclidean distance
    def dist(c1, c2):
        return ((c1['x'] - c2['x'])**2 + (c1['y'] - c2['y'])**2)**0.5
    
    # Build a list of customer objects for quick access
    customer_objs = {c['id']: c for c in customers}
    
    # Main construction loop: build routes until all customers are assigned
    while unvisited:
        route = []
        load = 0
        current_node_id = depot_id
        current_node = {'id': depot_id, 'x':0, 'y':0}  # placeholder, will set later
        # For the initial position, set to depot coordinates
        # Find depot coordinates
        depot = None
        for c in customers:
            if c['id'] == depot_id:
                depot = c
                break
        current_node = depot
        remaining_capacity = capacity
        # Greedy insertion: pick the closest unvisited customer that fits
        while True:
            # Find feasible customers
            feasible_customers = []
            for cid in unvisited:
                c = customer_dict[cid]
                if c['demand'] <= remaining_capacity:
                    feasible_customers.append(c)
            if not feasible_customers:
                break
            # Select the closest feasible customer to current_node
            next_customer = min(feasible_customers, key=lambda c: dist(current_node, c))
            # Add to route
            route.append(next_customer['id'])
            unvisited.remove(next_customer['id'])
            remaining_capacity -= next_customer['demand']
            current_node = next_customer
        # Save route
        routes.append(route)
    return routes

