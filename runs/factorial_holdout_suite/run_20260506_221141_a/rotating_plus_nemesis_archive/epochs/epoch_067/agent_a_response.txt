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
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    # Score: prioritize resources we can reach sooner than opponent; then prioritize absolute speed.
    best = None
    best_val = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive if we're faster
        val = lead * 1000 - sd  # strong contest pressure, then faster arrival
        # Small deterministic tie-break to reduce jitter: prefer lower x then y
        val -= rx * 0.001 + ry * 0.000001
        if val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # If target cell is an obstacle (shouldn't happen), fall back to safe direction by trying stay/axes.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        candidates = [(0, 0), (dx, 0), (0, dy), (dx, dy)]
        for cdx, cdy in candidates:
            tx, ty = sx + cdx, sy + cdy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                return [int(cdx), int(cdy)]
        return [0, 0]

    return [int(dx), int(dy)]