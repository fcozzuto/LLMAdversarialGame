def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    same_y = [r for r in resources if r[1] == oy]
    cand = same_y if same_y else resources

    best = None
    if cand:
        scored = []
        for rx, ry in cand:
            ds = manh(sx, sy, rx, ry)
            do = manh(ox, oy, rx, ry)
            scored.append((do - ds, -ds, rx, ry, ds, do))
        ahead = [t for t in scored if t[0] > 0]  # self strictly closer
        use = ahead if ahead else scored
        use.sort(reverse=True)  # (do-ds) then -ds then rx then ry
        best = use[0]
        tx, ty = best[3], best[4]
    else:
        tx, ty = resources[0][0], resources[0][1]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy
        ns = -manh(nx, ny, tx, ty)
        # anti-opponent pressure + slight center bias for robustness
        no = manh(ox, oy, tx, ty)
        add = (no - manh(nx, ny, tx, ty)) * 0.35
        cb = -(((nx - (w - 1) / 2) ** 2) + ((ny - (h - 1) / 2) ** 2)) * 0.001
        s = ns + add + cb
        if s > best_s or (s == best_s and (dx, dy) < best_m):
            best_s = s
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]