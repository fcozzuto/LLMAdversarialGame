def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    (sx, sy) = observation.get("self_position", (0, 0))
    (ox, oy) = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

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

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (nx + ny) < best[2]):
                best = (d, (dx, dy), nx + ny)
        return [best[1][0], best[1][1]] if best else [0, 0]

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        stepd = []
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can beat (small ds - do), otherwise just minimize ds
            key = (ds - do, ds, rx, ry)
            stepd.append((key, rx, ry))
        key, _, _ = min(stepd, key=lambda t: t[0])
        score = key[0] * 1000 + key[1]  # deterministic combined preference
        if best is None or score < best[0] or (score == best[0] and (nx + ny) < best[2]):
            best = (score, (dx, dy), nx + ny)

    return [best[1][0], best[1][1]] if best else [0, 0]