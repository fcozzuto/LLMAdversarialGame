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

    res = set()
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            res.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    evader = "evader" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        s = d2 if evader else -d2
        if (nx, ny) in res:
            s += 10**6
        if best is None or s > best_s:
            best = (dx, dy)
            best_s = s

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]