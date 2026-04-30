def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or [])]

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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = (0, 0, -10**18)
    for dx, dy, nx, ny in legal:
        if resources:
            best_res = -10**18
            myd = cheb(nx, ny, ox, oy)  # discourages letting opponent close too fast (small effect)
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ourd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                v = (opd - ourd) * 1000 - ourd * 3 - myd
                # tiny deterministic tie-break toward center
                v -= cheb(nx, ny, cx, cy) * 0.1
                if v > best_res:
                    best_res = v
            val = best_res
        else:
            val = -cheb(nx, ny, cx, cy)
        if val > best[2]:
            best = (dx, dy, val)

    return [best[0], best[1]]