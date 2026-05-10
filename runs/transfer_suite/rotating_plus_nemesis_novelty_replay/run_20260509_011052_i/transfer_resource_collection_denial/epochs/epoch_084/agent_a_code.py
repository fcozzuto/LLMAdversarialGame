def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources we can reach no later than opponent; otherwise deny by minimizing our lateness.
    # Tie-break deterministically by closer-to-self, then closer-to-opponent, then lexicographic.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        contested = 1 if sd <= od else 0
        # Light obstacle pressure: penalize targets adjacent to obstacles.
        adj = 0
        for nx, ny in ((rx+1, ry), (rx-1, ry), (rx, ry+1), (rx, ry-1)):
            if (nx, ny) in obstacles:
                adj += 1
        # Score key: maximize value
        val = (od - sd) * 3 + contested * 10 - adj
        key = (val, -sd, -od, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal step lands on obstacle (rare), fall back to axis step that avoids obstacle.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        cand = []
        if (sx + dx, sy) not in obstacles:
            cand.append((dx, 0))
        if (sx, sy + dy) not in obstacles:
            cand.append((0, dy))
        if cand:
            # Choose deterministic: whichever reduces chebyshev distance more; tie by axis priority.
            best_move = None
            best_k = None
            for mx, my in cand:
                nk = (-(cheb(sx + mx, sy + my, tx, ty)), -abs(my), -abs(mx))
                if best_k is None or nk > best_k:
                    best_k = nk
                    best_move = (mx, my)
            dx, dy = best_move
        else:
            dx, dy = 0, 0

    return [int(dx), int(dy)]