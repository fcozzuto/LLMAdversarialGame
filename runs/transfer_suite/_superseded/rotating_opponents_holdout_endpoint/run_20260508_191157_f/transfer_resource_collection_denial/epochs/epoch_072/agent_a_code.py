def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources, drift to a strategic point (center-ish)
    if not resources:
        tx, ty = (gw // 2), (gh // 2)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Pick a resource to race/deny: favor small (self_dist - 0.9*opp_dist)
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = ds - 0.9 * do  # lower is better: grab early and/or beat opponent
        if best is None or score < best[0] or (score == best[0] and (ds, rx, ry) < (best[1], best[2], best[3])):
            best = (score, ds, rx, ry)
    _, _, tx, ty = best

    # Greedy one-step with obstacle penalty and slight denial bias
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (tx, ty))
        oppd = dist((ox, oy), (tx, ty))
        # Prefer reducing distance to target and, when possible, not letting opponent get closer (denial)
        val = myd - 0.35 * (oppd - dist((sx, sy), (tx, ty))) + (0.15 * dist((nx, ny), (ox, oy)))
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move is not None else [0, 0]