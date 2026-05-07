def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    # Pick a target resource we are relatively closer to than the opponent
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Lower is better: mainly prefer minimizing our distance, but also deny if opponent is closer
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Candidate step directions
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer reducing distance to target; deterministic tie-break by fixed dir order
    curr_best = None
    curr_dxdy = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        key = (d, abs(dx), abs(dy), dx, dy)
        if curr_best is None or key < curr_best:
            curr_best = key
            curr_dxdy = [dx, dy]
    return curr_dxdy