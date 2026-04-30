def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick best resource: minimize (our distance - 0.9*opponent distance), tie-break by coordinates
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = ds - 0.9 * do
        key = (score, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = (best[1][0], best[1][1]) if best else (ox, oy)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0,0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        if ny < 0: ny = 0
        if nx >= w: nx = w - 1
        if ny >= h: ny = h - 1
        if (nx, ny) in obstacles:
            continue
        # Prefer moving toward target; slight preference to keep distance from opponent
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # also slightly prefer avoiding being closer than opponent to the target
        do_next = cheb(ox, oy, tx, ty)
        val = (d_to, -0.15 * d_opp, 0.01 * (nx + ny), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]