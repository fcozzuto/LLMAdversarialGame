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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    self_role = (observation.get("self_role") or "").lower()
    evader = ("evader" in self_role) or ("escape" in self_role) or ("runner" in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        mob = 0
        for ddx, ddy in dirs:
            x2, y2 = nx + ddx, ny + ddy
            if ok(x2, y2):
                mob += 1
        val = d2 if evader else -d2
        val2 = val * 1000 + mob
        if best is None or val2 > best_val:
            best = (dx, dy)
            best_val = val2

    return list(best) if best is not None else [0, 0]