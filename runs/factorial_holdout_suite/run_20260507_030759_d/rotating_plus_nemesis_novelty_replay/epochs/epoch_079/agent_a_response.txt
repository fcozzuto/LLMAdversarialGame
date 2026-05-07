def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
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
        win_margin = do - ds  # >0 means we can arrive no later than opponent
        # Prefer immediate collection; break ties toward corners opposite opponent
        dist_score = -ds
        corner_pref = (rx + ry) if (ox > (w - 1) / 2.0) else ((w - 1 - rx) + (h - 1 - ry))
        key = (win_margin, dist_score, corner_pref, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    if sx == rx and sy == ry:
        return [0, 0]

    dx = 0
    if rx > sx:
        dx = 1
    elif rx < sx:
        dx = -1
    dy = 0
    if ry > sy:
        dy = 1
    elif ry < sy:
        dy = -1

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # fallback: try axis-aligned step deterministically
        if rx != sx:
            dx2 = 1 if rx > sx else -1
            nx2, ny2 = sx + dx2, sy
            if 0 <= nx2 < w and (nx2, ny2) not in obstacles:
                return [dx2, 0]
        if ry != sy:
            dy2 = 1 if ry > sy else -1
            nx2, ny2 = sx, sy + dy2
            if 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                return [0, dy2]
        return [0, 0]

    return [dx, dy]