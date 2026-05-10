def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((int(x), int(y)) for x, y in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    # One-step lookahead: choose move maximizing expected advantage, with a small obstacle-penalty.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine keeps in place if invalid

        # Small penalty for proximity to obstacles (encourages threading corridors)
        obs_pen = 0
        for ax, ay in obstacles:
            ax, ay = int(ax), int(ay)
            dd = cheb(nx, ny, ax, ay)
            if dd == 0: obs_pen += 10
            elif dd == 1: obs_pen += 1

        # Evaluate best target resource for this hypothetical position
        # Prefer states where opponent is farther relative to us, then prefer absolute closeness.
        best_rel = None
        best_abs = None
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            rel = od - sd
            # tie-break: smaller our distance; then larger opponent distance
            if (best_rel is None or rel > best_rel or
                (rel == best_rel and (best_abs is None or sd < best_abs))):
                best_rel = rel
                best_abs = sd

        # Also slightly prefer moves that reduce our distance to the currently closest resource.
        cur_close = min(cheb(sx, sy, rx, ry) for rx, ry in res)
        new_close = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        progress = cur_close - new_close

        score = (best_rel * 1000) + (progress * 10) - (best_abs if best_abs is not None else 0) - obs_pen
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best