def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Deterministic escape-to-center while maximizing distance from opponent
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            oppd = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            centd = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            key = (-oppd, centd, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target selection: deny if opponent is closer (or tie), otherwise grab what you're ahead on.
    best_target = None
    for rx, ry in resources:
        my_d = manh(sx, sy, rx, ry)
        opp_d = manh(ox, oy, rx, ry)
        if my_d <= opp_d + 1:
            # try to be first among "close/tied" resources
            key = (0, my_d, opp_d, rx, ry)
        else:
            # only if truly ahead, prefer the biggest gap
            key = (1, -(my_d - opp_d), my_d, opp_d, rx, ry)
        if best_target is None or key < best_target[0]:
            best_target = (key, (rx, ry))
    tx, ty = best_target[1]

    # Move selection: step that reduces distance to target; among ties, maximize distance from opponent.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dtar = manh(nx, ny, tx, ty)
        oppd = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Prefer approaching target; if multiple, choose the one that denies/creates space from opponent.
        key = (dtar, -oppd, abs(dx) + abs(dy), dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]] if best else [0, 0]