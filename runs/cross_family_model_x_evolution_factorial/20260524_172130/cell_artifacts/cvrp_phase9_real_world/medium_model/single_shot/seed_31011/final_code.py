def solve_cvrp(instance):
    # instance expected as a dict with:
    # - 'distance_matrix': 2D list or similar square matrix
    # - 'demands': list of non-negative ints for customers 1..n
    # - 'vehicle_capacity': int
    # - 'depot': index of depot (commonly 0)
    #
    # We will implement a deterministic constructive solver:
    # - Start with all customers unassigned
    # - Build routes by greedily adding the nearest feasible customer to the current route
    # - After construction, perform a simple 2-opt style local repair on each route (swap adjacent customers)
    #
    # We treat customers as indices 0..n-1 for actual customers in the matrix, where depot is at depot_index.
    #
    # To meet the requirement "do not include the depot" in routes, routes contain only customer ids.
    #
    # Basic assumptions:
    # - The first element of demands is for customer 0; if depot is 0, adjust accordingly when indexing.
    # - If depot is not 0, we'll adapt by removing the depot from the customer lists used for demands/distance.
    #
    # Normalize input shape:
    dist = instance.get('distance_matrix')
    demands = instance.get('demands')
    capacity = instance.get('vehicle_capacity')
    depot = instance.get('depot', 0)
    n = len(demands)

    # Build a list of customer ids excluding depot
    customers = [i for i in range(n) if i != depot]

    # If depot appears in middle, ensure distances are accessible: we assume dist is full matrix including depot index
    unvisited = set(customers)
    routes = []

    # Precompute a simple neighbor suggestion: for a given sequence start, pick nearest feasible next
    # Helper to compute distance from a route's end to a candidate
    def dist_between(a, b):
        return dist[a][b]

    # Start constructing routes deterministically: always start with the nearest unvisited to depot
    while unvisited:
        # Start a new route with the nearest customer to depot
        # Compute nearest by distance from depot
        if depot is not None:
            start = min(unvisited, key=lambda c: dist[depot][c])
        else:
            start = min(unvisited, key=lambda c: dist[c][0] if dist and dist[0] else 0)
        route = [start]
        load = demands[start]

        unvisited.remove(start)

        # Greedily append nearest feasible customer
        while True:
            # candidates still unvisited
            candidates = list(unvisited)
            if not candidates:
                break
            # choose nearest to current last
            last = route[-1]
            candidates.sort(key=lambda c: dist[last][c])
            added = False
            for c in candidates:
                if load + demands[c] <= capacity:
                    route.append(c)
                    load += demands[c]
                    unvisited.remove(c)
                    added = True
                    break
            if not added:
                break

        routes.append(route)

    # Local repair: try to improve by 2-opt-like swap of adjacent customers within each route
    # Since we must keep feasibility, we'll swap adjacent customers if it doesn't violate capacity (it won't change load)
    # and reduces distance by reordering pairs (a simple local improvement)
    for r in range(len(routes)):
        route = routes[r]
        if len(route) <= 2:
            continue
        improved = True
        while improved:
            improved = False
            for i in range(len(route) - 1):
                # Try swapping route[i] and route[i+1]
                a, b = route[i], route[i+1]
                # If swapping reduces distance for the segment around i
                before = 0
                after = 0
                # distance from previous to a
                if i > 0:
                    before += dist[route[i-1]][a]
                    after += dist[route[i-1]][b]
                else:
                    before += dist[depot][a]
                    after += dist[depot][b]
                # distance from a to b and b to next
                if i+1 < len(route) - 1:
                    before += dist[a][b] + dist[b][route[i+2]]
                    after += dist[b][a] + dist[a][route[i+2]]
                else:
                    before += dist[a][b]
                    after += dist[b][a]
                if after < before:
                    route[i], route[i+1] = b, a
                    improved = True
            # end for
        routes[r] = route

    # Final check: ensure every customer exactly once
    seen = []
    for r in routes:
        seen.extend(r)
    # If any missing (due to some edge case), append them as individual routes
    missing = [c for c in customers if c not in seen]
    for m in missing:
        routes.append([m])

    return routes
