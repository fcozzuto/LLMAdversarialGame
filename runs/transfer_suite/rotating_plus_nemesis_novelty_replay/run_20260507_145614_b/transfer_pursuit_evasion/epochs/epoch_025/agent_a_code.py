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

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    dx_t = 0 if ox == sx else (1 if ox > sx else -1)
    dy_t = 0 if oy == sy else (1 if oy > sy else -1)
    def align(nx, ny):
        ax, ay = nx - sx, ny - sy
        return (ax == dx_t) + (ay == dy_t)

    best = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d_inf = max(abs(nx - ox), abs(ny - oy))

        mob = 0
        for ddx, ddy in dirs:
            x2, y2 = nx + ddx, ny + ddy
            if ok(x2, y2):
                mob += 1

        # Tie-breakers: alignment with direct vector + mobility
        if evader:
            val = (d2, d_inf, mob, align(nx, ny), -abs(nx - ox) - abs(ny - oy))
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            val = (-d2, -d_inf, mob, align(nx, ny), abs(nx - ox) + abs(ny - oy))
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]