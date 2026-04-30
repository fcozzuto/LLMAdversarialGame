def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                v = -cheb(nx, ny, tx, ty)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    best_r = None
    best_score = -10**18
    for p in resources:
        if not p or len(p) < 2:
            continue
        rx, ry = int(p[0]), int(p[1])
        if (rx, ry) in obs:
            continue
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        score = (d_op - d_me) * 3 - d_me  # race-aware
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best_r = (tx, ty)

    tx, ty = best_r
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            v = -10**12
        else:
            d_new = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            v = -d_new + (d_op - d_new) * 0.7
            if dx == 0 and dy == 0:
                v -= 0.1
        if v > bestv:
            bestv = v
            best_move = [dx, dy]
    return best_move