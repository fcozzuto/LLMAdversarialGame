def choose_move(observation):
    def ti(v, d=0):
        try:
            return int(v)
        except:
            return d

    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = ti(sx), ti(sy), ti(ox), ti(oy)
    w = ti(observation.get("grid_width", 8), 8) or 8
    h = ti(observation.get("grid_height", 8), 8) or 8

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
            if inb(x, y):
                obs_set.add((x, y))

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
            if inb(x, y) and (x, y) not in obs_set:
                targets.append((x, y))
    if not targets:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def best_step_to(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs_set:
            return dx, dy
        # Deterministic fallback: try orthogonal first, then still
        cand = []
        if dx != 0:
            cand.append((dx, 0))
        if dy != 0:
            cand.append((0, dy))
        cand.append((0, 0))
        for cdx, cdy in cand:
            nx, ny = sx + cdx, sy + cdy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                return cdx, cdy
        return 0, 0

    best = None
    best_key = None
    for tx, ty in targets:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer stealing chances; if none, minimize self distance.
        key = (od - sd, -sd, -cheb(tx, ty, ox, oy))
        if best is None or key > best_key:
            best, best_key = (tx, ty), key

    tx, ty = best
    dx, dy = best_step_to(tx, ty)
    return [dx, dy]