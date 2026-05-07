def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res or (sx, sy) in obst:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer targets we can reach earlier; if tied, prefer closer; then prefer resources deeper toward opponent side.
        ahead = od - sd  # higher is better
        depth = (tx + ty)  # deterministic secondary
        key = (-(ahead), sd, -depth, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
        return [dx, dy]

    # If diagonal/greedy blocked, try axis moves deterministically.
    candidates = [(dx, 0), (0, dy), (dx, dy), (-1 if dx > 0 else (1 if dx < 0 else 0), 0), (0, -1 if dy > 0 else (1 if dy < 0 else 0)), (0, 0)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if cdx in (-1, 0, 1) and cdy in (-1, 0, 1) and 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [cdx, cdy]
    return [0, 0]