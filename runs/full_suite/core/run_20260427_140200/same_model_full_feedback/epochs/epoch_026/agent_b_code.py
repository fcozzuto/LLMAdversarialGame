def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        # New policy: prioritize resource distance, but also discourage moving into opponent's proximity.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dres = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < dres:
                    dres = d
            dop = cheb(nx, ny, ox, oy)
            # Deterministic tie-break: prefer smaller dx, then smaller dy.
            val = dres * 1000 + (7 - dop) * 3 + (dx + 1) * 2 + (dy + 1)
            cand = (val, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    # No resources: deterministically move toward center while maximizing distance from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dc = cheb(nx, ny, cx, cy)
        dop = cheb(nx, ny, ox, oy)
        val = dc * 10 - dop + (dx + 1) * 2 + (dy + 1)
        cand = (val, dx, dy)
        if best is None or cand < best:
            best = cand
    return [best[1], best[2]]