def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            return sx, sy
        return nx, ny

    if not resources:
        # Drift toward center but keep away from obstacles and opponent.
        cx, cy = w // 2, h // 2
        best = (0, 0)
        best_score = -10**9
        for dx, dy in deltas:
            nx, ny = clamp_move(dx, dy)
            if (nx, ny) == (sx, sy) and (sx + dx, sy + dy) != (sx, sy):
                continue
            d_center = cheb(nx, ny, cx, cy)
            d_opp = cheb(nx, ny, ox, oy)
            score = -d_center + 0.12 * d_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target resource that we are currently closest to relative to opponent.
    best_target = resources[0]
    best_adv = -10**9
    for rx, ry in resources:
        da = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = (do - da)  # positive means we're closer
        # Mildly prefer more central resources (opponent center_rush)
        cent = -cheb(rx, ry, w // 2, h // 2) * 0.04
        val = adv + cent
        if val > best_adv:
            best_adv = val
            best_target = (rx, ry)

    tx, ty = best_target

    # One-step lookahead: maximize advantage to target and general resource access, penalize proximity to opponent.
    alpha = 1.05
    beta = 0.35
    gamma = 0.12

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = clamp_move(dx, dy)
        da2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)  # opponent doesn't move this turn in our evaluation
        adv2 = do2 - da2

        # Resource accessibility: consider nearest resource distance (cheap).
        nearest = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < nearest:
                nearest = d

        d_opp = cheb(nx, ny, ox, oy)
        score = alpha * adv2 - beta * nearest + gamma * d_opp
        # Avoid getting stuck next to obstacles when possible: small penalty if current action doesn't move.
        if (nx, ny) == (sx, sy) and (sx + dx, sy + dy) != (sx, sy):
            score -= 0.5

        # Deterministic tie-break: prefer moves with smaller distance to target, then lexicographic.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cur_best_da = cheb(sx + best_move[0], sy + best_move[1], tx, ty)
            if da2 < cur_best_da:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]