def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx = (w - 1) if (ox + oy) > (sx + sy) else (w // 2)
        ty = h // 2
        if valid(tx, ty) is False:
            tx, ty = (w - 1) // 2, (h - 1) // 2
        if ox < sx: tx = min(w - 1, sx + 1)
        if ox > sx: tx = max(0, sx - 1)
        if oy < sy: ty = min(h - 1, sy + 1)
        if oy > sy: ty = max(0, sy - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        my_best = 10**9
        rel_best = -10**9
        rel_sum = 0
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if dm < my_best: my_best = dm
            rel = do - dm
            if rel > rel_best: rel_best = rel
            rel_sum += rel
        # Prioritize winning a resource race; use my_best to break ties.
        score = rel_best * 20 - my_best + rel_sum * 0.1
        # Small deterministic nudge: slightly prefer moves that keep closer to center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= (abs(nx - cx) + abs(ny - cy)) * 0.01
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move