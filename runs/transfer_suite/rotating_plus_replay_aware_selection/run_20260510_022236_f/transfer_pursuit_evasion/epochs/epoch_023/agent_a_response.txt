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
    is_pursuer = ("purs" in role) or ("evad" not in role)
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

    def corner_targets():
        return [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def edge_pen(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    best_m = (0, 0)
    best_s = -10**18 if is_pursuer else 10**18
    d0 = dist2(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d1 = dist2(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)
        ep = edge_pen(nx, ny)

        if is_pursuer:
            # Prefer closing distance, avoid dead-ends, and slightly prefer central squares.
            score = (d0 - d1) * 10 + fn * 2 + ep * 0.1
            # If distance isn't improving, add a small bias toward increasing movement options.
            score += (1 if d1 < d0 else 0) * 3
            if score > best_s:
                best_s, best_m = score, [dx, dy]
        else:
            # Evader: prefer increasing distance, avoid corners that reduce mobility, and keep distance from pursuer.
            score = (d1 - d0) * 10 + fn * 2 - ep * 0.1
            # If can't improve much, still try to maximize escape mobility.
            score += (1 if d1 > d0 else 0) * 3
            if score > best_s:
                best_s, best_m = score, [dx, dy]

    # If multiple equalities happen, tie-break deterministically by move order using stored best.
    return best_m