def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tiebreak: fixed order with small preference for (0,0) only if truly best.
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # If no resources visible, chase opponent's direction while staying obstacle-safe.
    if not resources:
        best = None
        for dx, dy, nx, ny in candidates:
            score = -cheb(nx, ny, ox, oy)  # maximize closeness
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    oppd0 = cheb(ox, oy, ox, oy)
    mybest = None
    for dx, dy, nx, ny in candidates:
        my_to_opp = cheb(nx, ny, ox, oy)
        best_local = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer moves that make us reach a resource sooner than opponent.
            # Add slight tie-break for being closer overall and to reduce chasing opponent when contested.
            gain = (opd - myd)
            contest_pen = 0
            if gain < 0:
                contest_pen = 3 * (-gain)
            # Encourage taking resources that are relatively near overall.
            near_boost = 0.1 * (16 - myd)
            opp_push = -0.02 * my_to_opp
            val = gain * 10 - contest_pen + near_boost + opp_push
            if val > best_local:
                best_local = val
        # Small deterministic bias to prefer diagonal progress when scores tie.
        bias = 0
        if dx != 0 and dy != 0:
            bias = 0.01
        score = best_local + bias
        if mybest is None or score > mybest[0]:
            mybest = (score, dx, dy)

    return [int(mybest[1]), int(mybest[2])]