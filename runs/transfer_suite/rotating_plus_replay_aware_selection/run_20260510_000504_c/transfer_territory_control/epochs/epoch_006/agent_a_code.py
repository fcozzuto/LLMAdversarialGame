def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def near_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in opp_terr:
                        return True
        return False
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if unclaimed:
        cand = [p for p in unclaimed if not near_opp(p[0], p[1])]
        pool = cand if cand else list(unclaimed)
        pool.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))
        tx, ty = pool[0]
    else:
        tx, ty = cx, cy
    candidates = []
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        opp_pen = -1 if near_opp(nx, ny) else 0
        to_opp = abs(nx - ox) + abs(ny - oy)
        score = -dist + opp_pen - 0.001 * to_opp
        candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[2], t[1]))
    return [candidates[0][1], candidates[0][2]]