def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for o in (observation.get("obstacles") or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

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
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - ds)  # positive => we arrive earlier
        # Prefer bigger advantage, then shorter our distance, then lexicographically
        key = (score, -ds, -ry, -rx)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    nx, ny = sx + dx, sy + dy
    if (dx != 0 or dy != 0) and 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [dx, dy]

    # Try axis moves deterministically if blocked or invalid
    candidates = [(dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 0)]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [mx, my]
    return [0, 0]