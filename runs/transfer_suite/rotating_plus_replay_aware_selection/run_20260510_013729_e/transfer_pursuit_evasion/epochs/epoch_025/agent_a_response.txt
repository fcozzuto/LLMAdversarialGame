def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in ob:
            cand.append((nx, ny, dx, dy))
    if not cand:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def mobility(x, y):
        m = 0
        for ddx, ddy in deltas:
            tx, ty = x + ddx, y + ddy
            if in_bounds(tx, ty) and (tx, ty) not in ob:
                m += 1
        return m

    # Pursuer: minimize distance; Evader: maximize distance.
    # Secondary: avoid dead-ends; tertiary: stay nearer center to reduce corner traps.
    best = None
    best_score = None
    for nx, ny, dx, dy in cand:
        d = dist(nx, ny, ox, oy)
        m = mobility(nx, ny)
        center = abs(nx - cx) + abs(ny - cy)
        if "evader" in role:
            score = (d, m, -center)  # maximize all in order
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            score = (-d, m, -center)  # maximize lexicographically on (-d)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]