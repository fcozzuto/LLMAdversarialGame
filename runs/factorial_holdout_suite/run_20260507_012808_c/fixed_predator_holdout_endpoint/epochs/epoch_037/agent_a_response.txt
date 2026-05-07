def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_value(x, y):
        if (x, y) in obstacles:
            return (-10**9, 10**9)
        self_d = dist((x, y), (sx, sy))
        opp_d = dist((x, y), (ox, oy))
        lead = opp_d - self_d
        return (lead, -self_d)

    # pick target deterministically: maximize lead, then minimize our distance
    best_t = resources[0]
    best_key = None
    for t in resources:
        d_s = dist(t, (sx, sy))
        d_o = dist(t, (ox, oy))
        key = (d_o - d_s, -d_s, -abs(t[0] - (w - 1)) - abs(t[1] - (h - 1)))
        if best_key is None or key > best_key:
            best_key = key
            best_t = t
    tx, ty = best_t

    # propose step toward target, then fall back to best legal neighbor
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy
    if in_bounds(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]

    # evaluate all moves (deterministic ordering)
    candidates = []
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if ddx == 0 and ddy == 0:
                continue
            x, y = sx + ddx, sy + ddy
            if not in_bounds(x, y) or (x, y) in obstacles:
                continue
            candidates.append((cell_value(x, y), (ddx, ddy)))
    candidates.sort(key=lambda z: (z[0][0], z[0][1], z[1][0], z[1][1]), reverse=True)

    if candidates:
        return [candidates[0][1][0], candidates[0][1][1]]
    return [0, 0]