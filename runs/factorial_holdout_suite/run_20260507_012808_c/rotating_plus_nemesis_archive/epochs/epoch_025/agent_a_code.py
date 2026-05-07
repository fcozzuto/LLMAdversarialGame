def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        best = None
        best_key = None
        for rx, ry in res:
            my = cheb(sx, sy, rx, ry)
            op = cheb(ox, oy, rx, ry)
            key = (op - my, -my, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = pick_target()
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        my2 = cheb(nx, ny, tx, ty)
        op2 = cheb(ox, oy, tx, ty)
        my_curr = cheb(sx, sy, tx, ty)
        moved_towards = 1 if my2 < my_curr else 0
        key = (moved_towards, -(my2), (op2 - my2), -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move