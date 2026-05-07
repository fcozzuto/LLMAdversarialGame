def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda p: (dist2(sx, sy, p[0], p[1]),
                                             -dist2(ox, oy, p[0], p[1]), p[0], p[1]))
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (dist2(nx, ny, tx, ty), dist2(nx, ny, ox, oy), nx, ny)
            if best is None or key < best:
                best = key
                best_move = [dx, dy]
        return best_move if best is not None else [0, 0]

    # Choose a resource where we are likely to beat/deny opponent: maximize (opp_d2 - self_d2).
    # If tie, prefer closer to us (smaller self_d2), then farther from opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        key = (-(od - sd), sd, -od, rx, ry)  # minimize negative advantage => maximize (od-sd)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res

    # Move evaluation: primarily get closer to target while keeping opponent farther from it.
    # Secondary: stay away from obstacles by not stepping into them (already filtered).
    best = None
    best_move = [0, 0]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = dist2(nx, ny, rx, ry)
        opp_d = dist2(ox, oy, rx, ry)
        # Small deterministic "intercept" nudge: if opponent is extremely close to target, drift toward blocking line.
        # Use projection-like heuristic via comparing neighbor distances to a point between opponent and target.
        mx, my = (ox + rx) // 2, (oy + ry) // 2
        intercept = dist2(nx, ny, mx, my)
        key = (self_d, -opp_d, intercept, abs(nx - rx) + abs(ny - ry), nx, ny)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return best_move