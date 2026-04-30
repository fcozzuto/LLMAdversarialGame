def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)
    if not resources:
        return [0, 0]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obs_set:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources where we are closer than opponent; otherwise nearest.
        score_key = (ds - do, ds, rx, ry)
        if best is None or score_key < best_key:
            best = (rx, ry)
            best_key = score_key
    tx, ty = best

    # Deterministic move order: dx,dy in [-1,0,1]
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        dnew = dist((nx, ny), (tx, ty))
        # Also mildly prefer moves that reduce opponent's distance to our target (deny).
        do_new = dist((ox, oy), (tx, ty))
        # tie-break deterministically by position
        key = (dnew, -do_new, nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]