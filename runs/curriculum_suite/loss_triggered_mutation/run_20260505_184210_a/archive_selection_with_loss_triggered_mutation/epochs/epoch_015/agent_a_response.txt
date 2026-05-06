def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if w <= 0 or h <= 0:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dc = abs(nx - cx) + abs(ny - cy)
            if best is None or (dc, dx, dy) < best:
                best = (dc, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose move that maximizes "contest": reach some resource sooner than opponent.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        best_gap = -10**9
        best_our_time = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)
            gap = opp_t - our_t
            if gap > best_gap or (gap == best_gap and our_t < best_our_time):
                best_gap = gap
                best_our_time = our_t

        # Encourage finishing quickly; slight bias toward blocking via central approach.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        central = abs(nx - cx) + abs(ny - cy)
        key = (-best_gap, best_our_time, central, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]