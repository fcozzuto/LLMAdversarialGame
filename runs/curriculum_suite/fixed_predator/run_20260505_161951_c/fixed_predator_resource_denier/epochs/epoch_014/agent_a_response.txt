def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # If no resources: maximize separation from opponent
    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            v = d * 1000 + (nx + ny)  # slight drift deterministically
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    # Choose a move that improves our advantage on the best resource
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # Evaluate the best resource for this hypothetical position
        local_best = -10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Positive if we are closer than opponent; also prefer closer absolute distance
            v = (od - sd) * 1000 - sd
            # If we can step onto a resource, prioritize heavily
            if nx == rx and ny == ry:
                v += 10**7
            # Slight tie-break by resource location to keep deterministic
            v += (rx * 0.01 + ry * 0.001)
            if v > local_best:
                local_best = v

        # Add a small component to prevent aimless wandering when tied
        sep = cheb(nx, ny, ox, oy)
        vtot = local_best + sep * 2
        if vtot > bestv or (vtot == bestv and (dx, dy) < (best[0], best[1])):
            bestv = vtot
            best = [dx, dy]
    return best