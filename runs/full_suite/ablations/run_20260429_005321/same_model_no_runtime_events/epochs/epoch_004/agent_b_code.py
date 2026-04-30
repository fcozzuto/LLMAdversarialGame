def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_cell = None
    best_margin = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        margin = do - ds
        if margin > best_margin or (margin == best_margin and (ds < dist(sx, sy, rx, ry))):
            best_margin = margin
            best_cell = (rx, ry)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if best_cell is None:
        # Fallback: keep useful tempo by moving toward center while drifting away from opponent
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = (-dist(nx, ny, cx, cy)) + 0.2 * (dist(nx, ny, ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    rx, ry = best_cell

    best = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        ds = dist(nx, ny, rx, ry)
        do = dist(ox, oy, rx, ry)

        # Prefer being strictly closer than opponent to the main target.
        margin = do - ds
        score = 1000 * margin - 5 * ds

        # If we can be taken next turn at our current/target vicinity, heavily penalize.
        # (captures are essentially reaching within 1 step)
        if do <= 1 and ds > 0:
            score -= 800

        # If opponent is closer than us, try to disrupt by increasing their distance to the target.
        if margin < 0:
            score += 20 * (dist(ox, oy, rx, ry) - dist(ox, oy, rx, ry))  # deterministic no-op
            # small bias away from opponent to prevent helping their path
            score -= dist(nx, ny, ox, oy)

        # Tie-break: keep moving toward center slightly (prevents stalling)
        score += -0.2 * dist(nx, ny, cx, cy)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]