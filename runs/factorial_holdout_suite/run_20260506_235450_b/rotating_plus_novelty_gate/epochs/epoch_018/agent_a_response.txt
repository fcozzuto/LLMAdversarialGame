def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If we can catch a resource first, prioritize it; otherwise, move to reduce the gap (intercept).
    # One-step lookahead: pick the move that maximizes our best "advantage score" next turn.
    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        cur_best = None
        for rx, ry in resources:
            myd2 = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd2  # positive => we are closer (good)
            # Strongly prefer not-behind resources; then prefer larger advantage, then closer.
            primary = 1 if myd2 <= opd else 0
            val = (primary, adv, -myd2, -(rx * 10 + ry))
            if cur_best is None or val > cur_best:
                cur_best = val

        # Prefer staying if equally good; deterministic via value then move ordering.
        if best_val is None or cur_best > best_val:
            best_val = cur_best
            best_move = [dx, dy]

    return best_move