def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    if resources:
        opp_dist = man(ox, oy, ox, oy)
        best = None
        best_score = -10**18
        for dx, dy, nx, ny in candidates:
            d = min(man(nx, ny, rx, ry) for rx, ry in resources)
            d2 = min(man(ox, oy, rx, ry) for rx, ry in resources)
            score = (d2 - d) * 100 - d
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best = min(candidates, key=lambda t: (man(t[2], t[3], ox, oy), t[0], t[1]))
    return [int(best[0]), int(best[1])]