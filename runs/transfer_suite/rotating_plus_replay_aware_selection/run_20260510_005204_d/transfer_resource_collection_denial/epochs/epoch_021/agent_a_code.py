def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a target where we are at least as fast as the opponent; tie-break by closer and then stable preference.
    best_target = resources[0]
    best_key = None
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        center_bias = -(abs(rx - cx) + abs(ry - cy))
        key = (adv, -myd, center_bias, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    myd_now = cheb(sx, sy, tx, ty)
    in_range_moves = []

    res_set = set(tuple(p) for p in resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Immediate reward for collecting.
        collect = 1.5 if (nx, ny) in res_set else 0.0
        myd1 = cheb(nx, ny, tx, ty)
        opd1 = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance; also prefer moves that keep/extend advantage.
        score = collect + (opd1 - myd1) * 1.0 + (myd_now - myd1) * 0.25
        # Additional deterrent for stepping farther from target.
        if myd1 > myd_now:
            score -= 0.15 * (myd1 - myd_now)
        in_range_moves.append(((score, -myd1, -(nx + ny)), dx, dy))

    in_range_moves.sort(reverse=True, key=lambda t: t[0][0])
    if not in_range_moves:
        return [0, 0]
    return [in_range_moves[0][1], in_range_moves[0][2]]