def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If opponent is already on same row, prefer targets where we reduce their linear advantage.
        extra = 0
        if ry == oy:
            extra = (abs(ox - rx) - abs(sx - rx))  # positive means opponent line is worse
        # Key: maximize advantage, then be closer for tie-break.
        key = (do - ds, extra, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    cur_best = None
    cur_best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us; avoid obstacle move for consistency
        dnext = cheb(nx, ny, tx, ty)
        dn_opp = cheb(ox, oy, tx, ty)
        # Prefer moves that maintain/improve advantage and reduce distance to target.
        key = (dn_opp - dnext, -dnext, -abs(nx - tx), -abs(ny - ty), dx, dy)
        if cur_best_key is None or key > cur_best_key:
            cur_best_key = key
            cur_best = (dx, dy)

    return [int(cur_best[0]), int(cur_best[1])]