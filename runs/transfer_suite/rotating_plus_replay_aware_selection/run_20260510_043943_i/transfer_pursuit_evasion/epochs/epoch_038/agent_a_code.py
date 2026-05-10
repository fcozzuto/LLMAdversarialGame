def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        m = dx if dx >= dy else dy
        return m * m

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb2(nx, ny, ox, oy)
        center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        if is_evader:
            # Maximize distance from opponent; slight preference for escaping directions.
            tx = (w - 1) - nx if ox <= (w - 1) / 2.0 else nx
            ty = (h - 1) - ny if oy <= (h - 1) / 2.0 else ny
            escape_bias = tx * tx + ty * ty
            val = (d, escape_bias, -center)
        else:
            # Minimize distance to opponent; keep relatively central to avoid corners.
            val = (-d, -center, 0)
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    return [best[0], best[1]] if best is not None else [0, 0]