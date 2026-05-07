def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick best resource: prioritize making us earlier than opponent; then closer to us.
    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, rx, ry)  # higher key preferred
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance; if tied, prefer making opponent relatively later;
        # also lightly prefer moving toward region with resources by maximizing sum distances.
        score_key = (-(ndo - nds), -nds, nx, ny)
        if best_mkey is None or score_key > best_mkey:
            best_mkey = score_key
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]