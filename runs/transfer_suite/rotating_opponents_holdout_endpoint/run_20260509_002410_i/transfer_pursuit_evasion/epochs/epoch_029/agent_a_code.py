def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    sr = (observation.get("self_role") or "").lower()
    orr = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in sr) or ("purs" in orr and "evad" not in sr)
    self_is_evader = ("evad" in sr) or ("evad" in orr and "purs" not in sr)
    if not (self_is_pursuer or self_is_evader):
        self_is_pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_dxdy = (0, 0)
    best_score = None

    curd = man(sx, sy, ox, oy)
    target_corner = (0, 0) if (sx + sy) <= (w - 1 - sx + h - 1 - sy) else (w - 1, h - 1)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist = man(nx, ny, ox, oy)
        if self_is_pursuer:
            # primary: minimize distance; secondary: break ties by favoring movement toward nearest corner
            corner_bias = man(nx, ny, target_corner[0], target_corner[1])
            score = (dist, corner_bias, abs(dx) + abs(dy), nx * 9 + ny)
            better = best_score is None or score < best_score
        else:
            # primary: maximize distance; secondary: flee toward farther corner deterministically
            corner_flee = man(nx, ny, target_corner[0], target_corner[1])
            score = (-dist, -corner_flee, abs(dx) + abs(dy), nx * 9 + ny)
            better = best_score is None or score < best_score
        if better:
            best_score = score
            best_dxdy = (dx, dy)

    if best_dxdy == (0, 0):
        # deterministic fallback toward/away from opponent (one-step)
        dx = 0
        if ox > sx: dx = 1
        elif ox < sx: dx = -1
        dy = 0
        if oy > sy: dy = 1
        elif oy < sy: dy = -1
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            return [int(dx), int(dy)]
    return [int(best_dxdy[0]), int(best_dxdy[1])]