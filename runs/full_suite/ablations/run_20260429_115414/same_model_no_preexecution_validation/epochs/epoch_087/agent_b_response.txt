def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose deterministic target: closest Chebyshev distance, then smallest (x,y)
    best = None
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        key = (d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    target = best[1]
    tx, ty = target

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            # Greedy toward target, with tie-break to avoid opponent if close
            d_to_t = cheb(nx, ny, tx, ty)
            d_to_o = cheb(nx, ny, int(op[0]), int(op[1]))
            cand.append((d_to_t, -d_to_o, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    return [cand[0][2], cand[0][3]]