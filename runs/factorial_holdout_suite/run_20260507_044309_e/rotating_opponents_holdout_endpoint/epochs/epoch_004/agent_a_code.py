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
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer getting there earlier (smaller ds-do), then closer ds, then deterministic coord.
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curr_ds = cheb(sx, sy, tx, ty)
    curr_do = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Maximize relative improvement: (curr_do - curr_ds) -> (ndo - nds).
        rel_before = curr_do - curr_ds
        rel_after = ndo - nds
        rel_gain = rel_after - rel_before
        # Prefer reducing our distance, then deterministic.
        key = (-rel_gain, nds, nx, ny, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]