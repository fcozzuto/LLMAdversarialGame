def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer than opponent
            # Prefer guaranteed/strong advantages; then pick farthest opponent distance to avoid contention; deterministic tiebreak
            key = (adv, -od, -sd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1]

    tx, ty = pick_target()
    if sx == tx and sy == ty:
        return [0, 0]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy)))
    # deterministic: minimize distance to target; if tie, maximize opponent distance; if still tie, deterministic on dx,dy
    best = None
    for dx, dy, d_to_t, d_to_o in candidates:
        key = (d_to_t, -d_to_o, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]