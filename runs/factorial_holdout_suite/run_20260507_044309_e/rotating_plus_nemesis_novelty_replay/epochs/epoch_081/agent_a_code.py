def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obs_raw = observation.get("obstacles") or []
    obstacles = obs_raw if isinstance(obs_raw, set) else set(tuple(p) for p in obs_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer being closer than opponent; also prefer immediate targets.
        key = (0 if ds == 0 else 1, ds, do - ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dsn = cheb(nx, ny, tx, ty)
        don = cheb(ox, oy, tx, ty)
        immediate = 0 if (nx, ny) == (tx, ty) else 1
        # Minimize self distance; prefer moves that keep opponent relatively farther.
        key = (immediate, dsn, -(don - dsn), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move