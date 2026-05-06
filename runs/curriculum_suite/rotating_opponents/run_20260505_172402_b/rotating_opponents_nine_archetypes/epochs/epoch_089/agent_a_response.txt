def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    if not valid(sx, sy):
        for y in range(h):
            for x in range(w):
                if valid(x, y):
                    sx, sy = x, y
                    break
            if valid(sx, sy):
                break

    if not resources:
        # Deterministic fallback: move away from opponent if possible else stay
        dx = 0 if ox == sx else (-1 if ox > sx else 1)
        dy = 0 if oy == sy else (-1 if oy > sy else 1)
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        for step in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = sx + step[0], sy + step[1]
            if valid(nx, ny):
                return [step[0], step[1]]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources we can reach sooner than the opponent (and nearer to us).
    best = None
    best_key = None
    for rx, ry in resources:
        d_us = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Minimize: primary advantage for us; tie-breaker: closer to us; deterministic by coords.
        key = (d_us - d_op, d_us, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # If direct diagonal step is blocked, fall back to best valid one-step move.
    cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    # Add alternatives for robustness (still deterministic)
    cand += [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    seen = set()
    for m in cand:
        if m in seen:
            continue
        seen.add(m)
        mx, my = m[0], m[1]
        nx, ny = sx + mx, sy + my
        if valid(nx, ny):
            return [mx, my]

    return [0, 0]