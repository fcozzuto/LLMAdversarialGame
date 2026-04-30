def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))

    if not cand:
        return [0, 0]

    # Deterministic tie-breaking: same score -> lexicographically smallest (dx, dy)
    cand.sort(key=lambda t: (t[0], t[1]))

    if resources:
        best = (-10**18, 0, 0)
        for dx, dy, nx, ny in cand:
            score = -10**18
            for rx, ry in resources:
                score = max(score, dist2(ox, oy, rx, ry) - dist2(nx, ny, rx, ry))
            if score > best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]
    else:
        bestd = 10**18
        best = (0, 0)
        for dx, dy, nx, ny in cand:
            d = dist2(nx, ny, ox, oy)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]