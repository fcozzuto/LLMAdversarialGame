def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def step_options(x, y):
        opts = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    opts.append((dx, dy, nx, ny))
        if not opts:
            return [(0, 0, x, y)]
        return opts

    # If no resources, head toward the opposite corner from the opponent to reduce interference.
    if not resources:
        tx = 0 if ox > (w - 1) / 2 else (w - 1)
        ty = 0 if oy > (h - 1) / 2 else (h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Pick a resource that is "safer": opponent farther than us, but also prefer closeness.
    # Utility: (opp_d - self_d) + small tie-break on smaller self_d and center bias.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_u = -10**18
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        center_bias = -0.05 * (abs(rx - cx) + abs(ry - cy))
        # Mild obstacle proximity penalty around our position to avoid tight traps.
        neigh_pen = 0
        for dx2 in (-1, 0, 1):
            for dy2 in (-1, 0, 1):
                nx, ny = sx + dx2, sy + dy2
                if (nx, ny) in obstacles:
                    neigh_pen += 1
        u = (od - sd) + (-0.02 * sd) + center_bias - 0.01 * neigh_pen
        if u > best_u:
            best_u = u
            best = (rx, ry)

    tx, ty = best
    # Greedy step toward target with deterministic obstacle-aware choice.
    candidates = step_options(sx, sy)
    # Prefer diagonal/orthogonal moves that reduce distance to target.
    best_m = (0, 0, sx, sy)
    best_d = 10**9
    best_score = -10**18
    for dx, dy, nx, ny in candidates:
        nd = dist(nx, ny, tx, ty)
        score = -nd * 10 + (abs(dx) + abs(dy) == 2) * 0.1  # slight preference for diagonals
        if nd < best_d or (nd == best_d and score > best_score):
            best_d = nd
            best_score = score
            best_m = (dx, dy, nx, ny)

    return [int(best_m[0]), int(best_m[1])]