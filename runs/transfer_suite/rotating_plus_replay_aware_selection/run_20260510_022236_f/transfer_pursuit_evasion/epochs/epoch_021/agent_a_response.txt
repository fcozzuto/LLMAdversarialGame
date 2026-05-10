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

    def edge_pen(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    best = None
    best_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)
        ep = edge_pen(nx, ny)
        # Score: pursuer minimizes distance, evader maximizes distance.
        if pursuer:
            score = (-d) + 0.2 * fn + 0.03 * ep
        else:
            score = (d) + 0.2 * fn + 0.03 * ep
        if best is None or (score > best):
            best = score
            best_moves = [[dx, dy]]
        elif score == best:
            best_moves.append([dx, dy])

    # Deterministic tie-break: prefer moves that are not (0,0), then smallest dx, then smallest dy.
    cand = best_moves
    if len(cand) == 1:
        return cand[0]
    cand.sort(key=lambda m: (1 if (m[0] == 0 and m[1] == 0) else 0, m[0], m[1]))
    return cand[0]