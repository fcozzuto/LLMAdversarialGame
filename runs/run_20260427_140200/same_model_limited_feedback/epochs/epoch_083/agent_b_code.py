def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    # Choose a resource we can contest (prefer where we are closer than opponent).
    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer positive advantage; then smaller self distance; then deterministic coordinate order.
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        # No resources: move to maximize distance from opponent.
        target = (0, 0)
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            nd = cheb(nx, ny, ox, oy)
            key = (-nd, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                target = (nx, ny)
        return [target[0] - sx, target[1] - sy]

    rx, ry = best_res

    # Evaluate candidate moves.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Score: prefer reducing our distance to contested resource, and being at least as competitive.
        score = (self_d - opp_d, self_d, -cheb(nx, ny, ox, oy), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]