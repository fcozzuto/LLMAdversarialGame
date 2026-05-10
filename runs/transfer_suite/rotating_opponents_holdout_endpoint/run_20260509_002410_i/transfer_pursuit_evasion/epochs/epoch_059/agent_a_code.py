def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = "evader" in role or "run" in role

    resources = observation.get("resources") or []
    res_pts = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res_pts.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    def score_for(x, y):
        dx = x - ox
        dy = y - oy
        d2 = dx * dx + dy * dy
        best_res = 0
        if res_pts:
            md2 = None
            for rx, ry in res_pts:
                tx = x - rx
                ty = y - ry
                v = tx * tx + ty * ty
                if md2 is None or v < md2:
                    md2 = v
            best_res = 0 if md2 is None else (1.0 / (1.0 + md2))
        # Evader wants distance and safety; pursuer wants closeness and resources.
        if evader:
            return d2 + 5.0 * best_res
        return -d2 + 5.0 * best_res

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = None
    for dx, dy in moves:
        x, y = sx + dx, sy + dy
        if inb(x, y) and not blocked(x, y):
            v = score_for(x, y)
            if best is None or v > bestv:
                best, bestv = (dx, dy), v

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]