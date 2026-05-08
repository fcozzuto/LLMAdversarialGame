def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role_s = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role_s for k in ("evad", "run", "away", "escape", "runner"))
    is_pursuer = ("purs" in role_s) or ("hunt" in role_s) or ("chase" in role_s)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x, y):
        ax = abs(ox - x)
        ay = abs(oy - y)
        return ax if ax > ay else ay

    def min_obs_dist(x, y):
        if not blocked:
            return 99
        dmin = 99
        for bx, by in blocked:
            d = abs(bx - x) + abs(by - y)
            if d < dmin:
                dmin = d
        return dmin

    best_move = [0, 0]
    best_score = None
    # Deterministic tie-break: iterate moves in fixed order; update only on strict improvement
    for dx, dy in moves:
        x, y = sx + dx, sy + dy
        if x < 0 or x >= w or y < 0 or y >= h:
            continue
        if (x, y) in blocked:
            score = -10**9
        else:
            d = cheb(x, y)
            od = min_obs_dist(x, y)
            border = min(x, y, w - 1 - x, h - 1 - y)
            # Evader: maximize distance; also prefer being near obstacles' "far side" and keep some border.
            # Pursuer: minimize distance; also prefer not being trapped adjacent to obstacles.
            if is_evader and not is_pursuer:
                score = (10 * d) + (2.0 * od) + (0.15 * border)
            else:
                score = (-10 * d) + (1.5 * od) + (0.05 * border)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]