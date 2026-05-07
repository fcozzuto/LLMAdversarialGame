def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    curr_ds = cheb(sx, sy, tx, ty)
    best_step = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Prefer improving relative arrival first, then shortest our distance, then deterministic position
        score = (nds - ndo, nds, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_step = [dx, dy]

    if best_score is None:
        return [0, 0]
    return best_step