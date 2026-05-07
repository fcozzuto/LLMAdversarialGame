def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    best = None
    best_key = None
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        if (rx, ry) in obst:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        dist_center = abs(rx - cx) + abs(ry - cy)
        key = (od - sd, -sd, -dist_center)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    rx, ry = best
    dx = rx - sx
    dy = ry - sy
    if dx > 1:
        dx = 1
    elif dx < -1:
        dx = -1
    if dy > 1:
        dy = 1
    elif dy < -1:
        dy = -1
    return [int(dx), int(dy)]