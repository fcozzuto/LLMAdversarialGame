def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in occ:
                continue
            score = -dist(nx, ny, cx, cy)  # go center
            score -= 0.15 * dist(nx, ny, ox, oy)  # keep some distance
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    # Pick best resource by maximizing our distance advantage (self closer than opponent).
    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        adv = od - sd  # positive => we are closer
        # Tie-break toward closer actual distance and deterministic position.
        key = (-adv, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Move to improve our next-step advantage toward the chosen target, while blocking opponent if possible.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in occ:
            continue
        nsd = dist(nx, ny, tx, ty)
        nod = dist(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Primary: our advantage gap at next step.
        score = (nod - nsd) * 100
        # Secondary: prefer reducing distance to target.
        score -= 2.0 * nsd
        # Tertiary: avoid stepping into immediate confrontation if it helps opponent reach sooner.
        opp_min = min(dist(nx, ny, rx, ry) for rx, ry in resources) if resources else 0
        score -= 0.2 * opp_min
        # Small penalty for moving away from center to break ties safely.
        score -= 0.01 * dist(nx, ny, cx, cy)

        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    return [best[1][0], best[1][1]] if best else [0, 0]