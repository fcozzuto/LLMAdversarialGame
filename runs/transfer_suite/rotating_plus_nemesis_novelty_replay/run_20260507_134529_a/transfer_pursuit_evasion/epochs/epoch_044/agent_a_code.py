def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_cell(x, y):
        d2 = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        # mobility: fewer options near obstacles (for pursuer) is bad; for evader is good
        mob = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                mob += 1
        # Also bias toward center slightly to avoid getting trapped
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = ((x - cx) * (x - cx) + (y - cy) * (y - cy)) * 0.01
        if self_is_evader:
            return d2 + mob * 0.2 - center_pen
        else:
            return -d2 + mob * 0.05 - center_pen

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = score_cell(nx, ny)
        key = (v, -abs(nx - ox) - abs(ny - oy))
        if best is None or (key[0] > bestv[0]) or (key[0] == bestv[0] and key[1] > bestv[1]):
            best = (dx, dy)
            bestv = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]