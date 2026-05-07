def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def pos_value(px, py):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer winning targets (do - ds high), then closer for us, then deterministic tie-break.
            v = (do - ds, -ds, -cheb(px, py, ox, oy), ry, rx)
            if best is None or v > best:
                best = v
        if best is None:
            return (-10**9, 0, 0, 0, 0)
        return best

    best_move = (None, None)
    best_v = (-10**18, -10**18, -10**18, -10**18, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = pos_value(nx, ny)
        if v > best_v:
            best_v = v
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]