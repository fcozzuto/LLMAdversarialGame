def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = [(dx, dy) for dx in dxs for dy in dys if not (dx == 0 and dy == 0)] + [(0, 0)]

    if not resources:
        best = (0, 0)
        bestd = md(sx, sy, w // 2, h // 2)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                d = md(nx, ny, w // 2, h // 2)
                if d < bestd or (d == bestd and (dx, dy) < best):
                    bestd = d
                    best = (dx, dy)
        return [best[0], best[1]]

    best_t = None
    best_score = None
    best_sd = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        score = od - sd
        if best_score is None or score > best_score or (score == best_score and (sd < best_sd or (sd == best_sd and (rx, ry) < best_t))):
            best_score = score
            best_sd = sd
            best_t = (rx, ry)

    tx, ty = best_t
    best = (0, 0)
    bestd = md(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            d = md(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
    return [best[0], best[1]]