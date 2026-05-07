def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    def best_target_for_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        best_t = None
        best_pair = None
        for t in res:
            da = dist(nx, ny, ox, oy)
            db = dist(sx, sy, ox, oy)
            # prefer targets closer to us but keep race advantage
            s_my = dist(nx, ny, t[0], t[1])
            s_op = dist(ox, oy, t[0], t[1])
            pair = (s_op - s_my, -s_my)  # maximize advantage, then minimize my dist
            if best_pair is None or pair > best_pair:
                best_pair = pair
                best_t = t
        return best_t

    best_move = None
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        t = best_target_for_move(dx, dy)
        if t is None:
            continue
        myd = dist(nx, ny, t[0], t[1])
        opd = dist(ox, oy, t[0], t[1])
        # local safety: if adjacent to obstacle cells, slightly penalize
        adj_obs = 0
        for ox2 in (-1, 0, 1):
            for oy2 in (-1, 0, 1):
                xx, yy = nx + ox2, ny + oy2
                if (xx, yy) in obs:
                    adj_obs += 1
        val = (opd - myd, -myd, -adj_obs)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]