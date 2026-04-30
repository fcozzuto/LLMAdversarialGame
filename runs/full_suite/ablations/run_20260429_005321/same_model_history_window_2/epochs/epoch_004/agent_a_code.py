def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    rem = observation.get("remaining_resource_count", len(resources))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def step_score(x, y, tx, ty):
        myd = md(x, y, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Prefer resources we can get first; lightly prefer central-ish targets.
        cx, cy = w // 2, h // 2
        center_bias = -0.02 * md(x, y, cx, cy)
        return (opd - myd) + center_bias

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cx, cy = w // 2, h // 2
    if not resources:
        best = [0, 0]
        best_sc = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -md(nx, ny, cx, cy) - 0.01 * md(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc, best = sc, [dx, dy]
        return best

    best = [0, 0]
    best_sc = -10**18
    prefer_center_when_low = rem <= 6

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Determine best resource to pursue from this move.
        local_best = -10**18
        for rx, ry in resources:
            v = step_score(nx, ny, rx, ry)
            if (nx, ny) == (rx, ry):
                v += 1000  # immediate pickup
            local_best = v if v > local_best else local_best

        # If we're not competing well, still drift to center to keep options open.
        center_term = -0.03 * md(nx, ny, cx, cy) if prefer_center_when_low else -0.01 * md(nx, ny, cx, cy)

        # Avoid moving closer to opponent when it would also worsen our best contest.
        opp_close = -0.02 * md(nx, ny, ox, oy)

        sc = local_best + center_term + opp_close
        if sc > best_sc:
            best_sc, best = sc, [dx, dy]

    return best