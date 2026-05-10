def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    role = (observation.get("self_role") or "").lower()
    want_evade = ("evad" in role) or ("run" in role) or ("escape" in role)

    def obstacle_pen(x, y):
        if not obs_set:
            return 0
        best = 10**9
        for (px, py) in obs_set:
            d = cheb(x, y, px, py)
            if d < best:
                best = d
        if best == 10**9:
            return 0
        return 0 if best > 1 else 3  # discourage moving adjacent/into tight areas

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        dist = cheb(nx, ny, ox, oy)
        pen = obstacle_pen(nx, ny)
        val = dist - pen if want_evade else -dist - pen
        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            if want_evade:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)
            else:
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)

    if best_val is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]