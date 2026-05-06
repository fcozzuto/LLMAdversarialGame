def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

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
            d = max(abs(nx - tx), abs(ny - ty))
            if best is None or d < best[0] or (d == best[0] and (nx + ny) < best[1]):
                best = (d, nx + ny, dx, dy)
        return [best[2], best[3]] if best else [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    parity = observation.get("turn_index", 0) & 1
    best_t = None
    for rx, ry in resources:
        sd = dist_cheb(sx, sy, rx, ry)
        od = dist_cheb(ox, oy, rx, ry)
        # If opponent is closer, prioritize denying it; else secure closest.
        adv = od - sd  # positive => we are closer
        if parity == 0:
            key = (-adv, sd, rx, ry)  # maximize adv first
        else:
            key = (sd - od, sd, rx, ry)  # prioritize worst-case contested
        if best_t is None or key < best_t[0]:
            best_t = (key, (rx, ry), sd, od)
    tx, ty = best_t[1]

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = dist_cheb(nx, ny, tx, ty)
        # Small tie-breaker: also discourage drifting toward the opponent when parity matches.
        drift = abs(nx - ox) + abs(ny - oy)
        key = (d, drift if parity == 0 else -drift, nx + 7 * ny, dx * 2 + dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]