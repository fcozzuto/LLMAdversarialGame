def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def best_target():
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            advantage = od - sd  # positive = we are closer
            # If we can win a pickup race, go for it; otherwise contest by minimizing who arrives first.
            primary = 1 if advantage > 0 else 0
            key = (primary, advantage, -(sd + 0.25 * od), -sd, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1]

    tx, ty = best_target()

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dnew = cheb(nx, ny, tx, ty)
            # Prefer moves that reduce our distance; tie-break deterministically toward x/y positives.
            key = (-dnew, dx, dy, nx, ny)
            if best_step is None or key > best_step[0]:
                best_step = (key, (dx, dy))
    return list(best_step[1]) if best_step else [0, 0]