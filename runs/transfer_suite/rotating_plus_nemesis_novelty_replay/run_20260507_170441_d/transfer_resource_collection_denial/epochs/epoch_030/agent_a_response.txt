def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def risk(x0, y0, x1, y1):
        # Penalize resources whose approach likely passes adjacent to obstacles.
        # Uses small deterministic stencil around the direction step.
        dx = 0 if x1 == x0 else (1 if x1 > x0 else -1)
        dy = 0 if y1 == y0 else (1 if y1 > y0 else -1)
        ax, ay = x0 + dx, y0 + dy
        r = 0
        for ox2, oy2 in obst:
            if abs(ox2 - ax) <= 1 and abs(oy2 - ay) <= 1:
                r += 3
            if abs(ox2 - x0) <= 1 and abs(oy2 - y0) <= 1:
                r += 1
        return r

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        best_res = None
        for rx, ry in resources:
            self_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)

            # Primary: capture sooner than opponent (smaller self_t - opp_t is better).
            # Secondary: minimize self time.
            # Tertiary: reduce approach risk and prefer nearer resources to us only when close.
            rel = self_t - opp_t
            val = (rel, self_t, risk(nx, ny, rx, ry), -opp_t)
            if best_res is None or val < best_res:
                best_res = val
        if best_res is not None and (best is None or best_res < best):
            best = best_res
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]