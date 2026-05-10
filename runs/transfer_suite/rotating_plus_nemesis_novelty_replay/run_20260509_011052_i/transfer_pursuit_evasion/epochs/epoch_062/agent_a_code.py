def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources") or []
    if resources:
        best = None
        bestv = None
        for r in resources:
            rx, ry = r if isinstance(r, (list, tuple)) and len(r) >= 2 else (None, None)
            if rx is None:
                continue
            d_op = cheb(rx, ry, ox, oy)
            d_me = cheb(rx, ry, sx, sy)
            score = -d_me + (d_op if not pursuer else -d_op)
            if best is None or score > bestv:
                bestv = score
                best = (int(rx), int(ry))
        tx, ty = best if best else (sx, sy)
    else:
        tx, ty = (ox, oy) if pursuer else (0 if ox < w / 2 else w - 1, 0 if oy < h / 2 else h - 1)

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        val = (-d_to + (d_op if not pursuer else -d_op))
        if best_val is None or val > best_val or (val == best_val and (dx == 0 and dy == 0)):
            best_val = val
            best_move = [dx, dy]
    return best_move if isinstance(best_move, list) else [0, 0]