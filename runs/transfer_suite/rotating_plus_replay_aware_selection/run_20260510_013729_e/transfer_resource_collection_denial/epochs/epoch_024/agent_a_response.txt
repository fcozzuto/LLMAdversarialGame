def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    if not resources:
        return [0, 0]

    obs = {(x, y) for x, y in obstacles}

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -(ds), -(rx * 8 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if (sx, sy) == (tx, ty):
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    ordered = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        avoid_penalty = 0
        # Prefer not to step adjacent to many obstacles (soft walling)
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ax, ay = nx + adx, ny + ady
            if in_bounds(ax, ay) and (ax, ay) in obs:
                avoid_penalty += 1
        key = (-(abs(ns - 0)), -ns, -avoid_penalty, -no, -(nx * 8 + ny))
        ordered.append((key, (dx, dy)))

    if not ordered:
        return [0, 0]

    ordered.sort(key=lambda t: t[0], reverse=True)
    return [int(ordered[0][1][0]), int(ordered[0][1][1])]