def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(px, py):
        return 0 <= px < w and 0 <= py < h and (px, py) not in obstacles

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inside(nx, ny):
                continue
            v = -dist2(nx, ny, cx, cy) + 0.15 * dist2(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) > best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # choose a few best targets by our distance, deterministic ordering
    scored_targets = []
    for rx, ry in resources:
        dv = dist2(x, y, rx, ry)
        scored_targets.append((dv, rx, ry))
    scored_targets.sort()
    candidates = scored_targets[:min(5, len(scored_targets))]

    best_move = (0, 0)
    best_val = -10**18
    # prioritize grabbing/controlling races: our closeness, opponent distance, and blocking risk
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        val = 0
        # obstacle proximity penalty (soft)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1
        val -= 0.05 * adj_obs

        for dv, rx, ry in candidates:
            our = dist2(nx, ny, rx, ry)
            opp = dist2(ox, oy, rx, ry)
            # encourage moves that reduce our distance and increase opponent distance
            val += -our + 0.55 * opp
            # stronger reward if we step onto a resource
            if (nx, ny) == (rx, ry):
                val += 10000
            # small nudge to align diagonals toward target
            val += -0.01 * (abs(nx - rx) + abs(ny - ry))
        # also discourage getting too close to opponent unless it helps capture
        val += 0.02 * dist2(nx, ny, ox, oy)

        if val > best_val or (val == best_val and (dx, dy) > best_move):
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]