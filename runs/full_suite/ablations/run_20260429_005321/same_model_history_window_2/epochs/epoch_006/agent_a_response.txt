def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If no resources, go toward center
    cx, cy = w // 2, h // 2
    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -md(nx, ny, cx, cy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    best = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        score = 0.0
        # Evaluate contest pressure over all remaining resources
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)

            if myd < opd:
                # Prefer winning soon and more decisively
                race = (opd - myd)
                score += race * 12.0 - myd * 0.25
            elif opd < myd:
                # Penalize allowing opponent to win; weight by how hard to catch up
                race = (myd - opd)
                score -= race * 10.0 - opd * 0.15
            else:
                # Tie: slightly prefer the nearer one (likely controlled by move timing)
                score += -myd * 0.05

        # Small bias toward not drifting too far (reduces oscillation)
        score += -md(nx, ny, cx, cy) * 0.01

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]