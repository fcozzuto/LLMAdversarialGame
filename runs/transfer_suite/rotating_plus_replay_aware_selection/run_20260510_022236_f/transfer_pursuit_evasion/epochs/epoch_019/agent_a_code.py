def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("evad" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    def center_bonus(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        d = abs(x - cx) + abs(y - cy)
        return -d

    best = None
    best_val = None
    best_tiebreak = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)
        cb = center_bonus(nx, ny)
        if pursuer:
            val = -d
            tiebreak = (fn, cb)
        else:
            val = d
            tiebreak = (fn, cb)
        if best is None or val > best_val or (val == best_val and tiebreak > best_tiebreak):
            best = (dx, dy)
            best_val = val
            best_tiebreak = tiebreak

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]