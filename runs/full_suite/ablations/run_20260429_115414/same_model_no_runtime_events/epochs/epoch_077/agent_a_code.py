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

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored = []
    if resources:
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            best = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < best: best = d
            score = -best - 0.01 * cheb(nx, ny, ox, oy)
            scored.append((score, dx, dy))
        scored.sort(key=lambda t: (-t[0], t[1], t[2]))
        if scored:
            return [scored[0][1], scored[0][2]]
    else:
        tx, ty = (0, 0) if (sx + sy) <= (ox + oy) else (w - 1, h - 1)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty) + 0.02 * cheb(nx, ny, ox, oy)
            scored.append((score, dx, dy))
        scored.sort(key=lambda t: (-t[0], t[1], t[2]))
        if scored:
            return [scored[0][1], scored[0][2]]

    return [0, 0]