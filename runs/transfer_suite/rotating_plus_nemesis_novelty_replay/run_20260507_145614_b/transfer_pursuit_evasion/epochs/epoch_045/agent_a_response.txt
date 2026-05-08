def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner_score = -10**18
    for cx, cy in corners:
        if inb(cx, cy):
            corner_score = max(corner_score, dist2(cx, cy, ox, oy) if evader else -dist2(cx, cy, ox, oy))

    def free_neighbors(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    best = None
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        s = (-d if not evader else d)
        s += 0.35 * free_neighbors(nx, ny)
        # Avoid moving into corners when acting as pursuer; cling to corners when evader.
        is_corner = (nx, ny) in corners
        s += (0.8 if (evader and is_corner) else 0.0) - (0.6 if ((not evader) and is_corner) else 0.0)
        # Gentle preference toward (or away from) the best-corner direction.
        if any((inb(cx, cy) and dist2(nx, ny, cx, cy) == 0) for cx, cy in corners):
            s += 0.0
        if best_sc is None or s > best_sc or (s == best_sc and (dx, dy) < best):
            best_sc = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]