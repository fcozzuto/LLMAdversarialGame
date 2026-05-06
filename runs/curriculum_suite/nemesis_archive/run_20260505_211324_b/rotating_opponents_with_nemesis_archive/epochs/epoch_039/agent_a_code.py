def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Switch from previous "global cell scoring" to a local "one-step advantage" evaluation.
    # Emphasize resources that opponent is currently best positioned to take.
    opp_focus = min(res, key=lambda p: (md(ox, oy, p[0], p[1]), p[0], p[1]))
    fx, fy = opp_focus[0], opp_focus[1]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        myd_focus = md(nx, ny, fx, fy)
        opd_focus = md(ox, oy, fx, fy)
        self_to_opp = md(nx, ny, ox, oy)

        # Advantage on the contested focus resource plus small pressure on stealing other nearby resources.
        val = (opd_focus - myd_focus) * 10 - myd_focus
        # If we reduce distance to opponent, we increase capture likelihood for contested paths.
        val += -0.6 * (self_to_opp)

        # Consider a few nearest resources to keep strategy robust without full-grid search.
        # Deterministically pick top-3 by opponent distance.
        ranked = sorted(res, key=lambda p: (md(ox, oy, p[0], p[1]), md(nx, ny, p[0], p[1]), p[0], p[1]))[:3]
        for tx, ty in ranked:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)
            contest = (opd - myd) * 4 - myd
            if (tx, ty) == (fx, fy):
                contest += 12
            val += contest

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    # If all moves were invalid (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]