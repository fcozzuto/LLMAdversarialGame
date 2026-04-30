def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -dist(nx, ny, int(cx), int(cy)) + 0.2 * dist(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best is not None else [0, 0]

    best_move = None
    best_val = -10**18
    # deterministic tie-breaker by move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cur = 0
        best_t = -10**18
        for rx, ry in resources:
            ds = dist(nx, ny, sx, sy) + 0  # small deterministic bias
            dself = dist(nx, ny, rx, ry)
            dop = dist(ox, oy, rx, ry)
            # prefer resources closer than opponent; penalize being behind
            val = (1000 - 10 * dself) + (2 * dop) - (120 if dop < dself else 0) - ds
            if val > best_t:
                best_t = val
        # also avoid moving next to opponent too aggressively
        cur = best_t + 0.1 * dist(nx, ny, ox, oy)
        if cur > best_val:
            best_val = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])] if best_move is not None else [0, 0]