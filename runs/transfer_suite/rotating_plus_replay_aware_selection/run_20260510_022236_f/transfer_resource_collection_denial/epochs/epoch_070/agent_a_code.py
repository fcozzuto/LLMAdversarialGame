def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    tr = int(observation.get("turns_remaining", 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = cheb_dist(sx, sy, rx, ry)
        do = cheb_dist(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer than opponent
        # Prefer clear wins; if not available, race for nearest.
        win_bias = 0
        if adv > 0:
            win_bias = 1000 + 50 * adv
        # Time pressure: if we can arrive within remaining turns, reduce penalty.
        time_pen = ds
        if tr > 0 and ds <= tr:
            time_pen = max(0, ds - 1)
        # Slight tie-break toward cells with larger coordinate sum variance to stay deterministic.
        tie = ((rx + ry) % 3) - 1
        sc = win_bias + (10 * adv) - (2 * time_pen) + tie
        if best_score is None or sc > best_score:
            best_score = sc
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]