def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs_set = set((x, y) for x, y in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def clamp_step(x, y):
        if x < 0 or x >= w or y < 0 or y >= h:
            return (sx, sy)
        if (x, y) in obs_set:
            return (sx, sy)
        return (x, y)
    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx >= dy else dy
    # pick target resource that is most "ours" relative to opponent
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, rx, ry)  # maximize advantage, then closer
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    # if no resources, drift to a corner away from opponent
    if best is None:
        tx, ty = (0, 0) if cheb(sx, sy, 0, 0) > cheb(ox, oy, 0, 0) else (w - 1, h - 1)
    else:
        tx, ty = best

    # choose step that minimizes distance to target while staying safe
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = clamp_step(sx + dx, sy + dy)
        # safety/penalty if would effectively not move
        if (nx, ny) == (sx, sy) and (dx, dy) != (0, 0):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        # anti-commute: prefer moves that also increase opponent distance to same target
        opp_d = cheb(ox, oy, tx, ty)
        opp_future = cheb(ox, oy, tx, ty)  # opponent move unknown; keep mild
        # mild repulsion from opponent to avoid easy race losses
        rep = cheb(nx, ny, ox, oy)
        score = (-d_to_target, rep, -abs((nx + ny) - (tx + ty)), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]